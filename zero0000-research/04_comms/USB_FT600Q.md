# USB / FT600Q 通信研究

> 来源：[FTDI与USB通路研究](bc-51662658-f637-5bf1-8cea-abd944d0a4e0)

## 要点

| 项 | 内容 |
|----|------|
| 芯片 | FT600Q：USB3 → **16-bit FIFO**，峰值约 **200 MB/s** |
| 驱动 | **D3XX**（非 D2XX）；PID **0x601E** |
| 与 FT232 区分 | `0403:601e` vs `0403:6001/6014`；速度 5Gbps vs 480Mbps |
| FPGA 角色 | Master；时钟由 FT600 输出（66/100 MHz） |
| Kintex-7 | 无官方现成工程，需移植 AN_421 RTL + XDC |

## 阶段4 Checklist（摘录）

**无实物可先做：** 定 245 模式、移植 FIFO master、写 XDC、仿真回环、准备 PyD3XX 脚本与 udev。

**有实物：** `lsusb` 确认 SuperSpeed → 回环 → 吞吐 → ILA 时序 → 长稳。

## 证据

FTDI DS / AN_386 / AN_412 / AN_421 / AN_379（详见子代理完整报告）。
