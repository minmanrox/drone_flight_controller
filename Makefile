# Makefile at repo root

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make sim      - run HDL simulation"
	@echo "  make cocotb   - run cocotb tests (when ready)"
	@echo "  make fpga     - synthesize + P&R for ULX3S"
	@echo "  make prog     - program ULX3S"
	@echo "  make clean    - clean build artifacts"

.PHONY: sim
sim:
	$(MAKE) -C sim sim

.PHONY: cocotb
cocotb:
	$(MAKE) -C sim cocotb

.PHONY: fpga
fpga:
	bash fpga/ulx3s_build.sh

.PHONY: prog
prog:
	# Pick your programmer, e.g. fujprog or ecpprog
	fujprog fpga/build/top.bit

.PHONY: clean
clean:
	$(MAKE) -C sim clean || true
	rm -rf fpga/build

