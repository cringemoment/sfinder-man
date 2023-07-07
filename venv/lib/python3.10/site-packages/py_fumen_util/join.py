# -*- coding: utf-8 -*-

import sys

from py_fumen_py import *

def join(fumen_codes, print_error=True, keep_invalid=True):
    results = []
    for code in fumen_codes:
        try:
            results += decode(code)
        except Exception as e:
            if keep_invalid:
                results.append(Page())
            if print_error:
                print(e)
    return [encode(results)] if results else []

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(join(' '.join(sys.argv[1:]).split())[0])
