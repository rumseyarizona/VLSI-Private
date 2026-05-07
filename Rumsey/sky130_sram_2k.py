import os

from siliconcompiler import StdCellLibrary


def setup(stackup=None):
    if stackup is None:
        raise RuntimeError("Stackup cannot be None")

    rootdir = os.path.dirname(__file__)
    lib = StdCellLibrary("sky130_sram_2k")

    lib.add_asic_pdk("skywater130")
    lib.add_asic_stackup(stackup)

    with lib.active_fileset("models.physical"):
        lib.add_file(os.path.join(rootdir, "sky130_sram_2kbyte_1rw1r_32x512_8.gds"))
        lib.add_file(os.path.join(rootdir, "sky130_sram_2kbyte_1rw1r_32x512_8.lef"))
        lib.add_asic_aprfileset()

    with lib.active_fileset("rtl"):
        lib.add_file(os.path.join(rootdir, "sky130_sram_2k.bb.v"))

    return lib
