# -*- coding: utf-8 -*-

import sys

from py_fumen_py import *

def split(fumen_codes, print_error=True, keep_invalid=True):
    results = []
    for code in fumen_codes:
        try:
            input_pages = decode(code)
            for page in input_pages:
                if input_pages[0].flags.colorize:
                    page.flags.colorize = True
                results.append(encode([page]))
        except Exception as e:
            if keep_invalid:
                results.append('')
            if print_error:
                print(e)

    return results

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for line in split(' '.join(sys.argv[1:]).split()):
            print(line)
