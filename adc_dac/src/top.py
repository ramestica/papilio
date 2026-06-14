import os
from amaranth import *
from amaranth.build import *
from amaranth.lib import io
from papilio_pro import PapilioProPlatform

class PapilioProPlatformNoAutoClk(PapilioProPlatform):
    def create_missing_domain(self, name):
        # We manage all clock domains manually — do nothing
        return Module()

class PRBSGenerator(Elaboratable):
    def __init__(self):
        self.prbs = Signal(8)

    def elaborate(self, platform):
        m = Module()
        state = Signal(8, init=1)
        m.d.sync += state.eq(Cat(
            state[7] ^ state[5] ^ state[4] ^ state[3],
            state[0], state[1], state[2], state[3],
            state[4], state[5], state[6],
        ))
        m.d.comb += self.prbs.eq(state)
        return m

class AdcDac(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # --- PLL ---
        clk_in     = platform.request("clk32", 0, dir="-")
        pll_fb     = Signal()
        pll_locked = Signal()
        clk_adc    = Signal()
        clk_dac    = Signal()
        clk_adc90  = Signal()

        m.submodules.pll = Instance("PLL_BASE",
            p_BANDWIDTH         = "OPTIMIZED",
            p_CLK_FEEDBACK      = "CLKFBOUT",
            p_COMPENSATION      = "INTERNAL",
            p_DIVCLK_DIVIDE     = 1,
            p_CLKFBOUT_MULT     = 16,
            p_CLKFBOUT_PHASE    = 0.0,
            p_CLKOUT0_DIVIDE    = 16,
            p_CLKOUT0_PHASE     = 0.0,
            p_CLKOUT1_DIVIDE    = 16,
            p_CLKOUT1_PHASE     = 0.0,
            p_CLKOUT2_DIVIDE    = 16,
            p_CLKOUT2_PHASE     = 90.0,
            p_CLKOUT3_DIVIDE    = 16,
            p_CLKOUT3_PHASE     = 0.0,
            p_CLKOUT4_DIVIDE    = 16,
            p_CLKOUT4_PHASE     = 0.0,
            p_CLKOUT5_DIVIDE    = 16,
            p_CLKOUT5_PHASE     = 0.0,
            p_CLKIN_PERIOD      = 31.25,
            p_REF_JITTER        = 0.100,
            i_CLKFBIN           = pll_fb,
            o_CLKFBOUT          = pll_fb,
            o_CLKOUT0           = clk_adc,
            o_CLKOUT1           = clk_dac,
            o_CLKOUT2           = clk_adc90,
            o_CLKOUT3           = Signal(),
            o_CLKOUT4           = Signal(),
            o_CLKOUT5           = Signal(),
            i_CLKIN             = clk_in.io,
            o_LOCKED            = pll_locked,
            i_RST               = Const(0),
        )

        # --- Clock domains ---
        m.domains.sys   = ClockDomain("sys")
        m.domains.sync  = ClockDomain("sync")
        m.domains.adc   = ClockDomain("adc")
        m.domains.dac   = ClockDomain("dac")
        m.domains.adc90 = ClockDomain("adc90")
        m.d.comb += [
            ClockSignal("sys").eq(clk_adc),
            ClockSignal("sync").eq(clk_dac),
            ClockSignal("adc").eq(clk_adc),
            ClockSignal("dac").eq(clk_dac),
            ClockSignal("adc90").eq(clk_adc90),
            ResetSignal("sys").eq(~pll_locked),
            ResetSignal("sync").eq(~pll_locked),
            ResetSignal("adc").eq(~pll_locked),
            ResetSignal("dac").eq(~pll_locked),
            ResetSignal("adc90").eq(~pll_locked),
        ]

        # --- PRBS driving DAC ---
        m.submodules.prbs = prbs = PRBSGenerator()

        # --- ADC sampling ---
        adc  = platform.request("adc",  0)
        diff = platform.request("diff", 0)
        m.d.adc += diff.o.eq(adc.i)

        # --- DAC output ---
        dac = platform.request("dac", 0)
        m.d.dac += dac.o.eq(prbs.prbs)

        # --- Clock outputs via xdr=2 (DDR) ---
        clk_adc_pin   = platform.request("clk_adc",     0, xdr=2)
        clk_adc90_pin = platform.request("clk_adc_90d", 0, xdr=2)
        clk_dac_pin   = platform.request("clk_dac",     0, xdr=2)

        m.d.comb += [
            clk_adc_pin.o_clk.eq(clk_adc),
            clk_adc_pin.o0.eq(1),
            clk_adc_pin.o1.eq(0),

            clk_adc90_pin.o_clk.eq(clk_adc90),
            clk_adc90_pin.o0.eq(1),
            clk_adc90_pin.o1.eq(0),

            clk_dac_pin.o_clk.eq(clk_dac),
            clk_dac_pin.o0.eq(1),
            clk_dac_pin.o1.eq(0),
        ]

        return m

if __name__ == "__main__":
    platform = PapilioProPlatformNoAutoClk()
    platform.add_resources([
        Resource("clk_adc",     0, Pins("P55",  dir="o"), Attrs(IOSTANDARD="LVTTL")),
        Resource("clk_adc_90d", 0, Pins("P114", dir="o"), Attrs(IOSTANDARD="LVTTL")),
        Resource("clk_dac",     0, Pins("P97",  dir="o"), Attrs(IOSTANDARD="LVTTL")),
        Resource("adc",  0, Pins("P95 P67 P62 P66 P59 P61 P57 P58", dir="i"), Attrs(IOSTANDARD="LVTTL")),
        Resource("dac",  0, Pins("P82 P85 P84 P88 P87 P93 P92 P98", dir="o"), Attrs(IOSTANDARD="LVTTL")),
        Resource("diff", 0, Pins("P123 P124 P126 P127 P131 P132 P133 P134", dir="o"), Attrs(IOSTANDARD="LVTTL")),
    ])

    plan = platform.prepare(AdcDac())
    build_dir = "../build"
    os.makedirs(build_dir, exist_ok=True)
    for filename, content in plan.files.items():
        with open(os.path.join(build_dir, filename), "w") as f:
            f.write(content)
    print(f"Generated: {list(plan.files.keys())}")
