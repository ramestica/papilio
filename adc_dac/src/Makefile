IMAGE   = xilinx-ise:14.7
BUILD   = $(PWD)/../build
SRC     = $(PWD)
LICENSE = $(HOME)/.Xilinx

generate:
	cd $(SRC) && python3 top.py

synthesize:
	docker run --rm \
		-v $(BUILD):/build \
		-v $(LICENSE):/root/.Xilinx \
		$(IMAGE) \
		bash -c "source /opt/Xilinx/14.7/ISE_DS/settings64.sh && \
		         cd /build && \
		         bash build_top.sh"

build: generate synthesize

flash:
	openFPGALoader -c ft2232 $(BUILD)/top.bit

clean:
	rm -rf $(BUILD)/

.PHONY: generate synthesize build flash clean
