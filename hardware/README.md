**简体中文** | [English](README.en.md)

# HAT 与 IMU 自制硬件

**HAT 和独立躯干 IMU 均已在实机上经过长时间使用验证，运行正常，没有发现问题。**

| 硬件 | 制作记录 | EasyEDA Pro 工程 |
| --- | --- | --- |
| HAT 主板 | [制作时间线及两层板的选择](HAT-TIMELINE.md) | [HAT_REVA_SCH](ProPrj_HAT_REVA_SCH_2026-10-07.epro2) |
| 独立躯干 IMU | [制作时间线、A5 冻结及飞特适配过程](IMU-TIMELINE.md) | [imu_to_dxl_RevA_V1](ProPrj_imu_to_dxl_RevA_V1_2026-10-07.epro2) |

## 采购清单

[下载 HAT／IMU 详细采购清单（Excel）](https://github.com/kissqy/Microduck-kissqy/raw/refs/heads/main/hardware/Microduck-HAT-IMU-Shopping-List-20261013.xlsx)

根据作者的实际购买记录整理，所列采购商品已确认实测可用。表内包含合并采购清单、HAT 与 IMU 位号 BOM、商品链接、完整型号、指定购买款式和用量，以及锡膏、镊子、焊台、钢网、烧录器等配件与制作用品。

HAT 的思路是先分析官方器件及外围，按实际需要精简，再用两层板和家庭回流完成实物。IMU 先跑通独立硬件及原版协议，再复用硬件接入飞特和 15 个舵机。

时间线依据 2026-10-12《整理HAT时间线》中已经整理的制作过程。工程文件是当前仓库公开的 2026-10-07 快照；实板调试改动与工程 BOM 的差异见 HAT 文档。

**当前记录基线（2026-10-12 确认）：** HAT 与 IMU 已完成制作、整机接入及长期实机验证；IMU 原 A5 与后续飞特适配保留各阶段的测试记录。
