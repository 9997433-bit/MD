"""FW / DRV / PROTO 层 identifier 目录（USB 子系统静态登记）。

边界声明
--------
本模块登记 USB 子系统三层可辨识对象：

- ``FW``    固件层：MCU（8051 兼容核）固件、串行 EEPROM 引导镜像、
            FPGA 位流的存在性与内容边界。
- ``PROTO`` 协议层：USB 描述符、端点映射、控制/批量传输面。
- ``DRV``   驱动层：主机侧驱动模块、绑定关系、固件加载器。

诚实登记原则：凡是**没有转储/反汇编/抓包证据**的对象，一律按其
缺失程度标注，绝不猜测数值：

- ``missing``      : 应存在但**尚无任何镜像/转储**可分析（8051 固件、EEPROM）。
- ``not_started``  : 有明确分析方法但**尚未开始**（描述符解析、驱动逆向）。
- ``unknown``      : 结构已知需存在但**具体取值/映射无证据**（端点号、传输类型）。
- ``observed``     : 文件/器件存在可见，但内容仍不透明（如 FPGA 位流）。

不做的事：不编造 VID/PID、不假设端点号与方向、不推断 IOCTL 编号、
不把“文件存在”当作“内容已理解”。
"""
from __future__ import annotations

from typing import Any

LAYERS = ("FW", "DRV", "PROTO")

