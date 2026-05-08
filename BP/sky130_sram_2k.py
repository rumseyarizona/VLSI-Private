'''
import os
from siliconcompiler import StdCellLibrary 

def setup(stackup=None):
    design = 'sky130_sram_2k'

    if stackup is None:
        raise RuntimeError("Stackup cannot be None")

    lib = StdCellLibrary(design)
    
    # 1. Register the Dataroot 
    lib.set_dataroot(
        name='vlsida',
        path='git+https://github.com/VLSIDA/sky130_sram_macros',
        tag='c2333394e0b0b9d9d71185678a8d8087715d5e3b'
    )
    
    # 2. Attach Physical Views using active_fileset (SC 0.37+ API)
    with lib.active_dataroot('vlsida'):
        with lib.active_fileset('models.physical'):
            lib.add_file('sky130_sram_2kbyte_1rw1r_32x512_8.gds')
            lib.add_file('sky130_sram_2kbyte_1rw1r_32x512_8.lef')
            
            # Helper function to automatically map these physical files to the APR tools
            lib.add_asic_aprfileset()
            
    # 3. Add the local blackbox Verilog to the RTL fileset
    rootdir = os.path.dirname(__file__)
    with lib.active_fileset('rtl'):
        lib.add_file(os.path.join(rootdir, 'sky130_sram_2k.bb.v'))

    return lib
'''

import os
from siliconcompiler import StdCellLibrary 

def setup(stackup=None):
    design = 'sky130_sram_2k'

    if stackup is None:
        raise RuntimeError("Stackup cannot be None")

    lib = StdCellLibrary(design)
    
    # CRITICAL FIX: Tell SC this macro belongs to skywater130 and the current stackup!
    lib.add_asic_pdk('skywater130')
    lib.add_asic_stackup(stackup)
    
    # lib.set_dataroot(
    #     name='vlsida',
    #     path='git+https://github.com/VLSIDA/sky130_sram_macros',
    #     tag='c2333394e0b0b9d9d71185678a8d8087715d5e3b'
    # )
    
    rootdir = os.path.dirname(__file__)
    
    # Attach Physical Views
    with lib.active_fileset('models.physical'):
        lib.add_file(os.path.join(rootdir, 'sky130_sram_2kbyte_1rw1r_32x512_8.gds'))
        lib.add_file(os.path.join(rootdir, 'sky130_sram_2kbyte_1rw1r_32x512_8.lef'))
        
        # This will now successfully map the files because the stackup is defined
        lib.add_asic_aprfileset()
            
    # Add the local blackbox Verilog
    with lib.active_fileset('rtl'):
        lib.add_file(os.path.join(rootdir, 'sky130_sram_2k.bb.v'))
        
    return lib