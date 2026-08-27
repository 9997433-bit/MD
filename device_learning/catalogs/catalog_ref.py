"""Reference-design (REF) evidence catalog.

登记来自**公开数据手册 / 公开参考设计**的接口信号定义，作为后续
引脚对照实验的对照模板。来源均为公开文档，与本板实测无关：

- CY7C68013A（EZ-USB FX2LP）数据手册 —— Slave FIFO 同步/异步接口信号组；
- ADS1271 数据手册 —— 串行数据接口（SPI / Frame-Sync 两种格式）；
- FX2LP 家族的串行 EEPROM I2C 引导约定（boot-load over I2C）。

诚实登记原则：

- 所有条目 status 一律 ``candidate``：信号定义在公开手册中真实存在，
  但**本板是否采用该接法、引到哪个引脚，均未验证**。
- 所有条目 boundary 一律标明「需引脚对照实验」：必须以万用表/示波器
  对照实物引脚后才能升级状态。

不推断本板网表、不假设 FPGA 管脚分配、不把“手册有此信号”当作“本板已连接”。
"""
from catalogs import make_entry

LAYER = "ref"
BOUNDARY = "需引脚对照实验"


def _e(identifier, module, description, evidence):
    return make_entry(identifier, LAYER, module, description, "candidate", BOUNDARY, evidence)


ENTRIES = [
    # ---- REF-USB-SLAVE-FIFO: FX2LP-class Slave FIFO interface signals ----
    _e(
        "REF-USB-SLAVE-FIFO-SLRD",
        "usb_slave_fifo",
        "SLRD: slave FIFO read strobe driven by the external master (FPGA)",
        "public datasheet (CY7C68013A slave FIFO mode); board-level hookup not verified",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-SLWR",
        "usb_slave_fifo",
        "SLWR: slave FIFO write strobe driven by the external master (FPGA)",
        "public datasheet (CY7C68013A slave FIFO mode); board-level hookup not verified",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-SLOE",
        "usb_slave_fifo",
        "SLOE: slave FIFO output enable gating the FD data bus drivers",
        "public datasheet (CY7C68013A slave FIFO mode); board-level hookup not verified",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-SLCS",
        "usb_slave_fifo",
        "SLCS#: slave FIFO chip select qualifying SLRD/SLWR/PKTEND",
        "public datasheet (CY7C68013A slave FIFO mode); board-level hookup not verified",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-FLAGA",
        "usb_slave_fifo",
        "FLAGA: FIFO status flag (indexed/programmable, e.g. programmable-level)",
        "public datasheet (CY7C68013A slave FIFO mode); flag configuration on this board unknown",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-FLAGB",
        "usb_slave_fifo",
        "FLAGB: FIFO status flag (typically full flag in default config)",
        "public datasheet (CY7C68013A slave FIFO mode); flag configuration on this board unknown",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-FLAGC",
        "usb_slave_fifo",
        "FLAGC: FIFO status flag (typically empty flag in default config)",
        "public datasheet (CY7C68013A slave FIFO mode); flag configuration on this board unknown",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-FIFOADR",
        "usb_slave_fifo",
        "FIFOADR[1:0]: 2-bit address selecting the active endpoint FIFO (EP2/4/6/8)",
        "public datasheet (CY7C68013A slave FIFO mode); endpoint selection wiring not verified",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-FD-BUS",
        "usb_slave_fifo",
        "FD[15:0]: bidirectional slave FIFO data bus (8-bit or 16-bit word mode)",
        "public datasheet (CY7C68013A slave FIFO mode); bus width used on this board unknown",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-PKTEND",
        "usb_slave_fifo",
        "PKTEND: strobe committing a short (non-full) IN packet to USB",
        "public datasheet (CY7C68013A slave FIFO mode); board-level hookup not verified",
    ),
    _e(
        "REF-USB-SLAVE-FIFO-IFCLK",
        "usb_slave_fifo",
        "IFCLK: interface clock, internal 30/48 MHz output or 5-48 MHz external input",
        "public datasheet (CY7C68013A slave FIFO mode); clock direction/source on this board unknown",
    ),
    # ---- REF-ADC-SPI: ADS1271-class serial data interface signals ----
    _e(
        "REF-ADC-SPI-DOUT",
        "adc_serial",
        "DOUT: serial conversion data output from the ADC toward the fabric",
        "public datasheet (ADS1271 serial interface); pin destination on this board not traced",
    ),
    _e(
        "REF-ADC-SPI-DRDY",
        "adc_serial",
        "DRDY: data-ready indication (shared DOUT/DRDY pin in SPI format)",
        "public datasheet (ADS1271 serial interface); interface format used on this board unknown",
    ),
    _e(
        "REF-ADC-SPI-SCLK",
        "adc_serial",
        "SCLK: serial shift clock for the ADC data interface",
        "public datasheet (ADS1271 serial interface); clock source/frequency on this board unknown",
    ),
    _e(
        "REF-ADC-SPI-FSYNC",
        "adc_serial",
        "FSYNC: frame-sync signal framing each conversion word (frame-sync format)",
        "public datasheet (ADS1271 serial interface); frame-sync usage on this board unknown",
    ),
    _e(
        "REF-ADC-SPI-DIN",
        "adc_serial",
        "DIN: serial data input used for daisy-chaining multiple ADCs",
        "public datasheet (ADS1271 serial interface); daisy-chain topology on this board unknown",
    ),
    _e(
        "REF-ADC-MASTER-CLK",
        "adc_serial",
        "CLK: ADC master/modulator clock input setting the data rate",
        "public datasheet (ADS1271); clock source and frequency on this board not measured",
    ),
    _e(
        "REF-ADC-MODE-PINS",
        "adc_serial",
        "MODE pin(s): operating-mode strap (high-speed / high-resolution / low-power)",
        "public datasheet (ADS1271); strap level on this board not read",
    ),
    _e(
        "REF-ADC-FORMAT-PINS",
        "adc_serial",
        "FORMAT[2:0]: interface-format straps selecting SPI vs frame-sync and chaining",
        "public datasheet (ADS1271); strap levels on this board not read",
    ),
    _e(
        "REF-ADC-SYNC-PIN",
        "adc_serial",
        "SYNC/PDWN: conversion synchronisation / power-down control input",
        "public datasheet (ADS1271); control source on this board not traced",
    ),
    # ---- REF-EEPROM-I2C: FX2LP-class serial EEPROM boot interface ----
    _e(
        "REF-EEPROM-I2C-SCL",
        "eeprom_boot",
        "SCL: I2C clock line between the USB controller and the boot EEPROM",
        "public datasheet (CY7C68013A boot loader); pull-ups and routing on this board not verified",
    ),
    _e(
        "REF-EEPROM-I2C-SDA",
        "eeprom_boot",
        "SDA: I2C data line between the USB controller and the boot EEPROM",
        "public datasheet (CY7C68013A boot loader); pull-ups and routing on this board not verified",
    ),
    _e(
        "REF-EEPROM-I2C-BOOT-ADDR",
        "eeprom_boot",
        "EEPROM I2C device address convention distinguishing small/large boot EEPROMs",
        "public datasheet (CY7C68013A boot loader); address strap on this board not read",
    ),
    _e(
        "REF-EEPROM-I2C-BOOT-BYTE",
        "eeprom_boot",
        "Leading boot-configuration byte (0xC0/0xC2 convention) selecting the boot mode",
        "public datasheet (CY7C68013A boot loader); actual first byte on this board not dumped",
    ),
]
