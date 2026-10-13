[简体中文](README.md) | **English**

# Compiled Feetech HD1910 firmware · control.40

An **ARM64 robot-service installation package for Radxa ZERO 3W**, based on official Microduck 0.15.1 and paired with Robot Console R17 V164, IPC API40. It includes compiled `robotd`, `padd`, `robotctl`, camera services, inference libraries, 10 movement models, and installation scripts. **No source compilation is required for ordinary use.**

[⬇️ Download compiled firmware .tar.gz](https://github.com/kissqy/Microduck-kissqy/raw/refs/heads/main/microduck-hd1910/firmware/console/updates/Microduck-Robotd-FT6-R17.tar.gz) · [SHA256 file](Microduck-Robotd-FT6-R17.sha256) · [Identity and verification record](firmware-control40.json) · [Project homepage](../README.en.md)

## Image, console, and standalone firmware

| Package | Purpose |
| --- | --- |
| System image `.img.xz` | Fresh microSD installation with control.40 and the robot environment preinstalled. |
| Robot Console V164 `.zip` | Computer-side control tool; `updates/` contains this same compiled firmware. |
| Standalone `.tar.gz` here | The original V164 firmware payload, offered separately for existing-system upgrades. |

**Ordinary users need the system image and Robot Console.** A current image does not require another firmware download merely to obtain compiled programs. This package updates ZERO Linux services; HAT/IMU microcontroller firmware uses separate `.bin` files. This `.tar.gz` is not a microSD system image.

## Install with the console

Extract the complete [Robot Console V164](https://github.com/kissqy/Microduck-kissqy/raw/refs/heads/main/release-assets/Microduck-Console-R17-V164.zip), run `start.cmd` (macOS/Linux: `bash start.command`), connect to ZERO over SSH, and use **系统维护 → 随包固件** (System Maintenance → Bundled Firmware). The console already includes this payload; no separate `.tar.gz` download is needed for that flow.

Local firmware import accepts ZIP rather than a bare `.tar.gz`. If you downloaded this standalone package, wrap the unchanged archive in ZIP using Windows PowerShell:

```powershell
Compress-Archive -Path .\Microduck-Robotd-FT6-R17.tar.gz -DestinationPath .\Microduck-Firmware-control40.zip
```

Select that ZIP in V164's firmware importer. Keep the inner name `Microduck-Robotd-FT6-R17.tar.gz`; the console verifies its SHA256 against the matched bundled firmware.

## Install separately over SSH

Use on ZERO with an existing official Microduck 0.15.1 or this project's Public Image R1 environment. **Run the commands in ZERO's SSH terminal.** For an empty microSD card, start with the system image instead.

```bash
(
  set -e
  microduck_fw_dir=$(mktemp -d "$HOME/microduck-control40.XXXXXX")
  curl -fL --progress-bar \
    -o "$microduck_fw_dir/Microduck-Robotd-FT6-R17.tar.gz" \
    "https://github.com/kissqy/Microduck-kissqy/raw/refs/heads/main/microduck-hd1910/firmware/console/updates/Microduck-Robotd-FT6-R17.tar.gz"
  printf '%s  %s\n' \
    'cba2a3d1fa486713c72f1155fed42d102c2fe3aea9bb3aaf0aad337e046b9afd' \
    "$microduck_fw_dir/Microduck-Robotd-FT6-R17.tar.gz" | sha256sum -c -
  tar -xzf "$microduck_fw_dir/Microduck-Robotd-FT6-R17.tar.gz" -C "$microduck_fw_dir"
  sudo bash "$microduck_fw_dir/Microduck-Robotd-FT6-R17/service.sh" upgrade
)
```

Download progress is shown; a failed checksum stops the commands. The existing `service.sh upgrade` flow reads and prioritizes valid local calibration and saved settings. Wait for startup steps 1/4–4/4, verify this assembly's joints and IMU, then complete HOME before enabling movement.

## Identity and checksum

| Item | Value |
| --- | --- |
| Build | `1fa8438-feetech-ft6-control.40` |
| Official baseline / API | `0.15.1` / `40` |
| Console | `R17 V164`; firmware compiled for V163 and reused by V164 |
| Architecture | Linux AArch64 / ARM64 |
| Size | 34,554,759 bytes (approximately 32.95 MiB) |
| SHA256 | `cba2a3d1fa486713c72f1155fed42d102c2fe3aea9bb3aaf0aad337e046b9afd` |

This publication verified byte identity with the firmware inside V164, all 160 archive checksum entries, and the hashes, sizes, and AArch64 ELF identity of eight programs/libraries against the existing BUILD record. It provides a standalone entry without recompilation or physical-robot installation. Original build/test scope is in [the V163 record](../microduck-hd1910/firmware/V163-BUILD.en.md).

[Firmware source and versions](../microduck-hd1910/firmware/README-R17.en.md) · [Build from source](../microduck-hd1910/docs/BUILD.en.md) · [Component licenses](../microduck-hd1910/LICENSE)
