#!/usr/bin/env python
"""
This tool dumps the MDIO register on systems similar to the Beaglebone and 
TI814x platforms.
"""

import sys
import devmem

class PhyMDIO:
    def __init__(self, base_addr):
        self.base_addr = base_addr
        self.mem = devmem.DevMem(base_addr, 0x100, "/dev/mem", 0)

    def get_mdio(self, offset):
        reg_go = 1 << 31
        reg_regaddr = offset << 21
        reg = 0
        reg = reg_go | reg_regaddr
        self.mem.write(0x80, [reg])

        buf = self.mem.read(0x80, 1)
        while buf[0] & reg_go:
            buf = self.mem.read(0x80, 1)

        buf.base_addr = offset
        buf[0] &= 0xffff

        return buf

    def get_cpsw(self, offset):
        return self.mem.read(offset, 1)

def dump_mdio(base_addr):
    phy = PhyMDIO(base_addr)

    cpsw_name = ["MDIO Version",
                 "MDIO Control",
                 "PHY Alive Status",
                 "PHY Link Status"]

    mii_name = ["MII Basic Mode Control",
                "MII Basic Mode Status",
                "MII PHY ID 1",
                "MII PHY ID 2",
                "MII Advertisement Control",
                "MII Link Parner Ability",
                "MII Expansion",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII 1000BASE-T Control",
                "MII 1000BASE-T Status",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Extended Status",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Disconnect Counter",
                "MII False Carrier Counter",
                "MII N-way Auto Neg Test",
                "MII Receive Error Counter",
                "MII Silicon Revision",
                "MII TPI Status for 10 Mbps",
                "MII Network Interface Config",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Manf Specific",
                "MII Manf Specific"]

    for i in range(4):
        print "{0!s:38} {1}".format(cpsw_name[i] + ' Register:',
                                    phy.get_cpsw(i << 2))
    
    # Blank line 
    print

    for i in range(0x20):
        print "{0!s:38} {1}".format(mii_name[i] + ' Register:',
                                    phy.get_mdio(i).hexdump(2, 2))

if __name__ ==  '__main__':

    sys.exit(dump_mdio(0x4a101000))
