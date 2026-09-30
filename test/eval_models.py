"""
Evaluate local Ollama models on C programming, across four tasks:
  1. WRITE   - write a C program (compiled + run against test input)
  2. DEBUG   - fix a buggy C program (compiled + run, output must be correct)
  3. EXPLAIN - explain a C program and state its exact output
  4. QA      - answer conceptual C questions (keyword check)

Metrics: correctness (auto pass/fail), latency, tokens/sec,
         readability of prose answers (Flesch), gcc warnings on code.

Setup (PowerShell):
    pip install requests textstat
    gcc --version        # gcc must be on PATH (MSYS2/MinGW works)
    python eval_c_suite.py
"""
import csv
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections import defaultdict
from statistics import mean

import requests
import textstat

OLLAMA = "http://localhost:11434/api/generate"
MODELS = ["qwen2.5-coder:1.5b", "llama3.2:latest", "qwen2.5-coder:7b"]

GCC = shutil.which("gcc")
if not GCC:
    raise SystemExit("gcc not found on PATH. Install MinGW/MSYS2 first.")

CODE_ONLY = "Output only the complete program in a single ```c block, no explanation."

# ---------------------------------------------------------------- TASKS
# WRITE: (name, prompt, stdin, regex the stdout must match)
WRITE = [
    ("chatbot",
     "Write a complete single-file C program for a simple rule-based chatbot. "
     "Loop: read a line with fgets. If the input contains 'hello' (any case) reply "
     "with a greeting containing the word Hello. If it contains 'bye' print a reply "
     "containing the word Goodbye and exit. Otherwise print a short fallback. "
     + CODE_ONLY,
     "hello\nrandom words\nbye\n",
     r"(?s)hello.*goodbye"),
    ("reverse_string",
     "Write a C program that reads one line from stdin and prints it reversed. "
     + CODE_ONLY,
     "hello\n",
     r"olleh"),
    ("sum_numbers",
     "Write a C program that reads an integer N, then N integers, and prints their sum. "
     + CODE_ONLY,
     "3\n10 20 30\n",
     r"\b60\b"),
]

# DEBUG: (name, what it should do, buggy code, regex the stdout must match)
DEBUG = [
    ("assign_in_if", "print the factorial of 5, which is 120",
     '#include <stdio.h>\nint fact(int n) {\n    if (n = 0) return 1;\n'
     '    return n * fact(n - 1);\n}\nint main(void) {\n'
     '    printf("%d\\n", fact(5));\n    return 0;\n}\n',
     r"\b120\b"),
    ("int_division", "print the average of 1, 2 and 4 as 2.33",
     '#include <stdio.h>\nint main(void) {\n    int a[] = {1, 2, 4};\n    int sum = 0;\n'
     '    for (int i = 0; i < 3; i++) sum += a[i];\n    double avg = sum / 3;\n'
     '    printf("%.2f\\n", avg);\n    return 0;\n}\n',
     r"2\.33"),
    ("off_by_one", "print the numbers 1 2 3 4 5 separated by spaces",
     '#include <stdio.h>\nint main(void) {\n'
     '    for (int i = 1; i < 5; i++) printf("%d ", i);\n'
     '    printf("\\n");\n    return 0;\n}\n',
     r"1\s+2\s+3\s+4\s+5"),
]

# EXPLAIN: (name, program, expected printed output)
EXPLAIN = [
    ("pointer_swap",
     '#include <stdio.h>\nint main(void) {\n    int a = 5, b = 10;\n'
     '    int *p = &a, *q = &b;\n    int t = *p; *p = *q; *q = t;\n'
     '    printf("%d %d\\n", a, b);\n    return 0;\n}\n',
     "10 5"),
    ("recursion",
     '#include <stdio.h>\nint f(int n) { return n <= 1 ? 1 : n * f(n - 1); }\n'
     'int main(void) {\n    printf("%d\\n", f(4));\n    return 0;\n}\n',
     "24"),
    ("sizeof_strlen",
     '#include <stdio.h>\n#include <string.h>\nint main(void) {\n'
     '    char s[] = "abc";\n    printf("%zu %zu\\n", sizeof(s), strlen(s));\n    return 0;\n}\n',
     "4 3"),
    ("pointer_arith",
     '#include <stdio.h>\nint main(void) {\n    int arr[] = {10, 20, 30, 40};\n'
     '    int *p = arr;\n    p += 2;\n    printf("%d %d\\n", *p, *(p - 1));\n    return 0;\n}\n',
     "30 20"),
]

# QA: (question, regex a correct answer must match)
QA = [
    ("In C, what does the 'static' keyword do when applied to a local variable? "
     "Answer in 2-3 sentences.",
     r"persist|retain|preserv|keeps?( its)? value|lifetime|between (function )?calls"),
    ("What is the difference between malloc and calloc? Answer in 2-3 sentences.",
     r"zero|initiali[sz]"),
    ("Why is gets() dangerous in C and what should be used instead? Answer briefly.",
     r"fgets"),
    ("Which header file declares strlen? Answer briefly.", r"string\.h"),
    ("What is a dangling pointer in C? Answer in 2-3 sentences.",
     r"free|deallocat|no longer valid|out of scope"),
]

