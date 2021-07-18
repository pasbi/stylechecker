#!/usr/bin/env python3

import sys
import argparse
import re
import checks as c
import json
import os


base_checks = [c.no_trailing_whitespace, c.no_tabs, c.unix_linebreak, c.single_blank_line_eof]
checker_map = {
  re.compile("^.*\.cpp$", re.IGNORECASE): base_checks + [c.no_bad_cpp_patterns, c.limit_line_length],
  re.compile("^.*\.h$", re.IGNORECASE): base_checks + [c.no_bad_cpp_patterns, c.limit_line_length],
  # re.compile("^.*\.py$", re.IGNORECASE): base_checks,
  re.compile("^CMakeLists.txt$"): base_checks,
  re.compile("^.*\.cmake$", re.IGNORECASE): base_checks,
  re.compile("^.*\.in$", re.IGNORECASE): base_checks,
  re.compile("^.*\.yml$", re.IGNORECASE): base_checks,
  re.compile("^.*\.yaml$", re.IGNORECASE): base_checks,
  re.compile("^.*\.sh$", re.IGNORECASE): base_checks,
  re.compile("^.*\.md$", re.IGNORECASE): base_checks,
  re.compile("^.*\.qss$", re.IGNORECASE): base_checks,
}

class Checker:
    def __init__(self, filename, checks, options):
        self.filename = filename
        self.checks = checks
        self.options = options
        with open(filename, 'rb') as f:
            # open as binary, otherwise \r\n will be hidden.
            self.lines = f.read().decode('utf-8').split("\n")

    def check(self):
        return all(self._apply_check(check) for check in self.checks)

    def handle_problem(self, problem, line=None):
        location = self.filename
        if line is not None:
            location += f":{line}"

        if isinstance(problem, c.Warning):
            print(f"WARNING in {location}: {problem.msg}")
            return True
        elif isinstance(problem, c.Error):
            print(f"ERROR in {location}: {problem.msg}")
            return False
        else:
            return True

    def _apply_check(self, check):
        if check.per_line:
            return all(self.handle_problem(check(line, options), i + 1)
                       for i, line in enumerate(self.lines))
        else:
            return self.handle_problem(check(self.lines, options))

def select_checks(filename):
    for pattern, checks in checker_map.items():
        if pattern.search(filename):
            return checks
    return None

def check_single_file(filename, options):
    checks = select_checks(os.path.basename(filename))
    if checks is None:
        return True
    else:
        return Checker(filename, checks, options).check()

def check(filenames, options):
    results = list(check_single_file(fn, options) for fn in filenames)
    uncompliant_files = [f for r, f in zip(results, filenames) if not r]

    if len(uncompliant_files) > 0:
        print(f"Uncompliant files ({len(uncompliant_files)})")
        for fn in uncompliant_files:
            print(fn)
    else:
        print("All files comply.")

    return len(uncompliant_files) == 0

def load_options(filename):
    with open(filename, 'r') as f:
        options = json.load(f)

    options["re_cpp_allowed_include"] = re.compile(r'^\s*#include <.*/.*\.h>')
    options["re_cpp_disallowed_include"] = re.compile(r'^\s*#include <.*\.h>')
    options["re_cpp_include_exceptions"] = [re.compile(fr'^\s*#include <{x}>')
                                         for x in options["c_style_include_exceptions"]]
    return options

def list_files(root):
    for root, _, fns in os.walk(root):
        for fn in fns:
            yield os.path.join(root, fn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
"""Simple style checker
Automatically picks the right rules based on the file ending.
Fails if there is at least one uncompliant file, succeeds
otherwise.""")
    parser.add_argument("--root", required=True,
            help="Files in the root directory will be checked (recursively). "
                 "The actually applied checks depend on the file ending. "
                 "Files can be excluded from the check based on their path.")
    parser.add_argument("--options", required=True, help="The options file.")
    args = parser.parse_args()

    options = load_options(args.options)

    fns = list(list_files(args.root))
    forbidden_paths = [re.compile(pattern) for pattern in options["excluded_paths"]]
    fns = [fn for fn in fns if not any(r.search(fn) for r in forbidden_paths)]

    if check(fns, options):
        sys.exit(0)
    else:
        sys.exit(1)
