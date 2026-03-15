#!/usr/bin/env bash
set -e

BOARD_OPTS="--45k --package CABGA381"  # change to --12k/--85k if needed

mkdir -p fpga/build

# 1. Synthesis
yosys -ql fpga/build/yosys.log fpga/yosys_ecp5.ys

# 2. Place & route
nextpnr-ecp5 \
  ${BOARD_OPTS} \
  --json fpga/build/top.json \
  --lpf fpga/ulx3s.lpf \
  --freq 25 \
  --report fpga/build/timing.json \
  --textcfg fpga/build/top.config

# 3. Bitstream pack
ecppack fpga/build/top.config fpga/build/top.bit

echo "Bitstream: fpga/build/top.bit"

