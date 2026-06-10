from migen import *
from litex_boards.platforms import gadgetfactory_papilio_pro

class Blinky(Module):
    def __init__(self, platform):
        clk = platform.request("clk32")
        led = platform.request("user_led", 0)

        self.clock_domains.cd_sys = ClockDomain("sys")
        self.comb += self.cd_sys.clk.eq(clk)

        counter = Signal(25)
        self.sync += counter.eq(counter + 1)
        self.comb += led.eq(counter[24])

def main():
    platform = gadgetfactory_papilio_pro.Platform()
    blinky = Blinky(platform)
    platform.build(blinky, build_dir="build", run=False)

if __name__ == "__main__":
    main()
