#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
BASE="${1:-base/Microduck-Console-R17-V162.zip}"
OUT="${2:-Microduck-Console-R17-V163.zip}"
command -v cargo >/dev/null
command -v rustc >/dev/null
command -v zig >/dev/null
rustc --version
cargo zigbuild --help >/dev/null
mkdir -p verification/v163
python3 verification/test_v163_manual.py
python3 verification/run-V163-tests.py --release-scope
cargo --config 'profile.release.package.pet-detect.codegen-units=1' --config 'profile.release.package.robotd.codegen-units=1' zigbuild --locked --release -p robotd -p padd --target aarch64-unknown-linux-gnu.2.31 2>&1 | tee verification/v163/arm64-build.log
BIN="${CARGO_TARGET_DIR:-target}/aarch64-unknown-linux-gnu/release"
# These variables point at an installed ARM64 QEMU and a compatible runtime root.
# The supplied original model files and ONNX Runtime stay unchanged.
python3 verification/run-V163-models.py --binary "$BIN/robotd"
python3 package-V163.py --base "$BASE" --robotd "$BIN/robotd" --padd "$BIN/padd" --output "$OUT"
python3 verification/verify-V163-package.py "$OUT"
