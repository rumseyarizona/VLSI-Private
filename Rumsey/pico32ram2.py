#!/usr/bin/env python3

import platform
import sys
import traceback
from pathlib import Path

import siliconcompiler
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
    rootdir = Path(__file__).resolve().parent
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"SiliconCompiler: {siliconcompiler.__version__}")
    print(f"Script directory: {rootdir}")

    required_files = [
        "picorv32.v",
        "picorv32_top2.v",
        "picorv32.sdc",
        "sky130_sram_2k.bb.v",
        "sky130_sram_2kbyte_1rw1r_32x512_8.gds",
        "sky130_sram_2kbyte_1rw1r_32x512_8.lef",
    ]
    missing_files = [name for name in required_files if not (rootdir / name).is_file()]
    if missing_files:
        raise FileNotFoundError(f"Missing required input files: {', '.join(missing_files)}")
    print("Required file preflight passed")

    design = PicoRV32RamDesign()
    if not design.check_filepaths():
        raise RuntimeError("SiliconCompiler design file path check failed")
    print("Design file path check passed")

    project = ASIC()

    project.set_design(design)
    project.add_fileset(["rtl", "sdc"])

    skywater130_demo(project)

    sram_lib = sky130_sram_2k.setup(stackup="5M1MIC")
    project.add_dep(sram_lib)
    project.add_asiclib(sram_lib)

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
    print("Starting SiliconCompiler remote run")

    project.run()
    project.summary()
    project.snapshot()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        error_path = Path(__file__).resolve().parent / "preflight_error.txt"
        error_text = traceback.format_exc()
        error_path.write_text(error_text)
        print(error_text, file=sys.stderr)
        print(f"Wrote exception details to {error_path}", file=sys.stderr)
        raise
