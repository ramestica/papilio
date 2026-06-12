IMAGE      = xilinx-ise:14.7
BUILD      = $(shell realpath $(PWD)/../build)
LICENSE    = $(HOME)/.Xilinx

generate:
	python blinky.py
	sed -i 's|$(BUILD)/||g' $(BUILD)/top.prj
	sed -i 's|^par |par -mt 4 |' $(BUILD)/build_top.sh

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
	rm -rf $(BUILD)

.PHONY: generate synthesize build flash clean
