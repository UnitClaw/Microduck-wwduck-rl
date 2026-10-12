[简体中文](README_FT2_SYNC20.md) | **English**

# FT2 Sync 20 increment

FT2 adds a read-only alias at address 56 for FT1's 20-byte IMU snapshot, while retaining address 124. Firmware identity changes from 1.0 to 2.0; data schema remains 1.

The original package's source patch is `patches/imu-ft1-to-ft2-sync20.patch`. Its original `../README.md` and `../TEST_RESULTS.md` described behavior and acceptance scope; these references describe the historical FT2 package layout.

Build:

```bash
make -f Makefile.feetech feetech \
  TOOLCHAIN=/path/to/bin/arm-none-eabi- \
  CMSIS_CORE=/path/to/CMSIS_5/CMSIS/Core/Include \
  CMSIS_DEVICE=/path/to/cmsis-device-g0
```

Default output: `build-feetech-ft2`; it does not overwrite FT1 output.
