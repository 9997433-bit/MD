"""USB subsystem evidence catalog — FW / DRV / PROTO layers.

登记被测采集板 USB 子系统三层可辨识对象：

- ``FW``    固件层：MCU（8051 兼容核）固件、串行 EEPROM 引导镜像、FPGA 位流的存在性与边界。
- ``PROTO`` 协议层：USB 描述符、端点映射、控制/批量传输面。
- ``DRV``   驱动层：主机侧驱动模块、绑定关系、固件加载器。

诚实登记原则——凡无转储/反汇编/抓包证据者，按缺失程度标注，绝不猜测数值：

- ``missing``      : 应存在但**尚无任何镜像/转储**可分析（8051 固件、EEPROM）。
- ``not_started``  : 有明确分析方法但**尚未开始**（描述符解析、驱动逆向）。
- ``unknown``      : 结构应存在但**具体取值/映射无证据**（端点号、传输类型）。
- ``candidate``    : 器件/文件存在可见，但内容仍不透明（如 FPGA 位流）。

不编造 VID/PID、不假设端点号与方向、不推断 IOCTL 编号、不把“文件存在”当作“内容已理解”。
"""
from catalogs import make_entry

ENTRIES = [
    # ---- FW: MCU (8051-compatible core) firmware ----
    make_entry(
        "FW-MCU-CORE-IMAGE", "FW", "mcu",
        "8051-compatible microcontroller firmware image",
        "missing", "no_dump",
        "no firmware binary dumped; nothing to disassemble",
    ),
    make_entry(
        "FW-MCU-RESET-VECTOR", "FW", "mcu",
        "Reset vector / boot entry of the MCU firmware",
        "missing", "no_dump",
        "no image available; entry address undetermined",
    ),
    make_entry(
        "FW-MCU-CODE-XRAM-MAP", "FW", "mcu",
        "Code / external-RAM address map of the MCU",
        "missing", "no_dump",
        "memory layout and XRAM mapping unknown without a dump",
    ),
    make_entry(
        "FW-MCU-I2C-BOOT-PATH", "FW", "mcu",
        "MCU boot path loading from the serial EEPROM over I2C",
        "missing", "no_dump",
        "boot decision and load flow have no evidence",
    ),
    make_entry(
        "FW-MCU-RENUMERATION", "FW", "mcu",
        "USB re-numeration behaviour after firmware load",
        "missing", "no_dump",
        "whether/when the device re-enumerates is unknown",
    ),
    # ---- FW: serial EEPROM boot image ----
    make_entry(
        "FW-EEPROM-IMAGE", "FW", "eeprom",
        "Serial EEPROM contents image",
        "missing", "no_dump",
        "EEPROM not dumped; contents entirely unknown",
    ),
    make_entry(
        "FW-EEPROM-CONFIG-BYTE", "FW", "eeprom",
        "EEPROM leading boot-configuration byte",
        "missing", "no_dump",
        "boot-mode configuration byte not read out",
    ),
    make_entry(
        "FW-EEPROM-VIDPID", "FW", "eeprom",
        "VID/PID fields possibly stored in the EEPROM",
        "missing", "no_dump",
        "identifier values not dumped and not guessed",
    ),
    make_entry(
        "FW-EEPROM-DESC-OVERRIDE", "FW", "eeprom",
        "Descriptor-override data possibly held in the EEPROM",
        "missing", "no_dump",
        "presence of custom descriptors unknown",
    ),
    # ---- FW: FPGA bitstream ----
    make_entry(
        "FW-FPGA-BITSTREAM", "FW", "fpga",
        "FPGA bitstream file (firmware/device.bit)",
        "candidate", "opaque_binary",
        "file present (see catalog_bit); payload not reversed",
    ),
    make_entry(
        "FW-FPGA-CONFIG-IFACE", "FW", "fpga",
        "FPGA configuration interface / load source",
        "unknown", "no_dump",
        "configured by MCU or flash not confirmed",
    ),
    # ---- PROTO: USB descriptors ----
    make_entry(
        "PROTO-DESC-DEVICE", "PROTO", "descriptor",
        "USB device descriptor",
        "not_started", "no_capture",
        "enumeration not captured; fields unparsed",
    ),
    make_entry(
        "PROTO-DESC-CONFIG", "PROTO", "descriptor",
        "USB configuration descriptor",
        "not_started", "no_capture",
        "power/interface counts unparsed",
    ),
    make_entry(
        "PROTO-DESC-INTERFACE", "PROTO", "descriptor",
        "USB interface descriptor",
        "not_started", "no_capture",
        "class/subclass/protocol fields unparsed",
    ),
    make_entry(
        "PROTO-DESC-STRING", "PROTO", "descriptor",
        "USB string descriptors",
        "not_started", "no_capture",
        "vendor/product strings not read",
    ),
    # ---- PROTO: endpoint mapping ----
    make_entry(
        "PROTO-EP-MAP", "PROTO", "endpoint",
        "Overall endpoint map",
        "unknown", "no_capture",
        "endpoint count/direction/type have no evidence",
    ),
    make_entry(
        "PROTO-EP-BULK-IN", "PROTO", "endpoint",
        "Bulk IN endpoint (data upstream to host)",
        "unknown", "no_capture",
        "endpoint number and max packet size unknown",
    ),
    make_entry(
        "PROTO-EP-BULK-OUT", "PROTO", "endpoint",
        "Bulk OUT endpoint (commands downstream)",
        "unknown", "no_capture",
        "endpoint number and purpose not confirmed",
    ),
    make_entry(
        "PROTO-EP-INTERRUPT", "PROTO", "endpoint",
        "Interrupt endpoint (status / events)",
        "unknown", "no_capture",
        "existence of an interrupt endpoint unknown",
    ),
    make_entry(
        "PROTO-EP-ALT-SETTINGS", "PROTO", "endpoint",
        "Interface alternate settings",
        "unknown", "no_capture",
        "bandwidth/endpoint changes per alt-setting unknown",
    ),
    make_entry(
        "PROTO-XFER-MODE", "PROTO", "transfer",
        "Data transfer mode for the acquisition stream (bulk vs isochronous)",
        "unknown", "no_capture",
        "whether the stream uses bulk or isochronous not confirmed",
    ),
    make_entry(
        "PROTO-CTRL-VENDOR-REQ", "PROTO", "control",
        "Vendor-specific control-request surface",
        "not_started", "no_capture",
        "bRequest/wValue semantics unparsed",
    ),
    # ---- DRV: host-side driver ----
    make_entry(
        "DRV-HOST-MODULE", "DRV", "driver",
        "Host-side USB driver module",
        "not_started", "no_binary",
        "driver binary not obtained; not reversed",
    ),
    make_entry(
        "DRV-INF-BINDING", "DRV", "driver",
        "Driver INF binding (VID/PID match)",
        "not_started", "no_binary",
        "match ids and install info not obtained",
    ),
    make_entry(
        "DRV-IOCTL-SURFACE", "DRV", "driver",
        "Driver IOCTL interface surface",
        "not_started", "no_binary",
        "IOCTL codes and structures not reversed",
    ),
    make_entry(
        "DRV-FIRMWARE-LOADER", "DRV", "driver",
        "Host-side firmware downloader",
        "not_started", "no_binary",
        "whether firmware is downloaded at attach, and its format, unknown",
    ),
    make_entry(
        "DRV-PIPE-EP-BIND", "DRV", "driver",
        "Driver pipe-to-endpoint binding",
        "unknown", "cross_layer",
        "depends on PROTO endpoint map; no evidence yet",
    ),
]
