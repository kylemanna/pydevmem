#!/usr/bin/env python3

import argparse
import os
import sys

from . import DevMem

"""If this is run as a script (rather then imported as a module) it provides some basic functionality out of the box"""

# Need to fix up argparse's prog value as it's broken and returns `__main__.py`
# Upstream bug:
# * https://bugs.python.org/issue22240
# pip workaround:
# * https://github.com/pypa/pip/blob/08c99b6e00135ca8df2e98db58aa0b701b971c64/src/pip/_internal/utils/misc.py#L124-L134
def get_prog() -> str:
    """Determine the program name if invoked directly or as a module"""

    name = (
        sys.argv[0]
        if globals().get("__spec__") is None
        else __spec__.name.partition(".")[0]
    )
    try:
        prog = os.path.basename(sys.argv[0])
        if prog in ("__main__.py", "-c"):
            return "{} -m {}".format(sys.executable, name)
        else:
            return prog
    except (AttributeError, TypeError, IndexError):
        pass

    return name


def main() -> int:
    """Main function with useful demo application"""

    parser = argparse.ArgumentParser(prog=get_prog())

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-r", "--read", metavar="ADDR", type=lambda x: int(x, 0), help="read a value"
    )
    group.add_argument(
        "-w",
        "--write",
        help="write a value",
        nargs=2,
        type=lambda x: int(x, 0),
        metavar=("ADDR", "VALUE"),
    )

    parser.add_argument(
        "-n",
        "--num",
        help="number of words to read",
        type=lambda x: int(x, 0),
        default=1,
    )

    parser.add_argument(
        "-s",
        "--word-size",
        help="size of word when displayed",
        type=int,
        default=4,
        choices=[1, 2, 4],
    )

    parser.add_argument(
        "-m",
        "--mmap",
        metavar="FILE",
        help="file to open with mmap()",
        type=str,
        default="/dev/mem",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="provide more information regarding operation",
    )

    parser.add_argument(
        "-d", "--debug", action="store_true", help="provide debugging information"
    )

    args = parser.parse_args()

    # Check for sane arguments
    if args.num < 0:
        parser.print_help()
        print("\nError: Invalid num of words specified")
        return 1

    # Only support writing one word at a time, force this
    if args.write is not None and args.num != 1:
        print("Warning: Forcing number of words to 1 for set operation\n")
        args.num = 1

    # Determine base address to operate on
    addr = args.write[0] if args.write else args.read

    # Create the Dev Mem object that does the magic
    mem = DevMem(addr, length=args.num, filename=args.mmap, debug=args.debug)

    # Perform the actual read or write
    if args.write is not None:
        if args.verbose:
            print(
                "Value before write:\t{0}".format(
                    mem.read(0x0, args.num).hexdump(args.word_size)
                )
            )

        mem.write(0x0, [args.write[1]])

        if args.verbose:
            print(
                "Value after write:\t{0}".format(
                    mem.read(0x0, args.num).hexdump(args.word_size)
                )
            )
    else:
        print(mem.read(0x0, args.num).hexdump(args.word_size))


if __name__ == "__main__":
    sys.exit(main())
