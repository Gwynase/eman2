#!/usr/bin/env python

# Run e2 programs by running the commands with -h

from pathlib import Path
import subprocess
import sys

MYDIR = Path(__file__).parent
PROGS_DIR = MYDIR.parent / "programs"

progs = set(p.name for p in PROGS_DIR.glob('e2*.py'))

with open(MYDIR / "programs_no_test.txt", "r") as fin:
    progs_exclude = set()
    for line in fin:
        progs_exclude.add(line.split()[0])

print("\nRemoving programs from test list...")
for f in progs_exclude:
    print(f"... {f}")

progs -= progs_exclude

failed_progs = []
for prog in progs:
    proc = subprocess.run([prog, "-h"], stdout=subprocess.DEVNULL)
    print(f"Running: {' '.join(proc.args)}")
    if proc.returncode:
        failed_progs.append(prog)

print(f"\nTotal failed programs: {len(failed_progs)} / {len(progs)}")
for prog in failed_progs:
    print(prog)

if failed_progs:
    sys.exit(1)
