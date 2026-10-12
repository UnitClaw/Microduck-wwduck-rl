[简体中文](BASELINE.md) | **English**

# Release baseline and validation scope

The current public baseline is **Public Image R1 + R17 V164 / control.40 + Training R1.5.27**. Source was synchronized with the corresponding delivery packages; see [PUBLICATION-MANIFEST.json](../PUBLICATION-MANIFEST.json) for identities and hashes.

| Component | Current version |
| --- | --- |
| Official firmware | daemon-v0.15.1, `1fa84386f07884e27866411bc1ba166977bced95` |
| HD1910 firmware | `1fa8438-feetech-ft6-control.40`, API40; compiled for V163, reused by V164 |
| Robot Console | R17 V164, `1.0.164` |
| Training Studio | R1.5.27; 14 action categories, 35 recipes |
| Training engine | microduck_rl `8d0db74916a4f833d1d9b95d6a1d7f4d13b9d5ec` |
| System image | Public Image R1, first-boot setup R5 |

## Source and downloads

- `firmware/`: upstream Rust workspace, Feetech adaptation, device services, gamepad bridge, HAT / IMU source, installation scripts, models, and original verification records.
- `firmware/console/`: Python, web pages, launchers, assets, and firmware upgrade payload synchronized with the V164 ZIP.
- `training-console/`: console, task configuration, adaptation code, tests, and licensing synchronized with the R1.5.27 ZIP. The training engine and GPU dependencies are downloaded during initial preparation.
- Repository root `release-assets/`: the user-uploaded V164 and R1.5.27 ZIPs; their original bytes were preserved.
- System image: the `public-image-r1` Release. Its automatically generated Source code attachments refer to the original tag snapshot. Use `main` or the homepage repository ZIP for the synchronized current source.

The original firmware source archive also contained three historical console ZIPs under `base/`. They are not source files and are not duplicated in the current source directory. Original `build-V163.sh` / `package-V163.py` remain as build records; running them requires the corresponding V162 base package and original test environment. For compilation on a new machine, use [BUILD.md](BUILD.en.md).

## Validation scope

The public image previously passed a fresh-card test covering Wi-Fi setup, SSH, robot communication, and R17 recognition.

Source synchronization compared the V164 embedded firmware with the control.40 source package's BUILD, native programs, and key source hashes. Rust source and both consoles' program sources were compared byte for byte with delivered files, and the current documentation, manifests, and build-script syntax were checked. Stale version values in the top-level BUILD and source index were corrected using actual release records; originals remain in `firmware/verification/source-package-original-*`.

`firmware/verification/v163/` retains original build-stage records: 235 targeted Rust checks, 6 Python checks, and loading / first inference for 10 ARM64/QEMU models passed. These are original records, not claims that synchronization rebuilt or reran them. Real roller recovery and model movement results remain subject to their individual physical test records.

Source synchronization did not recompile firmware, connect to ZERO to change services, or run long GPU training. It did not change robot control logic, mechanics, electronics, or policies.

## Known-Good and next step

Known-Good software references: official **0.15.1**, **R17 V164 / control.40**, **Training R1.5.27**, and reflash-tested **Public Image R1**. Acceptance scope for individual actions remains defined by the original records.

**The next single main task is to reproduce a new user's first installation and local calibration using the public instructions.** Continue validating one variable at a time.
