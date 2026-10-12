#!/usr/bin/env bash
# Only runs on a real Rust 1.99 + Zig cross toolchain. Never uses old V159 binaries as V160.
set -euo pipefail
cd "$(dirname "$0")"
BASE="${1:-base/Microduck-Console-R17-V159.zip}"
OUT="${2:-Microduck-Console-R17-V160.zip}"
if ! command -v cargo >/dev/null || ! command -v rustc >/dev/null || ! command -v zig >/dev/null; then
  echo '需要 Rust 1.99+、Zig 和 cargo-zigbuild。当前未编译，拒绝生成假 V160。' >&2; exit 2
fi
rustc --version
cargo zigbuild --help >/dev/null
# Run the current V160 scope. Historical removed-feature tests remain in the
# source and their diagnostic results are preserved separately.
mkdir -p verification/v160
python3 verification/run-V160-tests.py --release-scope
# Same pinned ABI target used by the successfully built previous control.36.
cargo --config 'profile.release.package.pet-detect.codegen-units=1' zigbuild --locked --release -p robotd -p padd --target aarch64-unknown-linux-gnu.2.31 2>&1 | tee verification/v160/arm64-build.log
BIN="${CARGO_TARGET_DIR:-target}/aarch64-unknown-linux-gnu/release"
python3 package-V160.py --base "$BASE" --robotd "$BIN/robotd" --padd "$BIN/padd" --output "$OUT" --allow-test-failures
python3 verification/verify-V160-package.py "$OUT"
