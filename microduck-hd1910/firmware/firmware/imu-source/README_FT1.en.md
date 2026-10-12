[简体中文](README_FT1.md) | **English**

# Microduck native Feetech FT1 — communication and IMU test build

September 20, 2026. Based on frozen daemon 0.10.0, commit `590b986bd8c0d50ae02cb3ea2f59c463b6828168`. This is a historical communication test, not an upstream-main upgrade or a finished walking release. Current FT6 documentation and hardware validation are recorded separately.

## What was built?

| Target | Work | Installation / status at FT1 delivery |
| --- | --- | --- |
| Radxa host | Independent native Feetech backend, selectable alongside Dynamixel | Development x 86_64 build / offline tests complete; ARM64 robotd not deployed |
| Custom RevA IMU | Native Feetech FT1 firmware | STM32 G031 F8 P6 ARM.bin generated; board not flashed at this stage |
| HD1910 servo | Factory native Feetech protocol | No internal servo firmware build / flash |
| Dynamixel / A5 | Preserved | Original code retained; rebuilt A5.bin SHA256 identical |

This is native communication, not protocol conversion. Feetech selection sends only Feetech packets, with no DXL attempt or fallback. Existing compatibility default remains `dynamixel`; the test explicitly sets `protocol = "feetech"`. Radxa services / configuration / installed programs were not changed. No automatic installation / flashing script was supplied.

## The single next FT1 test

At this historical step, do not flash IMU or replace robotd yet. Keep configured runtime `--fake`. Put package-root `feetech_probe.py` at `/home/radxa/feetech_probe.py` and run:

```bash
/home/radxa/dxl-venv/bin/python /home/radxa/feetech_probe.py --id 1
```

Read ID1 once; do not read ID2, scan the bus, or change torque / ID / gains / baud. It uses Python's standard library, without pyserial or service installation. It checks existing robotd first and exits before opening serial if a running daemon lacks the exact `--fake` argument. Resolve permissions / port ownership rather than taking the port with sudo. Defaults:`/dev/ttyS2`, 1 Mbps. Expect position_raw, voltage, temperature, and raw packets.

Review that one result before proceeding. Power off before wiring changes; do not hot-plug servos. Temporary systemd drop-ins live under `/run`; after reboot fake mode may be lost, so the script checks again.

## Implemented boundaries

- Native Rust encoding / checksum, streaming reception, echo filtering, ID / length / error validation, timeout.
- HD1910 address 56, 11-byte measured feedback; native position, torque, and 15-servo SyncWrite APIs.
-15-servo position SyncWrite is 128 bytes; this is offline encoding evidence, not 15-servo physical acceptance.
- SyncWrite has no ACK. Successful transmission does not prove execution; torque-off requires reading register 40.
- Native IMU identity/20-byte data, sequence, sample age, readiness; host retains the SFLP decoder.
- Servo and IMU native registers are read separately within a full cycle, not presented as simultaneous sampling.
- HD1910 0x82 SyncRead was not physically verified at FT1; diagnostics use verified per-ID Read.
- Bench servos retain IDs 1/2 rather than automatically adopting robot IDs. The 15-joint mapping needs separate calibration.

This first version was a communication / diagnostics backend:

1. `RobotIo::write`, policy gain / torque enable, and Feetech `robotd init` explicitly refuse.
2. Native `Bus` has bench position / torque / SyncWrite APIs; the delivered operational entry exposes reads only.
3. Full-robot diagnostics require a complete 15-joint map and confirmed speed / current units.
4. Unknown current is not shown as 0 mA; XL330 Kp and guessed HD1910 current ratios are not reused.
5. No automatic EEPROM writes, factory reset, ID / baud changes, or startup HOME.

`config/hd1910-calibration.template.toml` intentionally cannot enable directly. Use a single-servo probe before inventing calibration to start the daemon. `config/robotd-feetech-bench.toml` disables policies, voltage adaptation, and the old 2 S low-battery shutdown check; it is an example, not a replacement for installed configuration at the two-servo stage.

## IMU FT1 and A5

RevA / A5 MCU, SPI, UART, electrical direction control, sensor ODR, SFLP, and mounting transform remain. Only the Feetech build branch changes communication parsing / registers, expanding the RX ring to 256 bytes. Original Makefile builds DXL; separate `Makefile.feetech` builds FT without DXL objects.

| Item | FT1 definition |
| --- | --- |
| Serial |1 Mbps, 8 N1, original HAT TTL half-duplex |
| IMU ID |200, fixed / read-only |
| Model |Custom 0xF200; addresses 3/4, little-endian |
| Packet |`FF FF ID LENGTH INSTRUCTION PARAMS CHECKSUM` |
| Checksum |Inverted 8-bit sum from ID through last parameter |
| Ping |Native empty-parameter status reply; model read separately |
| Data |Address 124, 20 bytes; first 12 can be read for diagnostics |
| Write / reset / ID change |Unsupported; unicast error reply, no broadcast reply |
| SyncRead |0x82; responds only if ID200 is first; first host version does not use it |

| Address | Length | Data |
| --- | --- | --- |
|124–129|6|Raw gyro XYZ, i 16 little-endian, same as A5|
|130–135|6|SFLP quaternion XYZ, IEEEfloat 16 little-endian, same as A5|
|136–139|4|Quaternion-update sequence, u 32 little-endian; increments only on new quaternion, wraps|
|140–141|2|Quaternion age in milliseconds, u 16 saturated at 65535|
|142|1|Bit 0: valid quaternion received; other bits 0|
|143|1|Data schema, fixed 1|

