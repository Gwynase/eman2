#!/usr/bin/env python

# Run e2 programs by running the commands with -h

from pathlib import Path

MYDIR = Path(__file__).parent
PROGS_DIR = MYDIR.parent / "programs"

progs = set(p.name for p in PROGS_DIR.glob('e2*.py'))

with open(MYDIR / "programs_no_test.txt", "r") as fin:
    progs_exclude = set()
    for line in fin:
        progs_exclude.add(line.split()[0])

progs -= progs_exclude
