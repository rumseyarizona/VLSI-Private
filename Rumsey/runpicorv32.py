#!/usr/bin/env python3

from siliconcompiler import ASIC, Design
from siliconcompiler.targets import skywater130_demo


class PicoRV32(Design):
    def __init__(self):
        super().__init__()
        self.set_name("picorv32")

        # Assumes picorv32.v is in the same folder as this script
        self.set_dataroot("local", __file__)

        with self.active_fileset("rtl"):
            with self.active_dataroot("local"):
                self.set_topmodule("picorv32")
                self.add_file("picorv32.v")


def main():
    design = PicoRV32()

    project = ASIC(design)
    project.add_fileset("rtl")

    # Load SkyWater 130 demo ASIC target
    skywater130_demo(project)

    # Run on SiliconCompiler remote/cloud
    project.option.set_remote(True)

    project.run()
    project.summary()
    project.snapshot()


if __name__ == "__main__":
    main()
