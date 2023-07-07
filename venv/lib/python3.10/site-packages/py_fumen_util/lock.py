# -*- coding: utf-8 -*-

import sys

from py_fumen_py import *

def lock(fumen_codes, print_error=True, keep_invalid=True):
    results = []
    for code in fumen_codes:
        try:
            input_pages = decode(code)
            input_pages.append(Page(flags=Flags(lock=True)))
            results.append(encode(input_pages))
        except Exception as e:
            if keep_invalid:
                results.append('')
            if print_error:
                print(e)

    return results

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for line in lock(' '.join(sys.argv[1:]).split()):
            print(line)
