[简体中文](README.md) | **English**

# DIY HAT and IMU hardware

**Both the HAT and the independent torso IMU have passed extended real-robot use, operate normally, and have no identified issues.**

| Hardware | Build record | EasyEDA Pro project |
| --- | --- | --- |
| HAT board | [Build timeline and the choice of a two-layer PCB](HAT-TIMELINE.en.md) | [HAT_REVA_SCH](ProPrj_HAT_REVA_SCH_2026-10-07.epro2) |
| Independent torso IMU | [Build timeline, frozen A5 baseline, and Feetech adaptation](IMU-TIMELINE.en.md) | [imu_to_dxl_RevA_V1](ProPrj_imu_to_dxl_RevA_V1_2026-10-07.epro2) |

## Shopping list

[Download the HAT / IMU parts and tools shopping list (Excel, Chinese)](https://github.com/kissqy/Microduck-kissqy/raw/refs/heads/main/hardware/Microduck-HAT-IMU-Shopping-List-20261013.xlsx)

Compiled from the author's actual purchase records, with the listed purchases confirmed usable through real-robot testing. The workbook includes a consolidated shopping list, HAT and IMU reference-designator BOMs, product links, exact models, selected variants, and quantities, plus accessories and build supplies such as solder paste, tweezers, soldering stations, stencils, and an ST-LINK programmer.

The HAT started with a study of the official components and their surrounding circuits. Unneeded functions were removed, and the board was made using a two-layer PCB and home reflow. The IMU first established working independent hardware and the original protocol, then reused that hardware on the Feetech bus with 15 servos.

The timelines follow the build history organized on October 12, 2026. The published project files are snapshots dated October 7, 2026. Differences between physical-board tuning and the project BOM are documented in the HAT guide.

**Current baseline, confirmed October 12, 2026:** fabrication, full-robot integration, and extended real-robot validation are complete for both boards. Test records from the original IMU A5 and later Feetech adaptation stages are retained.
