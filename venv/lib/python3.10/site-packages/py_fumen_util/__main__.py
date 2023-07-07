# -*- coding:utf-8 -*-

import argparse
import sys

from py_fumen_py import *
import py_fumen_util

_alias_map = {
    'combine': 'join',
    'concat': 'join',
    'compile': 'assemble',
    'unglue': 'assemble',
    'decompile': 'disassemble',
    'glue': 'disassemble',
    'greyout': 'grayout',
    'gray': 'grayout',
    'grey': 'grayout',
    'grayoutall': 'grayout_all',
    'greyoutall': 'grayout_all',
    'grayall': 'grayout_all',
    'greyall': 'grayout_all',
    'pruneall': 'prune_all',
    'flip': 'mirror',
}

_usage = [
        'commands (case-insensitive):',
        '  join:        Join multiple Fumens into one',
        '               alias: combine, concat',
        '  split:       Split each page into a Fumen',
        '',
        '  assemble:    Assemble Fumen placements into one page',
        '               alias: compile, unglue',
        '  disassemble: Disassemble each Fumen page into tetromino placements',
        '               alias: decompile, glue',
        '',
        '  grayout:     Gray out the last page of each fumen',
        '               alias: greyout, gray, grey',
        '  grayoutall:  Gray out all pages of each fumen',
        '               alias: greyoutall, grayall, greyall',
        '',
        '  prune:       Prune colored minos from the last page of each fumen',
        '  pruneall:    Prune colored minos from all pages of each fumen',
        '',
        '  lock:        Lock the last page of each Fumen and append a new page',
        '  mirror:      Mirror Fumen pages',
        '               alias: flip',
        '  uncomment:   Uncomment Fumen pages',
    ]

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Tetris Fumen utilies in Python.',
        prog='python3 -m py_fumen_util',
        epilog='\n'.join(_usage)
    )
    argparser.add_argument(
        'command',
        type=str,
        nargs='+',
        help='Command(s) to execute on the Fumen(s).',
    )
    argparser.add_argument(
        'file',
        type=str,
        help='File with Fumen strings, separated with whitespace and/or linebreak. Use "-" to read from standard input.',
    )

    args = argparser.parse_args()
    commands = args.command
    fumen_file = sys.stdin if args.file == '-' else open(args.file, 'r')
    fumen_codes = fumen_file.read().split()
    fumen_file.close()

    for command in commands:
        try:
            command_function = getattr(
                py_fumen_util,
                _alias_map.get(command.casefold(), command)
            )
            fumen_codes = command_function(fumen_codes)
        except Exception as e:
            print(f'"{command}" is not a valid command.\n')
            argparser.print_help()

    for line in fumen_codes:
        print(line)
