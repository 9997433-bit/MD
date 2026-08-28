# Datasheet 索引(官方直链 + 本地下载说明)

本目录用于存放板卡关键器件的官方数据手册(PDF)。**PDF 体积普遍在 1–10 MB,不入库**(见文末 git 说明),仓库只保留本索引;需要时按下述直链自行下载到本目录。

## 器件与官方直链

| 器件 | 厂商 | 文档编号 | 官方直链 | 建议本地文件名 |
|---|---|---|---|---|
| XC7K160T(Kintex-7) | AMD/Xilinx | DS182(电气特性) | <https://docs.amd.com/v/u/en-US/ds182_Kintex_7_Data_Sheet> | `ds182_kintex7.pdf` |
| XC7K160T(Kintex-7) | AMD/Xilinx | DS180(7 系列总览) | <https://docs.amd.com/v/u/en-US/ds180_7Series_Overview> | `ds180_7series_overview.pdf` |
| FT600Q(USB 3.0 FIFO) | FTDI | FT_001118(v1.06) | <https://ftdichip.com/wp-content/uploads/2024/11/DS_FT600Q-FT601Q-IC-Datasheet.pdf> | `ft600q_ft601q.pdf` |
| ADS62P49(双通道 14-bit 250 MSPS ADC) | TI | SLAS635 | <https://www.ti.com/lit/ds/symlink/ads62p49.pdf> | `ads62p49.pdf` |
| DAC3283(双通道 16-bit 800 MSPS DAC) | TI | SLAS693 | <https://www.ti.com/lit/ds/symlink/dac3283.pdf> | `dac3283.pdf` |
| CDCE72010(10 路时钟分配/抖动清除) | TI | SCAS858 | <https://www.ti.com/lit/ds/symlink/cdce72010.pdf> | `cdce72010.pdf` |
| S25FL128S(128 Mb SPI NOR Flash) | Infineon(原 Cypress/Spansion) | 001-98283 | <https://www.infineon.com/assets/row/public/documents/10/49/infineon-s25fl128s-s25fl256s-128-mb-16-mb-256-mb-32-mb-fl-s-flash-spi-multi-io-3-v-datasheet-en.pdf?fileId=8ac78c8c7d0d8da4017d0ecfb6a64a17> | `s25fl128s.pdf` |
| IS43TR16128D(2 Gb DDR3,128M×16) | ISSI | 43-46TR16128D | <https://www.issi.com/WW/pdf/43-46TR16128D-82560DL.pdf> | `is43tr16128d.pdf` |
| RTL8211FI(千兆以太网 PHY) | Realtek | JATR-8275-15 | 无官方公开直链,见下方说明 | `rtl8211fi.pdf` |
| TPS74401（U10/U11 净轨 LDO，✅） | TI | SBVS066 | <https://www.ti.com/lit/ds/symlink/tps74401.pdf> | `tps74401.pdf` |
| TRS3221（U33 RS-232，✅） | TI | SLLS366 | <https://www.ti.com/lit/ds/symlink/trs3221.pdf> | `trs3221.pdf` |
| TPS54620（U4 候选，🔶） | TI | SLUS949 | <https://www.ti.com/lit/ds/symlink/tps54620.pdf> | `tps54620.pdf` |
| （已排除）TPS54425 | — | — | 封装与图25 不符，勿再下载作本板证据 | — |

### 各链接说明

- **AMD/Xilinx(DS182/DS180)**:`docs.amd.com/v/u/en-US/...` 是官方 PDF 入口,浏览器打开会直接触发 PDF 下载;脚本抓取会先收到 HTML 跳转页,建议用浏览器下载。
- **FTDI**:上表为官网当前版直链(2024-11 上传,v1.06,文档号 FT_001118);站点启用了 Cloudflare 防爬(curl/wget 会返回 403),请用浏览器下载。入口页:<https://ftdichip.com/products/ft600q-b/>。
- **TI 三款(ADS62P49/DAC3283/CDCE72010)**:`ti.com/lit/ds/symlink/<型号>.pdf` 是 TI 官方"永久链接",始终重定向到最新版 PDF,可直接 curl/wget。
- **Infineon(S25FL128S)**:上表为官方直链(与 S25FL256S 合刊,文档 001-98283);站点偶有防爬验证,如脚本下载失败请用浏览器。产品页:<https://www.infineon.com/cms/en/product/memories/nor-flash/standard-spi-nor-flash/quad-spi-flash/s25fl128sagnfi001/>。
- **ISSI(IS43TR16128D)**:合刊文档(覆盖 IS43/46TR16128D(L) 与 IS43/46TR82560D(L));issi.com 启用了 Incapsula 防爬,脚本请求会被拦截,请用浏览器下载,或从 <https://www.issi.com> 产品页(DRAM → DDR3)进入。
- **Realtek(RTL8211FI-CG)**:官方数据手册标注 "CONFIDENTIAL: Development Partners Only",Realtek 不提供公开直链,正式渠道需在 <https://www.realtek.com> 注册申请。工程参考可检索 "RTL8211F(D)(I)-CG Datasheet Rev 1.7"(第三方镜像广泛存在,例如各开发板厂商的资料页),使用时注意其保密声明。

## 本地下载说明

在本目录(`zero0000-research/assets/datasheets/`)下执行,TI 三款可直接脚本下载:

```bash
curl -L -o ads62p49.pdf   "https://www.ti.com/lit/ds/symlink/ads62p49.pdf"
curl -L -o dac3283.pdf    "https://www.ti.com/lit/ds/symlink/dac3283.pdf"
curl -L -o cdce72010.pdf  "https://www.ti.com/lit/ds/symlink/cdce72010.pdf"
curl -L -o tps74401.pdf   "https://www.ti.com/lit/ds/symlink/tps74401.pdf"
```

其余(AMD/FTDI/Infineon/ISSI)因站点防爬,请用浏览器打开上表直链下载,保存为表中"建议本地文件名"。下载后可用 `file *.pdf` 确认是真实 PDF(防爬拦截时保存下来的会是 HTML)。

## git 说明

本目录的 `*.pdf` 已在仓库根 `.gitignore` 中忽略,下载的 PDF 只留在本地,不要提交;若某份手册确需入库存档(例如厂商已下架),单独用 `git add -f` 并在 commit message 中说明理由。

旁证套件(非本板器件,供交叉比对):Abaco FMC150、TI TSW4200、FTDI AN_421/AN_379。

链接核验日期:2026-08-28(TI/ISSI/Infineon/FTDI/AMD 均为当日官方有效地址;防爬行为以当日实测为准)。
