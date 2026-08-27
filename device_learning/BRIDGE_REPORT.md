# 强制 Null 桥报告（自动生成）

**生成时间**：2026-08-27 16:24 UTC

**策略**：无新证据前禁止将 null 桥升级为 proven_bridge

> 无新证据前禁止将 null 桥升级为 proven_bridge

| Bridge | Status | Reason |
|--------|--------|--------|
| `bitstream_frame → verilog_module` | null | 无RTL源码，位流解码未闭合 |
| `usb_command → fpga_register` | null | 无USB抓包 |
| `photo_trace → pin_constraint` | null | 无网表 |
| `iob_pin → relay_control_bit` | null | 无切换实验 |
| `frame_word → clb_netlist` | null | 帧解析未完整 |
| `cypress_firmware → usb_protocol_table` | null | 固件镜像缺失 |
| `adc_sample → usb_data_frame` | null | 无数据流抓包 |
| `relay_command → gpio_bit` | null | 无协议逆向 |
| `sample_rate_config → clock_divider` | null | 无时钟域分析 |
| `bram_init → lookup_table_function` | null | BRAM内容未解码 |

共 **10** 条强制 null 桥。

