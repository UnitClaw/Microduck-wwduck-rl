**简体中文** | [English](README-R17.en.md)

# Microduck control.40 固件与 R17 V164 中控

本目录是 **control.40** 固件源码，基于官方 Microduck **0.15.1**，IPC API 为 **40**。配套机器人中控为 **R17 V164**。

V164 沿用 V163 已编译的 control.40 固件。原源码归档名为 `Microduck-Source-R17-V163-control40-compiled.tar.gz`；当前顶层 [BUILD.json](BUILD.json) 来自真实安装载荷，与 V164 随包 BUILD 逐字节一致。

- [机器人中控启动与使用](console/README.zh-CN.md)
- [固件配置、模型与设备安装说明](packaging/README.zh-CN.md)
- [新机器从源码编译](../docs/BUILD.md)
- [当前发布版本与验收范围](../docs/BASELINE.md)
- [原 V163 构建环境和测试记录](V163-构建说明.md)
- [上游工作区开发说明](CONTRIBUTING.md)

Rust、Python、网页、模型与原生程序按对应交付文件同步；本次只整理源码公开和版本索引。每台机器人仍需使用并核对自己的关节、方向、限位和 IMU 标定。
