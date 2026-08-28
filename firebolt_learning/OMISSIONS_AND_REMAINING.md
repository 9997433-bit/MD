# 省略项与剩余工作

> 静态骨架阶段登记。升级前不得把下列 `unknown` 升为 `confirmed`。

## 同步采集实现细节

| ID | 缺口 | 升级手段 |
|----|------|----------|
| BIT-SYNC-CLOCK-TREE | FPGA 内 sample clock / convert 同源连线 | 网表逆向或芯片级探测 |
| BIT-BANK-AICONV | bank 切换与 AIConv 定时器 HDL | 同上 / 实机 + 抓包对照 |
| FX3-REGMAP | `tFPGARegisterAccess` 寄存器偏移表 | Ghidra 深挖 + 抓包 |
| FX3-FUSION-REQ | Fusion vendor bRequest/payload | **USB 抓包**（刻意延后） |
| USB-FRAME-LAYOUT | Signal Stream 帧内通道打包格式 | 抓流 / 驱动静态 |
| HOST-DAQMX | 主机 API→Fusion 映射 | 驱动/NI-DAQmx 静态（范围外） |

## 硬件识别

| ID | 缺口 | 升级手段 |
|----|------|----------|
| HW-ADC-MPN | 16×ADC 确切料号 | 高清照片丝印 / 原理图 |
| HW-PHOTO-LOCAL | 照片默认不入库 | 从 sixfour 拉取到 `hardware/photos/` |

## 强制保持 null 的桥

见 `bridge_matrix.json` → `forced_null_bridges`。

## 停止条件提醒

目录与 catalog 齐全，**不等于**已掌握运行行为或可实现同卡功能驱动。
