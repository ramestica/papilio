from amaranth import *
from papilio_pro import PapilioProPlatform

class Blinky(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        led     = platform.request("led", 0)
        counter = Signal(25)

        m.d.sync += counter.eq(counter + 1)
        m.d.comb += led.o.eq(counter[24])

        return m

if __name__ == "__main__":
    import os
    plan = PapilioProPlatform().prepare(Blinky())
    build_dir = "../build"
    os.makedirs(build_dir, exist_ok=True)
    for filename, content in plan.files.items():
        with open(os.path.join(build_dir, filename), "w") as f:
            f.write(content)
    print(f"Generated {list(plan.files.keys())}")
