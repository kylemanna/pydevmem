#!/usr/bin/env python
"""
This is designed primarily for use with accessing /dev/mem on OMAP platforms.
It should work on other platforms and work to mmap() files rather then just
/dev/mem, but these use cases aren't well tested.

All file accesses are aligned to DevMem.word bytes, which is 4 bytes on ARM
platforms to avoid data abort faults when accessing peripheral registers.

References:
    http://wiki.python.org/moin/PythonSpeed/PerformanceTips
    http://www.python.org/dev/peps/pep-0008/

"""

import os
import sys
import mmap
import struct


class DevMemBuffer:
    """This class holds data for objects returned from DevMem class. It allows an easy way to print hex data"""

    lut = {1: "B", 2: "H", 4: "I"}

    def __init__(self, base_addr, data, word=4):
        self.data = data
        self.base_addr = base_addr
        self.word = word

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        start = i * self.word
        stop = start + self.word

        if stop > len(self.data):
            raise IndexError

        return self.data[start:stop]

    def __setitem__(self, i, value):
        raise NotImplementedError("DevMemBuffer is immutable")
        # self.data[i] = value

    def hexdump(self, words_per_row=4):
        # Build a list of strings and then join them in the last step.
        # This is more efficient then concat'ing immutable strings.

        dump = []
        row_step = words_per_row * self.word

        for row_pos in range(0, len(self.data), row_step):
            row = ["0x{0:02x}: ".format(self.base_addr + row_pos)]

            row_stop = min(row_pos + row_step, len(self.data))
            for col_pos in range(row_pos, row_stop, self.word):
                data = struct.unpack_from(self.lut[self.word], self.data, col_pos)
                for b in data:
                    row.append(" {0:0{width}x}".format(b, width=self.word * 2))

            dump.append(" ".join(row))

        return "\n".join(dump)

    def __str__(self):
        return self.hexdump()


class DevMem:
    """Class to read and write data aligned to word boundaries of /dev/mem"""

    f = None

    def __init__(self, base_addr, length=1, filename="/dev/mem", debug=0, word=4):

        if base_addr < 0 or length < 0:
            raise AssertionError
        self._debug = debug

        # Size of a word that will be used for reading/writing
        self.word = word
        self.mask = ~(word - 1)

        self.base_addr = base_addr & ~(mmap.PAGESIZE - 1)
        self.base_addr_offset = base_addr - self.base_addr

        stop = base_addr + length * self.word
        if stop % self.mask:
            stop = (stop + self.word) & ~(self.word - 1)

        self.length = stop - self.base_addr
        self.fname = filename

        # Check filesize (doesn't work with /dev/mem)
        # filesize = os.stat(self.fname).st_size
        # if (self.base_addr + self.length) > filesize:
        #    self.length = filesize - self.base_addr

        self.debug(
            "init with base_addr = {0} and length = {1} on {2}".format(
                hex(self.base_addr), hex(self.length), self.fname
            )
        )

        # Open file and mmap
        self.f = os.open(self.fname, os.O_RDWR | os.O_SYNC)
        self.mem = mmap.mmap(
            self.f,
            self.length,
            mmap.MAP_SHARED,
            mmap.PROT_READ | mmap.PROT_WRITE,
            offset=self.base_addr,
        )

    def __del__(self):
        if self.f:
            os.close(self.f)

    def read(self, offset, length):
        """Read length number of words from offset"""

        if offset < 0 or length < 0:
            raise AssertionError

        self.debug(
            "reading {0} bytes from offset {1}".format(length * self.word, hex(offset))
        )

        # Compensate for the base_address not being what the user requested
        # and then seek to the aligned offset.
        virt_base_addr = self.base_addr_offset & self.mask
        self.mem.seek(virt_base_addr + offset)

        # Read length words of size self.word and return bytes()
        data = self.mem.read(length * self.word)

        abs_addr = self.base_addr + virt_base_addr
        return DevMemBuffer(abs_addr + offset, data, self.word)

    def write(self, offset, din):
        """Write length number of words to offset"""

        if offset < 0 or len(din) <= 0:
            raise AssertionError

        self.debug(
            "writing {0} bytes to offset {1}".format(len(din) * self.word, hex(offset))
        )

        # Compensate for the base_address not being what the user requested
        # fix double plus offset
        # offset += self.base_addr_offset

        # Check that the operation is going write to an aligned location
        if offset & ~self.mask:
            raise AssertionError

        # Seek to the aligned offset
        virt_base_addr = self.base_addr_offset & self.mask
        self.mem.seek(virt_base_addr + offset)

        # Read until the end of our aligned address
        for i in range(len(din)):
            self.debug(
                "writing at position = {0}: 0x{1:x}".format(
                    self.self.mem.tell(), din[i]
                )
            )
            # Write one word at a time
            self.mem.write(struct.pack("I", din[i]))

    def debug_set(self, value):
        self._debug = value

    def debug(self, debug_str):
        if self._debug:
            print("DevMem Debug: {0}".format(debug_str))
