**简体中文** | [English](README_FT2_SYNC20.en.md)

> **历史版本；当前飞特方案使用 FT6。** 制作请先看 [IMU 下载与烧录指南](../../../../hardware/IMU-FIRMWARE.md)，下文的协议、LED 和测试工具属于当时版本。

# FT2 Sync20 增量

FT2 在 FT1 的 20 字节 IMU 快照上增加地址 56 的只读别名，同时保留地址 124。
固件身份版本由 1.0 更新为 2.0；数据 schema 仍为 1。

源码差异见包根目录 `patches/imu-ft1-to-ft2-sync20.patch`，完整行为与验收边界见
`../README.md` 和 `../TEST_RESULTS.md`。

构建：

```bash
make -f Makefile.feetech feetech \
  TOOLCHAIN=/path/to/bin/arm-none-eabi- \
  CMSIS_CORE=/path/to/CMSIS_5/CMSIS/Core/Include \
  CMSIS_DEVICE=/path/to/cmsis-device-g0
```

默认输出目录为 `build-feetech-ft2`，不会覆盖 FT1 构建目录。
