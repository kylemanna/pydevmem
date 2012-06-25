Python DevMem
=============

This is designed primarily for use with accessing /dev/mem on OMAP platforms.
It should work on other platforms and work to mmap() files rather then just
/dev/mem, but these use cases aren't well tested.

All file accesses are aligned to DevMem.word bytes, which is 4 bytes on ARM
platforms to avoid data abort faults when accessing peripheral registers.

Usage
-----

    Usage: devmem.py [options]

    Options:
      -h, --help            show this help message and exit
      -r ADDR, --read=ADDR  read a value
      -w ADDR VALUE, --write=ADDR VALUE
    						write a value
      -n NUM, --num=NUM     number of words to read
      -s WORD_SIZE, --word-size=WORD_SIZE
    						size of word when displayed
      -m FILE, --mmap=FILE  file to open with mmap()
      -v                    provide more information regarding operation
      -d                    provide debugging information


Speed
-----

Initial testing on a BeagleBoard-xM (Cortex-A8 in a TI DM3730) shows that
starting up the python interpreter is pretty slow:

    # time (echo | python)

    real    0m0.859s
    user    0m0.750s
    sys     0m0.102s

    # time python ./pydevmem.py -r 0x4830a204 -n 8
    0x4830a204:   1b89102f  00000000  00000000  000000f0
    0x4830a214:   cafeb891  0c030016  015739eb  1ff00000

    real    0m1.109s
    user    0m0.977s
    sys     0m0.133s

    # time python -S ./pydevmem.py -r 0x4830a204 -n 8
    0x4830a204:   1b89102f  00000000  00000000  000000f0
    0x4830a214:   cafeb891  0c030016  015739eb  1ff00000

    real    0m0.659s
    user    0m0.602s
    sys     0m0.047s

    # time python -S ./pydevmem.pyc -r 0x4830a204 -n 8
    0x4830a204:   1b89102f  00000000  00000000  000000f0
    0x4830a214:   cafeb891  0c030016  015739eb  1ff00000

    real    0m0.647s
    user    0m0.508s
    sys     0m0.133s


System information for those tests:

    Linux omap 3.0.6-x3 #1 SMP Wed Oct 5 07:19:24 UTC 2011 armv7l GNU/Linux

    python              2.7.2-7ubuntu2
    python-configobj    4.7.2+ds-3
    python-minimal      2.7.2-7ubuntu2
    python2.7           2.7.2-5ubuntu1
    python2.7-minimal   2.7.2-5ubuntu1

Something needs to be sped up to make python start-up in a reasonable amount
of time.
