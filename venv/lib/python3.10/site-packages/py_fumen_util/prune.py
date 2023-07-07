# -*- coding: utf-8 -*-

import sys

from py_fumen_py import *

def prune(fumen_codes, return_error=False, keep_invalid=True):
    results = []
    for code in fumen_codes:
        try:
            input_pages = decode(code)
            if input_pages[-1].field:
                for line in input_pages[-1].field[:]:
                    for i, mino in enumerate(line):
                        if mino.is_colored():
                            line[i] = Mino._
            results.append(encode(input_pages))
        except Exception as e:
            if keep_invalid:
                results.append('')
            if print_error:
                print(e)

    return results

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for line in prune(' '.join(sys.argv[1:]).split()):
            print(line)