# 字段：identifier / layer / name / status / source / boundary / missing
USB_ENTRIES: list[dict[str, Any]] = [
    # ---- FW：MCU（8051 兼容核）固件 ----
    {
        "identifier": "FW-MCU-CORE-IMAGE",
        "layer": "FW",
        "name": "8051 兼容核固件镜像",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "尚无固件二进制转储可供反汇编",
    },
    {
        "identifier": "FW-MCU-RESET-VECTOR",
        "layer": "FW",
        "name": "复位向量 / 启动入口",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "无固件镜像，入口地址无法确定",
    },
    {
        "identifier": "FW-MCU-CODE-XRAM-MAP",
        "layer": "FW",
        "name": "代码/XRAM 地址映射",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "存储布局与外部 RAM 映射未知",
    },
    {
        "identifier": "FW-MCU-I2C-BOOT-PATH",
        "layer": "FW",
        "name": "MCU 经 I2C 从 EEPROM 引导路径",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "引导判定与加载流程无证据",
    },
    {
        "identifier": "FW-MCU-RENUMERATION",
        "layer": "FW",
        "name": "重枚举（ReNumeration）行为",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "是否二次枚举、切换时机未知",
    },
    # ---- FW：串行 EEPROM 引导镜像 ----
    {
        "identifier": "FW-EEPROM-IMAGE",
        "layer": "FW",
        "name": "串行 EEPROM 内容镜像",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "EEPROM 尚未转储，内容全未知",
    },
    {
        "identifier": "FW-EEPROM-CONFIG-BYTE",
        "layer": "FW",
        "name": "EEPROM 首字节引导配置",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "引导模式配置字节未读出",
    },
    {
        "identifier": "FW-EEPROM-VIDPID",
        "layer": "FW",
        "name": "EEPROM 内 VID/PID 字段",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "标识符值不转储不猜测",
    },
    {
        "identifier": "FW-EEPROM-DESC-OVERRIDE",
        "layer": "FW",
        "name": "EEPROM 内描述符覆盖数据",
        "status": "missing",
        "source": "none",
        "boundary": "no_dump",
        "missing": "是否存放自定义描述符未知",
    },
    # ---- FW：FPGA 位流 ----
    {
        "identifier": "FW-FPGA-BITSTREAM",
        "layer": "FW",
        "name": "FPGA 位流文件（firmware/device.bit）",
        "status": "observed",
        "source": "firmware/device.bit",
        "boundary": "opaque_binary",
        "missing": "位流未解析，逻辑功能不透明",
    },
    {
        "identifier": "FW-FPGA-CONFIG-IFACE",
        "layer": "FW",
        "name": "FPGA 配置接口（加载来源）",
        "status": "unknown",
        "source": "none",
        "boundary": "no_dump",
        "missing": "由 MCU 还是 Flash 配置未确证",
    },
    # ---- PROTO：USB 描述符 ----
    {
        "identifier": "PROTO-DESC-DEVICE",
        "layer": "PROTO",
        "name": "设备描述符（Device Descriptor）",
        "status": "not_started",
        "source": "none",
        "boundary": "no_capture",
        "missing": "未抓取枚举包，字段未解析",
    },
    {
        "identifier": "PROTO-DESC-CONFIG",
        "layer": "PROTO",
        "name": "配置描述符（Configuration Descriptor）",
        "status": "not_started",
        "source": "none",
        "boundary": "no_capture",
        "missing": "供电/接口数量未解析",
    },
    {
        "identifier": "PROTO-DESC-INTERFACE",
        "layer": "PROTO",
        "name": "接口描述符（Interface Descriptor）",
        "status": "not_started",
        "source": "none",
        "boundary": "no_capture",
        "missing": "类/子类/协议字段未解析",
    },
    {
        "identifier": "PROTO-DESC-STRING",
        "layer": "PROTO",
        "name": "字符串描述符（String Descriptors）",
        "status": "not_started",
        "source": "none",
        "boundary": "no_capture",
        "missing": "厂商/产品字符串未读取",
    },
    # ---- PROTO：端点映射 ----
    {
        "identifier": "PROTO-EP-MAP",
        "layer": "PROTO",
        "name": "端点总体映射表",
        "status": "unknown",
        "source": "none",
        "boundary": "no_capture",
        "missing": "端点数量/方向/类型无证据",
    },
    {
        "identifier": "PROTO-EP-BULK-IN",
        "layer": "PROTO",
        "name": "批量 IN 端点（数据上行）",
        "status": "unknown",
        "source": "none",
        "boundary": "no_capture",
        "missing": "端点号与最大包长未知",
    },
    {
        "identifier": "PROTO-EP-BULK-OUT",
        "layer": "PROTO",
        "name": "批量 OUT 端点（命令下行）",
        "status": "unknown",
        "source": "none",
        "boundary": "no_capture",
        "missing": "端点号与用途未确证",
    },
    {
        "identifier": "PROTO-EP-INTERRUPT",
        "layer": "PROTO",
        "name": "中断端点（状态/事件）",
        "status": "unknown",
        "source": "none",
        "boundary": "no_capture",
        "missing": "是否存在中断端点未知",
    },
    {
        "identifier": "PROTO-EP-ALT-SETTINGS",
        "layer": "PROTO",
        "name": "接口备用设置（Alt Settings）",
        "status": "unknown",
        "source": "none",
        "boundary": "no_capture",
        "missing": "带宽/端点随 alt 切换关系未知",
    },
    {
        "identifier": "PROTO-XFER-MODE",
        "layer": "PROTO",
        "name": "数据传输模式（批量/同步）",
        "status": "unknown",
        "source": "none",
        "boundary": "no_capture",
        "missing": "采集流走批量还是同步未确证",
    },
    {
        "identifier": "PROTO-CTRL-VENDOR-REQ",
        "layer": "PROTO",
        "name": "厂商自定义控制请求面",
        "status": "not_started",
        "source": "none",
        "boundary": "no_capture",
        "missing": "bRequest/wValue 语义未解析",
    },
    # ---- DRV：主机侧驱动 ----
    {
        "identifier": "DRV-HOST-MODULE",
        "layer": "DRV",
        "name": "主机侧 USB 驱动模块",
        "status": "not_started",
        "source": "none",
        "boundary": "no_binary",
        "missing": "驱动二进制未获取，未逆向",
    },
    {
        "identifier": "DRV-INF-BINDING",
        "layer": "DRV",
        "name": "驱动 INF 绑定（VID/PID 匹配）",
        "status": "not_started",
        "source": "none",
        "boundary": "no_binary",
        "missing": "匹配标识与安装信息未获取",
    },
    {
        "identifier": "DRV-IOCTL-SURFACE",
        "layer": "DRV",
        "name": "驱动 IOCTL 接口面",
        "status": "not_started",
        "source": "none",
        "boundary": "no_binary",
        "missing": "IOCTL 编号与结构未逆向",
    },
    {
        "identifier": "DRV-FIRMWARE-LOADER",
        "layer": "DRV",
        "name": "主机侧固件下载器",
        "status": "not_started",
        "source": "none",
        "boundary": "no_binary",
        "missing": "是否上电下载固件、下载格式未知",
    },
    {
        "identifier": "DRV-PIPE-EP-BIND",
        "layer": "DRV",
        "name": "驱动管道到端点的绑定",
        "status": "unknown",
        "source": "none",
        "boundary": "cross_layer",
        "missing": "依赖 PROTO 端点映射，尚无证据",
    },
]


def usb_entries() -> list[dict[str, Any]]:
    """返回 USB 子系统全部 entry（只读副本）。"""
    return [dict(e) for e in USB_ENTRIES]


def get_entry(identifier: str) -> dict[str, Any] | None:
    for e in USB_ENTRIES:
        if e["identifier"] == identifier:
            return dict(e)
    return None


def entries_by_layer(layer: str) -> list[dict[str, Any]]:
    return [dict(e) for e in USB_ENTRIES if e["layer"] == layer]


def entries_by_status(status: str) -> list[dict[str, Any]]:
    return [dict(e) for e in USB_ENTRIES if e["status"] == status]


def identifiers() -> list[str]:
    return [e["identifier"] for e in USB_ENTRIES]


def count() -> int:
    return len(USB_ENTRIES)


def status_summary() -> dict[str, int]:
    out: dict[str, int] = {}
    for e in USB_ENTRIES:
        out[e["status"]] = out.get(e["status"], 0) + 1
    return out


ENTRIES = USB_ENTRIES


if __name__ == "__main__":
    print(f"USB entries: {count()} | by status: {status_summary()}")
    for _e in USB_ENTRIES:
        print(f"  {_e['identifier']:<24} {_e['layer']:<6} {_e['status']:<12} {_e['name']}")
