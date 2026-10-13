[简体中文](README-R17.zh-CN.md) | **English**

# Microduck control.40 firmware and R17 V164 console

This directory contains **control.40** source based on official Microduck **0.15.1**, using IPC API **40**. Its paired Robot Console is **R17 V164**.

V164 reuses control.40 compiled for V163. The original archive was `Microduck-Source-R17-V163-control40-compiled.tar.gz`. Current top-level [BUILD.json](BUILD.json) comes from the actual installation payload and is byte-for-byte identical to the BUILD bundled with V164.

- [Compiled control.40 download and installation](../../release-assets/README.en.md)
- [Robot Console startup and usage](console/USER-GUIDE.en.md)
- [Firmware configuration, models, and installation](packaging/README.en.md)
- [Compile from source on a new machine](../docs/BUILD.en.md)
- [Current baseline and acceptance scope](../docs/BASELINE.en.md)
- [Original V163 environment and tests](V163-BUILD.en.md)
- [Upstream workspace development](CONTRIBUTING.md)

Rust, Python, web pages, models, and native programs were synchronized from delivered files. Source publication organized documentation and version indexes. Each robot must still use and check its own joint, direction, limit, and IMU calibration.
