[简体中文](V163-构建说明.md) | **English**

# Microduck R17 V163 / control.40 build and usage scope

This build's console is `1.0.163`, firmware `1fa8438-feetech-ft6-control.40`, targeting official `0.15.1` Linux AArch 64. See [console usage](console/USER-GUIDE.en.md) and [firmware / model / calibration guide](packaging/README.en.md). This is the V163 delivery record; V164 reuses its firmware.

## Physical L3 roller recovery test

L3 means pressing the left stick. padd reads existing `robot.mode`, `robot.health`, and `robot.state`. It checks roller mode, enabled policy, no active action, ready / fresh IMU, and a fall consistent with the actual quaternion, then requests `roller_stand` through existing `robot.do`.

The test uses zero commands, scale 1.0, head / leg filters 1.0, and no repeated triggering. Local skill configuration supplies a 5-second window, returning to swizzle afterwards; Start cancels. The window is a manual-test setting, not a duration declared by the original export contract. Upright, walking, HOME, torque-released, stale-feedback, changed-mode, and unloaded-model states refuse the request and log why. This entry does not enable the policy or automatically apply torque; completed HOME and an enabled roller policy are prerequisites.

robotd control, serial, startup, and IPC mechanisms are retained; its source only updates BUILD identity. Service units, calibration, image repairs, SSH credentials, and project links follow confirmed configuration. Web L3 stays disabled and informational; LB remains left-foot kick.

The model uses the original roller recovery export. ONNX SHA256: `2575b5894bcd8e3fdbe005b1a7b90d9491085726df32000c26cf5b92b7a10ebb`. The archive name says 10000; the manifest's actual checkpoint is 11000. Contracts, training information, and weights are preserved file by file.

## Tools and build

Actual tools used: Rust `1.99.0`, Zig `0.15.1`, cargo-zigbuild `0.23.4`, target `aarch64-unknown-linux-gnu.2.31`. Requirements include the Rust AArch 64 standard library, AArch 64 libudev development files, native Linux build dependencies, Python 3, readelf, and ONNX Runtime. Host tests require `ORT_DYLIB_PATH` pointing to host-architecture ONNX Runtime; bundled ARM64 libraries cannot run host tests.

Set `PKG_CONFIG_ALLOW_CROSS=1`, `PKG_CONFIG_SYSROOT_DIR`, and target `PKG_CONFIG_LIBDIR`. Set `QEMU_AARCH64` to QEMU ARM64 and `ARM64_RUNTIME_PREFIX` to a compatible ARM64 runtime root. From the firmware project root:

```bash
bash build-V163.sh
```

The script runs the current targeted tests, compiles real robotd / padd, checks all ten models in QEMU, then packages and verifies the product. robotd and pet-detect use release codegen-units 1. Argument one can specify the base ZIP; argument two the output ZIP.

The base is `base/Microduck-Console-R17-V162.zip`, SHA256 `9e8d82ea6a57dfbfa15592fab980e57a1e67fb2dff1b6e7bfb63f773a2283a5e`. Packaging refuses old programs, incorrect build identity, failed tests, or mismatched ARM64 model records. Product verification uses the actual console firmware-import interface and compares changed files individually.

## Deliverables

`Microduck-Console-R17-V163.zip` includes installable firmware, four roller models, and usage instructions. Fully extract, connect to ZERO, and install using **系统维护 → 随包固件** (System Maintenance → Bundled Firmware). Replacing only the desktop console does not update the robot-side physical-gamepad program.

`Microduck-Source-R17-V163-control40-compiled.tar.gz` contains complete source, models, actual compiled programs, tools, and records, excluding reproducible target caches. `packaging/robotd` and `packaging/padd` match the installation package.

| Program | SHA256 |
| --- | --- |
| robotd | `464dde28e0be939237fdd1b7e9a4087d751b5c495b896cf25b6c8e44ba3c0fe9` |
| padd | `356ed712b97c5c073cc9c691ede802a72704c7ece42d69c626f3c69fab0af241` |

## Validation scope

| Check | Result |
| --- | --- |
| duck-control unit tests | 138 passed |
| duck-ipc-proto unit tests | 53 passed |
| padd unit tests, including L3 release gate and native IPC trigger / refusal | 41 passed |
| robotd roller and complete bundled-configuration loading | 3 passed |
| Configuration install / upgrade, custom settings, repeat installation, model / web-input preservation | 6 passed |
| ARM64/QEMU loading and first inference for six regular and four roller models | 10 passed |
| Product manifest, hashes, native ELF, config-change scope, and actual console import | Passed |
| Physical ZERO roller recovery movement | Not yet validated in this build record |

The targeted Rust scope totals 235 passed, zero failed. Originals are in `verification/v163/`, summarized in `V163-BUILD-STATUS.json`. This is not a full-workspace regression. Retained earlier diagnostics are not passed checks for this build. Physical recovery requires robot testing; ARM64/QEMU checks do not establish mechanical acceptance.
