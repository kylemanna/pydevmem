#!/usr/bin/env python3

import optparse
import sys
from . import DevMem

"""If this is run as a script (rather then imported as a module) it provides some basic functionality out of the box"""

parser = optparse.OptionParser()

parser.add_option(
    "-r", "--read", dest="read", metavar="ADDR", type=int, help="read a value"
)

parser.add_option(
    "-w",
    "--write",
    dest="write",
    help="write a value",
    nargs=2,
    type=int,
    metavar="ADDR VALUE",
)

parser.add_option(
    "-n", "--num", dest="num", help="number of words to read", type=int, default=1
)

parser.add_option(
    "-s",
    "--word-size",
    dest="word_size",
    help="size of word when displayed",
    type=int,
    default=4,
)

parser.add_option(
    "-m",
    "--mmap",
    dest="mmap",
    metavar="FILE",
    help="file to open with mmap()",
    type=str,
    default="/dev/mem",
)

parser.add_option(
    "-v",
    action="store_true",
    dest="verbose",
    help="provide more information regarding operation",
)

parser.add_option(
    "-d", action="store_true", dest="debug", help="provide debugging information"
)

(options, args) = parser.parse_args()

# Check for sane arguments
if options.write is not None and options.read is not None:
    parser.print_help()
    print("\nError: Both read and write are specified")
    sys.exit(1)
elif options.write is None and options.read is None:
    parser.print_help()
    print("\nError: Neither read or write are specified")
    sys.exit(1)

if options.num < 0:
    parser.print_help()
    print("\nError: Invalid num of words specified")
    sys.exit(1)

if options.word_size != 1 and options.word_size != 2 and options.word_size != 4:
    parser.print_help()
    print("\nError: Invalid word size specified")
    sys.exit(1)

# Only support writing one word at a time, force this
if options.write is not None and options.num != 1:
    print("Warning: Forcing number of words to 1 for set operation\n")
    options.num = 1

# Determine base address to operate on
addr = options.read
if options.write is not None:
    addr = options.write[0]

# Create the Dev Mem object that does the magic
mem = DevMem(addr, length=options.num, filename=options.mmap, debug=options.debug)

if options.debug:
    mem.debug_set(1)

# Perform the actual read or write
if options.write is not None:
    if options.verbose:
        print(
            "Value before write:\t{0}".format(
                mem.read(0x0, options.num).hexdump(options.word_size)
            )
        )

    mem.write(0x0, [options.write[1]])

    if options.verbose:
        print(
            "Value after write:\t{0}".format(
                mem.read(0x0, options.num).hexdump(options.word_size)
            )
        )
else:
    print(mem.read(0x0, options.num).hexdump(options.word_size))
