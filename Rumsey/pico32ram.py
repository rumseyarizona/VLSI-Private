#!/usr/bin/env python3

from siliconcompiler import ASIC, Design
from siliconcompiler.targets import skywater130_demo

from sky130_sram_2k import Sky130Sram2k


class PicoRV32RamDesign(Design):
    def __init__(self):
        super().__init__()

        self.set_name("picorv32_ram")
        self.set_dataroot("local", __file__)

        with self.active_fileset("rtl"):
            with self.active_dataroot("local"):
                self.set_topmodule("picorv32_top")

                # PicoRV32 core
                self.add_file("picorv32.v")

                # Top wrapper: instantiates PicoRV32 + SRAM
                self.add_file("picorv32_top2.v")

                # SRAM blackbox
                self.add_file("sky130_sram_2k.bb.v")

                # SRAM macro library description
                self.add_depfileset(Sky130Sram2k(), "rtl")
                #self.add_depfileset(Sky130Sram2k(), "lef")
                #self.add_depfileset(Sky130Sram2k(), "gds")
                #self.add_depfileset(Sky130Sram2k(), "lib")


def main():
    project = ASIC()

    project.set_design(PicoRV32RamDesign())
    project.add_fileset("rtl")

    skywater130_demo(project)
    area = project.constraint.area
    area.set_diearea([("0", "0"), ("1000", "1000")])
    area.set_corearea([("50","50"), ("950", "950")])
    area.set_density(20)

    project.option.set_remote(True)

    project.run()
    project.summary()
    project.snapshot()


if __name__ == "__main__":
    main()
