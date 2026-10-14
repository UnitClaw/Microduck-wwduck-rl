[简体中文](README.md) | **English**

# Independent torso IMU source · current FT6

This directory contains firmware for the **STM32G031F8P6 + LSM6DSV16X DIY IMU**, separate from the control.43 Linux services on ZERO. The current Feetech HD1910 setup uses **FT6_SYNC15_UART_IRQ_v1**, fixed ID 200 at 1 Mbps.

**Start with [IMU download, wiring, programming, and checks](../../../../hardware/IMU-FIRMWARE.en.md).** A compiled 8,428-byte `.bin` is available; normal assembly does not require compilation. That page owns the complete flashing procedure.

| Entry | Purpose |
| --- | --- |
| [Current FT6 protocol and compatibility](README_FT6_SYNC15.en.md) | Fast and diagnostic blocks, status, and host contract |
| [Makefile.feetech](Makefile.feetech) · [Pinned toolchain and dependencies](../../../docs/BUILD.en.md#imu-stm32) | Build FT6 for development; output is `build-feetech-ft6/imu_to_feetech_ReVA_FT6_SYNC15_UART_IRQ_v1.bin` |
| [src/](src/) · [include/](include/) · [tests/](tests/) | Current source, interfaces, and tests |
| [A5](README_A5_ORIGINAL.md) | **Historical: original Dynamixel baseline**, including original test tools |
| [FT1](README_FT1.en.md) · [FT2](README_FT2_SYNC20.en.md) · [FT4](README_FT4_LEDHEALTH.md) | **Historical: Feetech development stages**, not the current flashing entry |

`src/main.c` retains the original Dynamixel path under conditional compilation. `Makefile.feetech` defines `FEETECH_NATIVE` and selects the Feetech sources. Filenames containing `dxl`, A5's old LED description, and `tools/imu_live_mac.py` do not mean that FT6 uses Dynamixel protocol. Current FT6 LED behavior follows the source and current flashing guide.
