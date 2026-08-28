# 等待实物（STOP）

> 更新：2026-08-28（S1–S11 后）  
> **只做** `20230825_s2056.mcs` / zero0000。**不做 4431。**

## 静态阶段结论

在现有 mcs + 7 张照片条件下，**静态收窄已耗尽**。  
重复发送「继续」**不会**再产生新的实质分析。

## 下一动作（任选一条，带具体信息）

1. `有实物：输入电压=___V；有/无 JTAG；有/无示波器` → 启动 L4/L5 Day-1  
2. `新照片：` + U12/U13/U16 微距侧光 或 RTL8211 顶标  
3. `新固件/原理图：` + 链接  

## 已备好（有实物即可执行）

| 项 | 位置 |
|----|------|
| Flash 备份 SOP | `02_firmware/SOP_*.md` |
| L4 USB/ETH | `04_comms/` + `scripts/ft600_scaffold.py` `udp_probe.py` |
| SPI 靶标 | `03_architecture/FMC150_SPI靶标检查表.md` |
| L5 FFT 检查 | `scripts/l5_fft_check.py` |
| 电源安全 | `01_hardware/电源树.md`（TPS53515 / TPS74401） |

## 入口

- 范围：`00_meta/课题范围边界.md`  
- 仪表盘：`进度仪表盘.md`  
- PR：https://github.com/9997433-bit/MD/pull/14  
