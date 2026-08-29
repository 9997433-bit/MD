# Firebolt Identifier Index
> **停止条件**：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。
生成自 EvidenceLedger（71 条）。

## spec

| identifier | status | boundary | 一句话 |
|---|---|---|---|
| `SPEC-PRODUCT-USB-6453` | confirmed | spec_and_usb_pid | 32 SE / 16 DIFF AI, 4 AO, 16 DIO; community maps PID 0x7B44 to Firebolt |
| `SPEC-ADC-16` | confirmed | spec_sheet | Number of ADC = 16 |
| `SPEC-SIM-MAX-16CH` | confirmed | spec_sheet | Simultaneous sampling channels: up to 16 |
| `SPEC-SIM-1MS` | confirmed | spec_sheet | All 16 DIFF or up to 16 SE at 1 MS/s/ch |
| `SPEC-SE-PAIR` | confirmed | spec_sheet | e.g. AI0&AI8, AI1&AI9 on the same converter |
| `SPEC-BANK` | confirmed | spec_sheet | AI0:7 then AI8:15; gap via AIConv.Rate |
| `SPEC-AICONV-RATE` | confirmed | spec_sheet | Software property name only; device register unknown |
| `SPEC-TIMING-RES` | confirmed | spec_sheet | Sample clock timebase quality |
| `SPEC-FIFO-AI` | confirmed | spec_sheet | Shared depth, not per-channel dedicated |
| `SPEC-XFER-STREAM` | confirmed | spec_sheet | Also lists programmed I/O; stream is primary high-rate path |
| `SPEC-PFI-TRIG` | confirmed | spec_sheet | PFI0:15 multifunctional with DIO |
| `SPEC-SYNC-LAYER` | confirmed | spec_derived | Not host-side software alignment; follows from 16-ADC simultaneous model |
| `SPEC-AO-4CH` | confirmed | spec_sheet | Registered for system_map completeness; low priority for sync learning |
| `SPEC-DIO-16` | confirmed | spec_sheet | Port0/line0:15 |
| `SPEC-FIFO-SHARED-DEPTH` | confirmed | spec_sheet | 8191-sample FIFO is a single shared pool; ~8191/n samples per channel when n cha |
| `SPEC-DIFF-16` | confirmed | spec_sheet | DIFF mode pairs AIn with AIn+8 terminals; 16 DIFF channels map 1:1 onto the 16 A |
| `SPEC-RANGE-LIST` | confirmed | spec_sheet | Per-channel programmable input range up to +/-10 V full scale; exact range list  |
| `SPEC-MIN-RATE-NONE` | confirmed | spec_sheet | Spec lists maximum rates only; low-rate operation bounded by timebase/divider, n |
| `SPEC-OEM-VARIANT` | confirmed | spec_sheet | OEM variant shares the same AI/sync spec; differences are enclosure/connector le |

## hardware

| identifier | status | boundary | 一句话 |
|---|---|---|---|
| `HW-BRAND-NI` | confirmed | photo_silkscreen | NI logo / ni.com/patents / © 2024 on teardown photos |
| `HW-USB-C` | confirmed | photo | Visible on board edge |
| `HW-FX3-CYUSB3014` | confirmed | photo_marking | Matches firmware ThreadX ARM9 / FX3 strings |
| `HW-FPGA-ARTIX7` | confirmed | photo_and_bitstream | Photo marking + IDCODE XC7A100T |
| `HW-FPGA-XC7A100T` | confirmed | bitstream_idcode | IDCODE 0x0362C093; some photo OCR may say 50T — binary wins |
| `HW-ASSY-114365F` | candidate | photo_label | Multiple sticker variants across photos |
| `HW-OEM-S2C` | candidate | photo | Consistent with USB-6453 OEM 50-pin style interconnect |
| `HW-ADC-ARRAY` | candidate | photo_layout | Supports 16-ADC architecture; MPN not confirmed |
| `HW-ADC-MPN` | unknown | needs_photo_or_bom | See OMISSIONS |
| `HW-SYNC-LOCUS` | confirmed | spec_plus_arch | FX3 lacks sample/sync strings; SPEC requires shared convert clock |

## fx3

