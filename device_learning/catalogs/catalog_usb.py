"""USB subsystem evidence catalog — FW / DRV / PROTO layers.

登记 USB 子系统三层可辨识对象：

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
    make_entry(
        "FW-EEPROM-SYNTHETIC-FIXTURE", "FW", "eeprom",
        "Synthetic EEPROM for pipeline test only",
        "candidate", "NOT device data",
        "phase_b/fixtures/eeprom_synthetic_reference.bin",
    ),
    make_entry(
        "FW-EEPROM-LAYOUT-REF", "FW", "eeprom",
        "Public FX2LP EEPROM field layout reference",
        "candidate", "reference_only",
        "manifests/eeprom_layout_ref.json",
    ),
    make_entry(
        "FW-EEPROM-BOOT-BYTE-RULE", "FW", "eeprom",
        "Boot config byte semantics (0xC0/0xC2)",
        "candidate", "reference_only",
        "manifests/eeprom_layout_ref.json offset 0",
    ),
    make_entry(
        "FW-EEPROM-FW-OFFSET", "FW", "eeprom",
        "Typical 8051 firmware start offset 0x10 in EEPROM",
        "candidate", "reference_only",
        "manifests/eeprom_layout_ref.json",
    ),
    # ---- FW: MCU (8051-compatible core) firmware ----
    make_entry(
        "FW-MCU-CORE-IMAGE", "FW", "mcu",
        "8051-compatible microcontroller firmware image",
        "candidate", "volatile RAM extract from enum 0xA0; persistent EEPROM still missing",
        "phase_b/analysis/fx2_ram_from_enum.bin + manifests/usb_fx2_ram_extract.json",
    ),
    make_entry(
        "FW-MCU-RESET-VECTOR", "FW", "mcu",
        "Reset vector / boot entry of the MCU firmware",
        "candidate",
        "0x0000 LJMP 0x075B documented; init SFR order is candidate-level linear walk",
        "manifests/fx2_ram_scan.json + fx2_init_chain.json + fx2_ivt_map.json",
    ),
    make_entry(
        "FW-MCU-CODE-XRAM-MAP", "FW", "mcu",
        "Code / external-RAM address map of the MCU",
        "candidate",
        "16KiB volatile RAM image map + SFR/XDATA refs only; persistent EEPROM layout still unknown",
        "manifests/fx2_address_map.json + fx2_ram_xrefs.json + fx2_ivt_map.json + fx2_init_chain.json",
    ),
    make_entry(
        "FW-MCU-I2C-BOOT-PATH", "FW", "mcu",
        "MCU boot path loading from the serial EEPROM over I2C",
        "candidate", "host also does FX2 0xA0 RAM load; EEPROM role still unknown without dump",
        "usb_renumeration_timeline.json + usb_vendor_ctrl_7317.json",
    ),
    make_entry(
        "FW-MCU-RENUMERATION", "FW", "mcu",
        "USB re-numeration after FX2 RAM load: 0x7317 → 0x744f",
        "candidate", "persistent EEPROM image still missing",
        "usb_enum_decode_notes.json + usb_vendor_ctrl_7317.json (0xA0/CPUCS)",
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
    # ---- FW: EEPROM layout fields (offsets from public datasheet reference,
    #      see manifests/eeprom_layout_ref.json); values missing until a dump ----
    make_entry(
        "FW-EEPROM-BOOT-FORMAT", "FW", "eeprom",
        "EEPROM boot-format selector (boot_config_byte at offset 0x00)",
        "missing", "no_dump",
        "whether the image is identifier-only or a firmware load not read out",
    ),
    make_entry(
        "FW-EEPROM-DID-FIELD", "FW", "eeprom",
        "Device release / Device ID override word (did field at offset 0x05)",
        "missing", "no_dump",
        "DID value not dumped and not guessed",
    ),
    make_entry(
        "FW-EEPROM-FW-RECORDS", "FW", "eeprom",
        "Firmware image data records / firmware size (C2 data-record region)",
        "missing", "no_dump",
        "record layout and firmware size undetermined without a dump",
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
        "USB device descriptor VID=0x3923 PID=0x744f bcdDevice=0x0001",
        "confirmed", None,
        "usb_protocol_decode.json / usb_session.pcapng device descriptor",
    ),
    make_entry(
        "PROTO-DESC-CONFIG", "PROTO", "descriptor",
        "USB configuration descriptor: 1 interface, bmAttributes=0x80",
        "confirmed", None,
        "usb_protocol_decode.json configuration descriptor",
    ),
    make_entry(
        "PROTO-DESC-INTERFACE", "PROTO", "descriptor",
        "Interface 0 vendor-specific (0xff), 4 endpoints, alt=0",
        "confirmed", None,
        "usb_protocol_decode.json interface descriptor",
    ),
    make_entry(
        "PROTO-DESC-STRING", "PROTO", "descriptor",
        "USB string descriptors (partial; serial candidate present)",
        "candidate", "manufacturer/product strings sparse in capture",
        "usb_protocol_decode.json string_descriptors",
    ),
    # ---- PROTO: endpoint mapping ----
    make_entry(
        "PROTO-EP-MAP", "PROTO", "endpoint",
        "Endpoints: bulk 0x01 OUT, 0x81 IN, 0x06 OUT, 0x84 IN (512 B)",
        "confirmed", None,
        "usb_protocol_decode.json endpoints",
    ),
    make_entry(
        "PROTO-EP-BULK-IN", "PROTO", "endpoint",
        "Bulk IN endpoints 0x81 and 0x84, wMaxPacketSize=512",
        "confirmed", None,
        "usb_protocol_decode.json + session URB counts",
    ),
    make_entry(
        "PROTO-EP-BULK-OUT", "PROTO", "endpoint",
        "Bulk OUT endpoints 0x01 and 0x06, wMaxPacketSize=512",
        "confirmed", None,
        "usb_protocol_decode.json + session URB counts",
    ),
    make_entry(
        "PROTO-EP-INTERRUPT", "PROTO", "endpoint",
        "No interrupt endpoint in observed interface descriptor",
        "candidate", "only 4 bulk endpoints listed",
        "usb_protocol_decode.json",
    ),
    make_entry(
        "PROTO-EP-ALT-SETTINGS", "PROTO", "endpoint",
        "Only bAlternateSetting=0 observed",
        "candidate", "other alt-settings not seen in capture",
        "usb_protocol_decode.json",
    ),
    make_entry(
        "PROTO-XFER-MODE", "PROTO", "transfer",
        "Acquisition stream uses bulk transfers (not isochronous)",
        "confirmed", None,
        "usb_protocol_decode.json transfer_mode + session traffic",
    ),
    make_entry(
        "PROTO-CTRL-VENDOR-REQ", "PROTO", "control",
        "Vendor-specific control-request surface",
        "candidate", "primary has no vendor ctrl; companion FX2 0xA0/A4/A5/B0 tabulated",
        "usb_primary_ctrl_744f.json + usb_vendor_ctrl_7317.json",
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
        "candidate", "FX2-style RAM load observed (0xA0/CPUCS) before renumeration",
        "usb_vendor_ctrl_7317.json + usb_enum_decode_notes.json (0x7317→0x744f)",
    ),
    make_entry(
        "DRV-PIPE-EP-BIND", "DRV", "driver",
        "Driver pipe-to-endpoint binding",
        "candidate", "cmd plane EP01/81; data plane EP06/84 from session",
        "usb_protocol_decode.json + usb_data_plane_hypothesis.json + usb_command_taxonomy.json",
    ),
]
