"""Signal-layer (SIG) evidence catalog.

登记被测采集板模拟/信号链上的可辨识环节，路径大致为
输入接口 → 保护/耦合（含继电器）→ 衰减/放大 → 抗混叠 → ADC → 数字侧接口。

证据来源仅限 ``hardware/photos/`` 的板卡照片与其它层的间接推断，
没有任何示波/探针/在线测量。因此：

- ``candidate``   : 由硬件层器件间接推断存在（but 未探针验证）。
- ``unknown``     : 需要测量/数据手册才能确定的电气参数或连接关系。
- ``not_started`` : 需跨层（FW/PROTO）证据才能连通，尚未开始。

不推断信号流公式、不假设 ADC 位宽/采样率、不把“照片可见”当作“电气已验证”。
"""
from catalogs import make_entry

LAYER = "signal"


def _e(identifier, module, description, status, boundary, evidence):
    return make_entry(identifier, LAYER, module, description, status, boundary, evidence)


ENTRIES = [
    _e(
        "SIG-USB-DIFF-PAIR",
        "usb",
        "USB differential data pair between the connector and the FPGA",
        "candidate",
        "no_capture",
        "implied by HW-USB-CONNECTOR + HW-FPGA-PACKAGE; not probed",
    ),
    _e(
        "SIG-REF-CLOCK",
        "clock",
        "Reference clock distributed from the on-board oscillator to the FPGA",
        "candidate",
        "no_capture",
        "implied by HW-CLOCK-OSC; frequency not measured",
    ),
    _e(
        "SIG-CONFIG-BOOT",
        "config",
        "FPGA configuration/boot lines from the config memory",
        "candidate",
        "no_capture",
        "implied by HW-CONFIG-FLASH + BIT-DESIGN-NAME; not probed",
    ),
    _e(
        "SIG-ACQ-CHANNEL",
        "frontend",
        "Acquisition channel from the analog front-end into the fabric",
        "unknown",
        "no_capture",
        "front-end chain not traced; no waveform captured",
    ),
    _e(
        "SIG-POWER-RAILS",
        "power",
        "Core / I/O rail voltages presented to the FPGA",
        "unknown",
        "no_measurement",
        "regulators visible but rail voltages not measured",
    ),
    _e(
        "SIG-PROTOCOL-FRAMING",
        "usb",
        "Application-level framing carried over the USB link",
        "unknown",
        "no_capture",
        "no bus trace; framing not observed",
    ),
    _e(
        "SIG-INPUT-CONNECTOR",
        "input",
        "Analog input interface / connector at the board edge",
        "candidate",
        "photo_only",
        "implied by HW-ANALOG-FRONTEND; connector type/impedance not read",
    ),
    _e(
        "SIG-INPUT-PROTECTION",
        "input",
        "Input over-voltage protection / clamp on the front-end",
        "unknown",
        "no_measurement",
        "protection devices and clamp level not confirmed from photos",
    ),
    _e(
        "SIG-COUPLING-MODE",
        "coupling",
        "Input coupling selection (AC / DC) ahead of the gain stage",
        "unknown",
        "no_measurement",
        "AC/DC switch and DC-block capacitor not located",
    ),
    _e(
        "SIG-COUPLING-RELAY",
        "coupling",
        "Relay switching input coupling / range in the signal path",
        "unknown",
        "no_measurement",
        "relay presence not confirmed in hw catalog; type/contacts unknown",
    ),
    _e(
        "SIG-RELAY-DRIVE",
        "coupling",
        "Control/drive line that actuates the signal-path relay",
        "unknown",
        "no_measurement",
        "drive source (MCU/FPGA/latch) and level not traced",
    ),
    _e(
        "SIG-ATTENUATOR",
        "gain",
        "Input attenuator / divider setting the measurement range",
        "unknown",
        "no_measurement",
        "division ratio and range steps not confirmed",
    ),
    _e(
        "SIG-PREAMP-GAIN",
        "gain",
        "Front-end amplifier / buffer (possibly programmable-gain) stage",
        "unknown",
        "no_measurement",
        "amplifier part, gain and bandwidth not read from photos",
    ),
    _e(
        "SIG-ANTIALIAS-FILTER",
        "filter",
        "Anti-alias low-pass filter ahead of the ADC",
        "unknown",
        "no_measurement",
        "cutoff frequency, order and topology not confirmed",
    ),
    _e(
        "SIG-ADC-INTERFACE",
        "adc",
        "ADC device and its digital data interface into the fabric",
        "unknown",
        "no_measurement",
        "ADC part and bus form (parallel/LVDS/serial) not confirmed",
    ),
    _e(
        "SIG-ADC-RESOLUTION",
        "adc",
        "Sampling bit width / resolution of the ADC",
        "unknown",
        "no_datasheet",
        "resolution (8/12/14/16-bit?) has no supporting evidence",
    ),
    _e(
        "SIG-ADC-SAMPLE-RATE",
        "adc",
        "ADC sampling rate as configured on the board",
        "unknown",
        "no_datasheet",
        "max and configured sample rate unknown",
    ),
    _e(
        "SIG-ADC-REFERENCE",
        "adc",
        "ADC voltage reference source",
        "unknown",
        "no_measurement",
        "reference value and source device not identified",
    ),
    _e(
        "SIG-ADC-TO-INTERFACE",
        "path",
        "Data path from ADC through the fabric out to the host interface",
        "not_started",
        "cross_layer",
        "requires FW/PROTO evidence (see catalog_usb) to connect end-to-end",
    ),
]
