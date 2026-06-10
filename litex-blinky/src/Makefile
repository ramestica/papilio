IMAGE      = xilinx-ise:14.7
BUILD      = $(PWD)/../build
LICENSE    = $(HOME)/.Xilinx

generate:
	python3 blinky.py
	sed -i 's|$(BUILD)/||g' $(BUILD)/top.prj
	sed -i 's|^par |par -mt 4 |' $(BUILD)/build_top.sh

synthesize:
	docker run --rm \
		-v $(BUILD):/build \
		-v $(LICENSE):/root/.Xilinx \
		$(IMAGE) \
		bash -c "source /opt/Xilinx/14.7/ISE_DS/settings64.sh && \
		         cd /build && \
		         bash build_top.sh" 2>&1 | tee $(BUILD)/build.log

report:
	@echo "<html><head><title>ISE Build Report</title>" > $(BUILD)/report.html
	@echo "<style>body{background:#1e1e1e;color:#d4d4d4;font-family:monospace;padding:2em;}" >> $(BUILD)/report.html
	@echo "pre{white-space:pre-wrap;}.err{color:#f44;}.warn{color:#fa0;}.info{color:#4af;}</style></head><body><pre>" >> $(BUILD)/report.html
	@sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g' $(BUILD)/build.log | \
		sed 's/.*ERROR.*/\<span class="err"\>&\<\/span\>/g' | \
		sed 's/.*WARNING.*/\<span class="warn"\>&\<\/span\>/g' | \
		sed 's/.*INFO.*/\<span class="info"\>&\<\/span\>/g' >> $(BUILD)/report.html
	@echo "</pre></body></html>" >> $(BUILD)/report.html
	@echo "Report: $(BUILD)/report.html"
	open $(BUILD)/report.html

build: generate synthesize report

flash:
	openFPGALoader -b papilio_pro $(BUILD)/top.bit

clean:
	rm -rf $(BUILD)

.PHONY: generate synthesize build report flash clean