# ---------------------------------------------------------------- HELPERS


def ask(model, prompt):
    t0 = time.perf_counter()
    r = requests.post(OLLAMA, json={
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0, "num_predict": 900},
    }, timeout=900)
    wall = time.perf_counter() - t0
    d = r.json()
    tps = d["eval_count"] / (d["eval_duration"] / 1e9) if d.get("eval_duration") else 0
    return d.get("response", ""), wall, tps


def extract_c(text):
    m = re.search(r"```(?:c|C)?\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else None


def compile_run(code, stdin, workdir, tag):
    """Returns (stdout or None, gcc warning count)."""
    if not code:
        return None, 0
    src = os.path.join(workdir, tag + ".c")
    exe = os.path.join(workdir, tag + (".exe" if os.name == "nt" else ""))
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)
    cp = subprocess.run([GCC, "-Wall", "-Wextra", "-o", exe, src],
                        capture_output=True, text=True)
    warns = cp.stderr.count("warning:")
    if cp.returncode != 0:
        return None, warns
    try:
        rp = subprocess.run([exe], input=stdin, capture_output=True,
                            text=True, timeout=5)
        return rp.stdout, warns
    except subprocess.TimeoutExpired:
        return None, warns


def last_output_line(text):
    found = re.findall(r"output:\s*(.*)", text, re.I)
    if not found:
        return None
    val = re.sub(r"[^\w ]", "", found[-1])
    return " ".join(val.split())


# ---------------------------------------------------------------- RUN
rows = []
with tempfile.TemporaryDirectory() as tmp:
    for m in MODELS:
        print(f"\n=== {m} ===")
        ask(m, "Hi")  # warm-up: exclude model load time
        tagm = re.sub(r"\W", "_", m)

        def record(task, name, ok, wall, tps, warns, text):
            flesch = ""
            if task in ("explain", "qa"):
                flesch = round(textstat.flesch_reading_ease(text), 1)
            rows.append(dict(model=m, task=task, name=name,passed=int(bool(ok)),
                             latency_s=round(wall, 2), tok_per_s=round(tps, 1),
                             gcc_warnings=warns, flesch=flesch, response=text.strip()))
            print(f"  [{task:<7}] {'PASS' if ok else 'FAIL'}  {wall:5.1f}s  {name}")

        for name, prompt, stdin, pat in WRITE:
            text, wall, tps = ask(m, prompt)
            out, warns = compile_run(extract_c(text), stdin, tmp, f"{tagm}_w_{name}")
            record("write", name, out is not None and re.search(pat, out, re.I),
                   wall, tps, warns, text)

        for name, goal, buggy, pat in DEBUG:
            prompt = (f"This C program is supposed to {goal}, but it has a bug.\n"
                      f"```c\n{buggy}```\nFix the bug. " + CODE_ONLY)
            text, wall, tps = ask(m, prompt)
            out, warns = compile_run(extract_c(text), "", tmp, f"{tagm}_d_{name}")
            record("debug", name, out is not None and re.search(pat, out),
                   wall, tps, warns, text)

        for name, code, expected in EXPLAIN:
            prompt = (f"Here is a C program:\n```c\n{code}```\n"
                      "Explain step by step what it does, then give the exact printed "
                      "output on the final line in the form 'OUTPUT: <text>'.")
            text, wall, tps = ask(m, prompt)
            record("explain", name, last_output_line(text) == expected,
                   wall, tps, 0, text)

        for q, pat in QA:
            text, wall, tps = ask(m, q)
            record("qa", q[:40], re.search(pat, text, re.I), wall, tps, 0, text)

with open("eval_c_results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

# ---------------------------------------------------------------- SUMMARY
TASKS = ["write", "debug", "explain", "qa"]
print("\n" + "=" * 86)
print("PASS RATE by task, then latency and readability")
print(f"{'model':<22}" + "".join(f"{t:>9}" for t in TASKS)
      + f"{'overall':>9}{'lat(s)':>8}{'tok/s':>7}{'flesch':>8}{'warn':>6}")
for m in MODELS:
    mr = [r for r in rows if r["model"] == m]
    per = defaultdict(list)
    for r in mr:
        per[r["task"]].append(r["passed"])
    cells = "".join(f"{100 * mean(per[t]):>8.0f}%" for t in TASKS)
    overall = 100 * mean(r["passed"] for r in mr)
    fl = [r["flesch"] for r in mr if r["flesch"] != ""]
    code_rows = [r for r in mr if r["task"] in ("write", "debug")]
    print(f"{m:<22}{cells}{overall:>8.0f}%"
          f"{mean(r['latency_s'] for r in mr):>8.1f}"
          f"{mean(r['tok_per_s'] for r in mr):>7.1f}"
          f"{mean(fl):>8.1f}"
          f"{mean(r['gcc_warnings'] for r in code_rows):>6.1f}")
print("\nflesch = readability of prose answers (higher = easier); "
      "warn = avg gcc -Wall -Wextra warnings per code answer.")
print("All responses saved to eval_c_results.csv")