| identifier | status | boundary | 一句话 |
|---|---|---|---|
| `FX3-IMG-CY-MAGIC` | confirmed | firmware_bytes | niusbFirebolt.cfg offset 0: 43 59 1c b0 |
| `FX3-USB-VIDPID` | confirmed | firmware_device_descriptor | Matches Firebolt / USB-6453 community reports |
| `FX3-RTOS-THREADX` | confirmed | firmware_string | Express Logic copyright string |
| `FX3-SRC-NIMARENGO` | confirmed | firmware_string | Marengo platform naming |
| `FX3-FPGA-LOAD` | confirmed | firmware_string | Role: configuration agent |
| `FX3-FPGA-REGACC` | confirmed | firmware_string | Register map body unknown without RE/capture |
| `FX3-FUSION` | confirmed | firmware_string | tFusionManager / tFusionVendorDeviceRequest.h |
| `FX3-DMA` | confirmed | firmware_string | 01_DMA_THREAD / 03_PIB_THREAD / tDMAManager.c |
| `FX3-STATE-MACHINE` | hypothesis | firmware_string | May be device/USB state, not AI sample FSM |
| `FX3-COUNTER-MON` | candidate | firmware_string | Likely ties to 4 counters; not proven as AI clock |
| `FX3-REGMAP` | unknown | needs_ghidra_or_capture | OMISSIONS |
| `FX3-FUSION-REQ` | unknown | needs_usb_capture | Explicitly deferred this phase |
| `FX3-ROLE-SUMMARY` | confirmed | arch_synthesis | Synthesized from strings + SPEC sync layer |
| `FX3-USB-IF-VENDOR` | confirmed | firmware_config_descriptor | fx3_static_re.json; aligns with Fusion control plane |
| `FX3-USB-EP-TOPOLOGY` | confirmed | firmware_config_descriptor | Many bulk EPs consistent with multi-stream DMA / Signal Stream hypothesis |
| `FX3-USB-DESC-USB2-VIEW` | confirmed | firmware_config_descriptor | Do not deny product USB-C/SS; only asserts what this .cfg embeds |
| `FX3-LOAD-BASE-SYSMEM` | candidate | pointer_heuristic | tFPGARegisterAccess.c file 0x4624C -> VA 0x4001C24C; aids future Ghidra load |
| `FX3-UIB-BASE` | confirmed | firmware_mmio_literals | Highest-frequency E00* immediates; USB engine |
| `FX3-GCTL-BASE` | confirmed | firmware_mmio_literals | Clock/power/id controller region |
| `FX3-PIB-BASE` | confirmed | firmware_mmio_literals | On-chip bridge toward FPGA GPIF-II |
| `FX3-PIB-SOCKET-STRIDE` | confirmed | arm_disassembly | VA 0x400115F8: r3=0xE0010000+(index<<4); see fx3_mmio_map.json |
| `FX3-GPIF-FPGA-BRIDGE` | confirmed | arch_synthesis | Reinforces FX3-ROLE-SUMMARY; fabric regmap still unknown |
| `FX3-PIB-CFG-BASE` | confirmed | arm_disassembly | Init func VA 0x4001250C literal; see fx3_regaccess_shape.json |
| `FX3-PIB-CFG-STORES` | confirmed | arm_disassembly | Engine/socket setup — not fabric AIConv map |
| `FX3-SUBSYSTEM-TAGS` | candidate | firmware_string_table | Possible log/state enums; not proven AI sample FSM |
| `FX3-GPIF-CFG-OBJECT` | candidate | arm_disassembly | Descriptor/walker — not channel sample table |
| `FX3-ACCESS-PATH-SHAPE` | confirmed | arch_synthesis | Does not include fabric regmap or Fusion field dictionary |

## bitstream

| identifier | status | boundary | 一句话 |
|---|---|---|---|
| `BIT-FMT-BIN` | confirmed | firmware_bytes | No Xilinx .bit ASCII header |
| `BIT-SYNC-WORD` | confirmed | firmware_bytes | 7-series bitstream |
| `BIT-IDCODE` | confirmed | bitstream_packet | Type1 write IDCODE |
| `BIT-COMPRESSED` | candidate | size_heuristic | Uncompressed 7A100T ~3.8 MiB typical |
| `BIT-SYNC-CLOCK-TREE` | unknown | needs_netlist | OMISSIONS — sync logic locus asserted by SPEC+arch only |
| `BIT-BANK-AICONV` | unknown | needs_netlist_or_lab | OMISSIONS |
| `BIT-FIFO-LOGIC` | unknown | needs_netlist | SPEC gives 8191 samples; HDL unknown |

## learn

| identifier | status | boundary | 一句话 |
|---|---|---|---|
| `LEARN-Q1-SYNC-LAYER` | confirmed | checklist | Answer keyed to SPEC-SYNC-LAYER + HW-SYNC-LOCUS |
| `LEARN-Q2-16-VS-32` | confirmed | checklist | SPEC-SIM-* / SPEC-SE-PAIR / SPEC-BANK |
| `LEARN-Q3-CLOCK-TRIG-AICONV` | confirmed | checklist | SPEC timing + PFI + AIConv |
| `LEARN-Q4-FX3-VS-FPGA` | confirmed | checklist | FX3-ROLE-SUMMARY vs BIT unknowns |
| `LEARN-Q5-FRAME-PACK` | confirmed | checklist | Must not over-claim; see forced null bridges |
| `LEARN-Q6-UPGRADE-PATH` | confirmed | checklist | OMISSIONS_AND_REMAINING.md |
| `LEARN-NO-VENDOR-EQ` | confirmed | policy | README declaration |
| `LEARN-NO-CAPTURE-YET` | confirmed | policy | PHASE_PLAN deferred list |

## by_status

| status | count |
|---|---|
| candidate | 8 |
| confirmed | 56 |
| hypothesis | 1 |
| unknown | 6 |
