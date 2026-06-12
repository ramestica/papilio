#   _                            ____                 
#  | |                          |  _ \                
#  | |    _   _ _ __   __ _ _ __| |_) | __ _ ___  ___ 
#  | |   | | | | '_ \ / _` | '__|  _ < / _` / __|/ _ \
#  | |___| |_| | | | | (_| | |  | |_) | (_| \__ \  __/
#  |______\__,_|_| |_|\__,_|_|  |____/ \__,_|___/\___|
#
# https://patorjk.com/software/taag/#p=display&f=Big&t=LunarBase&x=none&v=4&h=4&w=80&we=false

import os
import subprocess
from amaranth.build import *
from amaranth.vendor import XilinxPlatform
from amaranth_boards.resources import *

__all__ = ["PapilioProPlatform"]

class PapilioProPlatform(XilinxPlatform):
    device      = "xc6slx9"
    package     = "tqg144"
    speed       = "2"
    default_clk = "clk32"
    resources   = [
        Resource("clk32", 0, Pins("P94", dir="i"),
            Clock(32e6), Attrs(IOSTANDARD="LVCMOS33")
        ),
        Resource("led", 0, Pins("P112", dir="o"),
            Attrs(IOSTANDARD="LVCMOS33", DRIVE="24", SLEW="QUIETIO")
        ),
        *SPIFlashResources(0,
            cs_n="P38", clk="P70", copi="P64", cipo="P65",
            attrs=Attrs(IOSTANDARD="LVCMOS33")
        ),
        SDRAMResource(0,
            clk="P32",
            cs_n="P1", cke="P33", we_n="P6", ras_n="P2", cas_n="P5",
            ba="P143 P142",
            a="P140 P139 P138 P137 P46 P45 P44 P43 P41 P40 P141 P35 P34",
            dq="P9 P10 P11 P12 P14 P15 P16 P8 P21 P22 P23 P24 P26 P27 P29 P30",
            dqm="P7 P17",
            attrs=Attrs(IOSTANDARD="LVCMOS33")
        ),
    ]
    connectors  = [
        Connector("A", 0,
            "P48 P51 P56 P58 P61 P66 P67 P75 P79 P81 P83 P85 P88 P93 P98 P100"
        ),
        Connector("B", 0,
            "P99 P97 P92 P87 P84 P82 P80 P78 P74 P95 P62 P59 P57 P55 P50 P47"
        ),
        Connector("C", 0,
            "P114 P115 P116 P117 P118 P119 P120 P121 P123 P124 P126 P127 P131 P132 P133 P134"
        ),
    ]
