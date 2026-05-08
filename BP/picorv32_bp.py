# picorv32_bp.py
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from siliconcompiler import ASIC, Design, StdCellLibrary
from siliconcompiler.targets import skywater130_demo

try:
    import sky130_sram_2k
except ImportError:
    from . import sky130_sram_2k

def build_top():
    design_name = 'picorv32_bp_top'
    die_w = 1200
    die_h = 1200

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
        
        # Add the SRAM blackbox Wrapper
        design.add_file('sky130_sram_2k.bb.v')
    
    # 2. Setup the Project Object
    project = ASIC(design)
    project.add_fileset(['rtl'])
    skywater130_demo(project)

    # 3. Setup SRAM Macro Library
    sram_lib = sky130_sram_2k.setup(stackup='5M1MIC')
    
    project.add_dep(sram_lib)
    project.add_asiclib(sram_lib)

    # 4. Tool Options for OpenROAD
    project.set('tool', 'openroad', 'task', 'global_route', 'var', 'grt_macro_extension', '0')
    project.set('tool', 'openroad', 'task', 'write_data', 'var', 'write_cdl', 'false')
    project.set('tool', 'openroad', 'task', 'global_placement', 'var', 'place_density', '0.5')
    project.set('tool', 'openroad', 'task', 'init_floorplan', 'var', 'ord_enable_images', 'false')
    project.set('tool', 'openroad', 'task', 'macro_placement', 'var', 'ord_enable_images', 'false')
    project.set('tool', 'openroad', 'task', 'global_placement', 'var', 'ord_enable_images', 'false')
    project.set('tool', 'openroad', 'task', 'detailed_placement', 'var', 'ord_enable_images', 'false')
    project.set('tool', 'openroad', 'task', 'global_route', 'var', 'ord_enable_images', 'false')
    project.set('tool', 'openroad', 'task', 'detailed_route', 'var', 'ord_enable_images', 'false')

    # 5. Floorplanning & Constraints
    area = project.constraint.area
    margin = 10

    area.set_diearea([(0, 0), (die_w, die_h)])
    area.set_corearea( [(margin, margin), (die_w - margin, die_h - margin)])
    area.set_density(20)

    # 6. Execute Build
    # Default to a remote SiliconCompiler run because this project is intended
    # for setups without a local OpenROAD installation.
    project.option.set_remote(True)
    project.run()
    project.summary()

if __name__ == "__main__":
    build_top()
