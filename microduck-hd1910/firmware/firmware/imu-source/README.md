**简体中文** | [English](README.en.md)

# 独立躯干 IMU 固件源码 · 当前 FT6

这里是 **STM32G031F8P6 + LSM6DSV16X 自制 IMU 板**的固件源码，不是 ZERO 上的 control.43 Linux 服务。当前飞特 HD1910 方案使用 **FT6_SYNC15_UART_IRQ_v1**，固定 ID 200、1 Mbps。

**制作板子从 [IMU 固件下载、接线、烧录与检查](../../../../hardware/IMU-FIRMWARE.md) 开始。** 已有编译好的 8,428 字节 `.bin`，普通制作无需编译。完整烧录说明由该页维护。

| 入口 | 用途 |
| --- | --- |
| [当前 FT6 协议与兼容](README_FT6_SYNC15.md) | 快速读区、诊断区、状态与配套主控约定 |
| [Makefile.feetech](Makefile.feetech) · [固定工具链与依赖](../../../docs/BUILD.md#imu-stm32) | 开发时构建 FT6，输出 `build-feetech-ft6/imu_to_feetech_ReVA_FT6_SYNC15_UART_IRQ_v1.bin` |
| [src/](src/) · [include/](include/) · [tests/](tests/) | 当前源代码、接口和测试 |
| [A5](README_A5_ORIGINAL.md) | **历史：原 Dynamixel 协议基线**，含原版测试工具 |
| [FT1](README_FT1.md) · [FT2](README_FT2_SYNC20.md) · [FT4](README_FT4_LEDHEALTH.md) | **历史：飞特适配阶段记录**，不是当前烧录入口 |

`src/main.c` 保留条件编译的原 Dynamixel 路径；`Makefile.feetech` 定义 `FEETECH_NATIVE` 并选择飞特源文件。文件名带 `dxl`、旧文档里的 A5 LED 说明及 `tools/imu_live_mac.py` 不代表当前 FT6 使用 Dynamixel 协议。当前 FT6 的 LED 行为以源码和当前烧录指南为准。
