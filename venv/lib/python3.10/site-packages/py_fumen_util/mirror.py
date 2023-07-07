# -*- coding: utf-8 -*-

import sys

from py_fumen_py import *

def mirror(fumen_codes, print_error=True, keep_invalid=True):
    results = []
    for code in fumen_codes:
        try:
            input_pages = decode(code)
            for i, page in enumerate(input_pages):
                page.field.mirror(mirror_color=True)
                if page.operation:
                    page.operation.mirror()
            results.append(encode(input_pages))
        except Exception as e:
            if keep_invalid:
                results.append('')
            if print_error:
                print(e)

    return results

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for line in mirror(' '.join(sys.argv[1:]).split()):
            print(line)
