# PicoRV32 Branch Predictor Flow

This project demonstrates an automated ASIC build flow using [SiliconCompiler](https://docs.siliconcompiler.com/) to integrate and implement a Perceptron Branch Predictor (Neural Branch History Table) inside the PicoRV32 RISC-V processor, utilizing a physical SRAM macro.

## Processor Integration Details

In this iteration, the Neural BHT predictor is fully integrated into the PicoRV32 core:
1. **Top-Level Wrapper**: `picorv32_bp_top.v` ties the PicoRV32 core together with the Neural BHT. 
2. **Instruction Fetch Monitoring**: The predictor listens directly to the PicoRV32 instruction fetches (`mem_addr`) and predicts if the current instruction branch will be taken.
3. **Execution Feedback (Training)**: Since PicoRV32 is a multi-cycle core, it generates branch reports via its trace interface when instantiated with `.ENABLE_TRACE(1)`. The top block pipes the `trace_data` back into the BHT's update ports, allowing the perceptron weights to dynamically learn and update their saturation counters across multiple execution cycles.

## Necessary Files to Run the Build

To execute the SiliconCompiler ASIC build successfully, you need the following files inside the `project/` directory:

### 1. Build Script
* `picorv32_bp.py`: The SiliconCompiler python driver running the synthesis-to-GDSII build pipeline.

### 2. RTL Source Files
* `picorv32_bp_top.v`: The top-level wrapper defining the processor + predictor integration.
* `picorv32.v`: The base RISC-V soft-core module.
* `neural_bht.v`: Synthesizable definition of the Branch History Table perceptron logic.
* `sky130_sram_2k.bb.v`: The Verilog blackbox definition for the SRAM macro so the synthesis tool (Yosys) knows its port interfaces.

### 3. Physical Macro Files (SRAM Library)
* `sky130_sram_2k.py`: A Python setup script that registers the physical layouts/macros dynamically with SiliconCompiler.
* `sky130_sram_2kbyte_1rw1r_32x512_8.lef`: The physical footprint and boundaries for OpenROAD.
* `sky130_sram_2kbyte_1rw1r_32x512_8.gds`: The layout geometry metadata of the SRAM.

## How to Run

0. **Configure Remote Execution**: The build script is configured for remote
   SiliconCompiler execution. Before running this project, configure and test
   your remote endpoint inside the same environment/container:
   ```bash
   sc-remote -configure
   sc-remote
   ```
   For the public server, use `https://server.siliconcompiler.com` and leave
   username/password blank.

1. **Execute the Build**: Run the python build script directly.
   ```bash
   python3 picorv32_bp.py
   ```
   The script uses a remote SiliconCompiler build, so a local OpenROAD install
   is not required.

2. **What happens during the build**:
   * It configures a $1200 \times 1200 \mu m$ die core area to accommodate both the CPU standard cells and the Large SRAM macro.
   * It relies on the selected SiliconCompiler target to configure tool-specific implementation steps.
   * Runs Yosys synthesis mapping the processor wrapper down to gates.
   * Runs remote physical implementation without requiring OpenROAD to be installed locally.
   * Dumps the results to `/build/picorv32_bp_top/job0/`.

3. **Viewing the Layout**:
   * To view the final GDS chip output:
     ```bash
     sc-show -design picorv32_bp_top
     ```
