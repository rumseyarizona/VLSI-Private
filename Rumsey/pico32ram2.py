#!/usr/bin/env python3

from siliconcompiler import ASIC, Design
from siliconcompiler.targets import skywater130_demo

import sky130_sram_2k


class PicoRV32RamDesign(Design):
    def __init__(self):
        super().__init__()

        self.set_name("picorv32_top")
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

        with self.active_fileset("sdc"):
            with self.active_dataroot("local"):
                self.add_file("picorv32.sdc")


def main():
    project = ASIC()

    project.set_design(PicoRV32RamDesign())
    project.add_fileset("rtl")

    skywater130_demo(project)

    sram_lib = sky130_sram_2k.setup(stackup="5M1MIC")
    project.add_dep(sram_lib)
    project.add_asiclib(sram_lib)

    project.add_fileset("sdc")

    area = project.constraint.area
    area.set_diearea([(0, 0), (1000, 1000)])
    area.set_corearea([(50, 50), (950, 950)])
    area.set_density(20)

    project.set("tool", "openroad", "task", "global_route", "var", "grt_macro_extension", "0")
    project.set("tool", "openroad", "task", "write_data", "var", "write_cdl", "false")
    project.set("tool", "openroad", "task", "global_placement", "var", "place_density", "0.5")

    for task in (
        "init_floorplan",
        "macro_placement",
        "global_placement",
        "detailed_placement",
        "global_route",
        "detailed_route",
    ):
        project.set("tool", "openroad", "task", task, "var", "ord_enable_images", "false")

    project.set("constraint", "component", "sram", "placement", ("150", "150"))
    project.set("constraint", "component", "sram", "rotation", "R180")

    project.option.set_remote(True)

    project.run()
    project.summary()
    project.snapshot()


if __name__ == "__main__":
    main()