Native read:`FF FF C8 04 02 7C 14 A1`. IMU stays silent for servo broadcast SyncWrite. Host rejects age above 50 ms or three consecutive identical sequences, including whole-cycle time in the age budget. Pseudo-serial / firmware-C integration checks do not establish physical UART timing.

New firmware:`firmware/imu_to_feetech_ReVA_FT1_UART_IRQ_v1.bin`, 7144 bytes, SHA256 `84c4d5dd488433585b262accd4a69971e3eec11b10d4bd8b424340ea9564035e`. Flash base 0x08000000, only for the confirmed RevA STM32 G031 F8 P6 board. This is not servo firmware; do not load it into HD1910 using FE-URT2 servo update.

A5 rollback:`rollback/imu_to_dxl_ReVA_M8A5_UART_IRQ_v1.bin`, 7432 bytes, SHA256 `85ee561cced17025a94be1b469a9b393578a16edc49bd90d101d2786aec79bac`. Returning to XL330 requires both Dynamixel host backend and A5 IMU firmware; a host toggle alone cannot make FT1 speak DXL. Use the previously validated SWD process separately after the single-servo read passes.

## Saved XL330 baseline and FT1 HD1910 evidence

Values come from original September 3, 2026 benchmark JSON / collector, not product ratings. Original CSV / JSON remains in `baseline/`; no invented HD1910 traces.

| Item | XL330-M288-T baseline | HD1910 evidence at FT1 |
| --- | --- | --- |
| Supply readback |5.3 V|5.9 V read, different conditions|
| Link |FTDI USB, ttyUSB0, 1 Mbps|HAT ttyS2, 1 Mbps|
| Communication |300/300; mean 1.933 ms, P95 2.159 ms|Single read / move and two-servo sync passed; no equivalent statistics|
| Movement |57 ticks≈5.016°; 5 rounds/20 segments|+100 ticks and return tested|
| Limits |Profile raw 10=2.29 rpm; acceleration raw 1; goal PWM raw 100|Speed raw 100, ACC raw 5; values cannot directly compare|
| Arrival |Mean 0.818 s, P95 0.8212 s|No timestamped trajectory|
| Final error |Mean absolute 1.75 ticks, max 3|One two-servo result:−1 at target,+1 on return|
| Overshoot |Observed 0 in this dataset|Unknown without time series|
| Current |Peak 13 mA|Model current-register scale unconfirmed; load cannot be converted|
| Temperature |27→27°C|30°C previously read; different room temperature / duration|

0.818 s measures from before target writing until first entry within±8 ticks, followed by 0.4 s observation. Sampling 0.05 s includes communication; it is neither maximum unloaded speed nor isolated motor delay.

## Trying to retain existing training

First preserve joint order, positive direction, zeros, observation units, and IMU mounting transform. Under confirmed allowed matching voltage, comparable speed limits, and equal inertia / load, record both servos' trajectories one item at a time. Match arrival time, error, delay, and deadband before fitting actuator compensation without changing weights.

Candidates include zero / direction mapping, bounded feedforward, and speed / acceleration limits. They require timestamped loaded data; outputs still obey joint range, speed, torque, and fall protection. Unlimited feedforward cannot make slower hardware faster; gain units, torque, and mechanical differences can invalidate old policies. FT1 therefore installs no guessed coefficients or automatic movement; decide weight reuse after comparison.

## Development reproduction — not the immediate Radxa step

The patch targets the frozen commit above. In a separate matching worktree, check then apply it. New files are included. No remote commit / push or production deployment was made in that step.

```bash
git apply --check /path/to/robotd-feetech-ft1.patch
git apply /path/to/robotd-feetech-ft1.patch
cargo test --locked -p duck-control -p robotd-params -p robotd --lib --bins
cargo build --locked -p robotd -p duck-control --examples --bins
python3 scripts/feetech_probe.py --self-test
python3 scripts/test_feetech_native.py --imu-source /path/to/imu-source
```

Rust 1.90.0, original lockfile. Development output is x 86_64 and cannot run on Radxa; no wrong-architecture robotd was supplied. ARM64 deployment belongs to a later stage.

Firmware uses Arm GNU14.3.Rel 1, CMSIS Core 5.9.0, ST cmsis-device-g 0 commit `f576c24e123edf3332988ecd49512c0f35f85186`:

```bash
make -f Makefile.feetech feetech \
  TOOLCHAIN=/path/to/bin/arm-none-eabi- \
  CMSIS_CORE=/path/to/CMSIS_5/CMSIS/Core/Include \
  CMSIS_DEVICE=/path/to/cmsis-device-g0
```

The separate toolchain needs no service reinstallation and is not bundled. The A5 linker script retains bare-metal nosys-stub and RWX LOAD warnings. FT1 ELF / BIN contains no DXL parser symbols. A5 build, protocol fuzz, and original-binary identity checks passed. Strict all-target Clippy is blocked by pre-existing consecutive `#[cfg(test)]` lines in frozen `robotd/src/chorale.rs`; unrelated code was not changed, and new communication modules were checked separately.

Packet / SMS_STS register cross-check:[official Feetech SDK](https://github.com/FTservo/FTServo_Python/blob/54e86a7a28824999f254d9a4f5364cdc17379583/scservo_sdk/sms_sts.py), a generic table rather than a complete HD1910 datasheet. XL330 units / table:[official ROBOTIS manual](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/). Test values above are saved user JSON measurements, not manual ratings.
