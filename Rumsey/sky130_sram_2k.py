from siliconcompiler import Design


class Sky130Sram2k(Design):
    def __init__(self):
        super().__init__()

        self.set_name("sky130_sram_2k")
        self.set_dataroot("local", __file__)

        with self.active_fileset("rtl"):
            with self.active_dataroot("local"):
                self.set_topmodule("sky130_sram_2kbyte_1rw1r_32x512_8")
                self.add_file("sky130_sram_2k.bb.v")

       # with self.active_fileset("lef"):
           # with self.active_dataroot("local"):
                #self.add_file("sky130_sram_2kbyte_1rw1r_32x512_8.lef")

       # with self.active_fileset("gds"):
        #    with self.active_dataroot("local"):
                #self.add_file("sky130_sram_2kbyte_1rw1r_32x512_8.gds")

       # with self.active_fileset("lib"):
        #    with self.active_dataroot("local"):
                #self.add_file("sky130_sram_2kbyte_1rw1r_32x512_8_TT_1p8V_25C.lib")
