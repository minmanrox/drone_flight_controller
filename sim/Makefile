# sim/Makefile

TOPLEVEL_LANG ?= verilog
TOPLEVEL      ?= top_module
SIM           ?= verilator

VERILOG_SOURCES = \
  ../rtl/top_module.v

INCLUDE_DIRS = \
  -I../rtl

MODULE ?= test_top,test_pwm_to_mix

BUILD_DIR := sim_build

.PHONY: sim
sim: $(BUILD_DIR)
	verilator -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC --cc --trace --timing\
	  --top-module $(TOPLEVEL) \
	  $(INCLUDE_DIRS) \
	  $(VERILOG_SOURCES) \
	  -Mdir $(BUILD_DIR)
	$(MAKE) -C $(BUILD_DIR) -f V$(TOPLEVEL).mk
	$(BUILD_DIR)/V$(TOPLEVEL)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Cocotb target using Verilator
EXTRA_ARGS = $(INCLUDE_DIRS) --timing -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC

.PHONY: cocotb
cocotb: $(BUILD_DIR)
	$(MAKE) -f $(shell cocotb-config --makefiles)/Makefile.sim \
		SIM=$(SIM) \
		TOPLEVEL=$(TOPLEVEL) \
		TOPLEVEL_LANG=$(TOPLEVEL_LANG) \
		COCOTB_TEST_MODULES=$(MODULE) \
		VERILOG_SOURCES="$(VERILOG_SOURCES)" \
		EXTRA_ARGS="$(EXTRA_ARGS)" \
		COCOTB_RESULTS_FILE=$(BUILD_DIR)/results.xml

clean:
	rm -rf $(BUILD_DIR) __pycache__
