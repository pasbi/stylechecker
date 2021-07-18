#!/usr/bin/env python3

import json
import re

def line_check(f):
    f.per_line = True
    return f

def file_check(f):
    f.per_line = False
    return f


class Warning:
    def __init__(self, msg):
        self.msg = msg

class Error:
    def __init__(self, msg):
        self.msg = msg

@line_check
def no_trailing_whitespace(line, options):
    if line.rstrip() != line:
        return Error("Line contains trailing whitespace.")

@line_check
def no_tabs(line, options):
    ws_length = len(line) - len(line.lstrip())
    ws = line[:ws_length]
    if '\t' in ws:
        return Error("Line is indented using tabs.")

@line_check
def unix_linebreak(line, options):
    if line.endswith("\r"):
        return Error("Line ends with CRLF.")

@line_check
def no_bad_cpp_patterns(line, options):
    if any(re.search(line) for re in options["re_cpp_include_exceptions"]):
        return
    if options["re_cpp_allowed_include"].search(line):
        return
    if options["re_cpp_disallowed_include"].search(line):
        return Error("Don't use C includes (like <math.h>), use C++ includes (like <cmath>).")

@line_check
def limit_line_length(line, options):
    maxcols = options["maxcols"]
    maxcols_soft = options["maxcols_soft"]
    if len(line) > maxcols:
        return Error(f"Line too long ({len(line)}>{maxcols}).")
    elif len(line) > maxcols_soft:
        return Warning(f"Line too long ({len(line)}>{maxcols_soft}) if there's no good reason.")

@file_check
def single_blank_line_eof(lines, options):
    if len(lines) >= 1 and len(lines[-1]) > 0:
        return Error("File does not end with blank line.")
    elif len(lines) >= 2 and len(lines[-2]) == 0:
        return Error("File ends with more than one blank line.")
