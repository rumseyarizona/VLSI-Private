# picorv32_bp.py
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from siliconcompiler import ASIC, Design
from siliconcompiler.targets import skywater130_demo

def build_top():
    design_name = 'picorv32_bp_top'
    die_w = 1200
    die_h = 1200
    use_sram_macro = os.getenv("USE_SRAM_MACRO", "false").lower() in ("1", "true", "yes")

    # 1. Setup the Design Object
    design = Design(design_name)
    design.set_dataroot('local', __file__)
    
    with design.active_dataroot('local'), design.active_fileset('rtl'):
        design.set_topmodule(design_name)

        # The Top-level wrapper integrating CPU and Predictor
        design.add_file('picorv32_bp_top.v')

        # The PicoRV32 processor core
        design.add_file('picorv32.v')

        # We inject our Verilog translation of the Scala NeuralBHT branch predictor
        design.add_file('neural_bht.v')
        
        if use_sram_macro:
            # Add the SRAM blackbox wrapper when using the physical macro path.
            design.add_define('USE_SRAM_MACRO')
            design.add_file('sky130_sram_2k.bb.v')

    with design.active_dataroot('local'), design.active_fileset('sdc'):
        design.add_file('picorv32.sdc')
    
    # 2. Setup the Project Object
    project = ASIC(design)
    project.add_fileset(['rtl', 'sdc'])
    skywater130_demo(project)

    # 3. Optional SRAM Macro Library
    # The default remote path uses synthesizable predictor storage. Enable this
    # only in an environment known to support user-provided SRAM LEF/GDS macros.
    if use_sram_macro:
        try:
            import sky130_sram_2k
        except ImportError:
            from . import sky130_sram_2k

        sram_lib = sky130_sram_2k.setup(stackup='5M1MIC')
        project.add_dep(sram_lib)
        project.add_asiclib(sram_lib)

    # 4. Floorplanning & Constraints
    area = project.constraint.area
    margin = 10

    area.set_diearea([(0, 0), (die_w, die_h)])
    area.set_corearea( [(margin, margin), (die_w - margin, die_h - margin)])
    area.set_density(20)

    # 5. Execute Build
    # Default to a remote SiliconCompiler run because this project is intended
    # for setups without a local OpenROAD installation.
    project.option.set_remote(True)
    project.run()
    project.summary()
    project.show()

if __name__ == "__main__":
    build_top()
