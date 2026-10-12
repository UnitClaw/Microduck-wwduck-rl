# 发布基线与验证范围

当前公开基线为 **Public Image R1 + R17 V164 / control.40 + Training R1.5.27**。源码按对应交付包同步，具体身份与哈希见 [PUBLICATION-MANIFEST.json](../PUBLICATION-MANIFEST.json)。

| 组件 | 当前版本 |
| --- | --- |
| 官方固件 | daemon-v0.15.1，`1fa84386f07884e27866411bc1ba166977bced95` |
| HD1910 固件 | `1fa8438-feetech-ft6-control.40`，API40；由 V163 编译，V164 沿用 |
| 机器人中控 | R17 V164，`1.0.164` |
| 训练中控 | R1.5.27；14 类动作、35 种配方 |
| 训练引擎 | microduck_rl `8d0db74916a4f833d1d9b95d6a1d7f4d13b9d5ec` |
| 系统镜像 | Public Image R1，首次配网 R5 |

## 源码与下载位置

- `firmware/`：官方 Rust 工作区、飞特适配、设备服务、手柄桥、HAT/IMU 源码、安装脚本、模型与原始验证记录。
- `firmware/console/`：与 V164 ZIP 同步的 Python、网页、启动入口、资源与固件升级载荷。
- `training-console/`：与 R1.5.27 ZIP 同步的训练中控、任务配置、适配代码、测试和许可。训练引擎及 GPU 依赖在首次准备环境时下载。
- 仓库根目录 `release-assets/`：用户上传的 V164 和 R1.5.27 两个 ZIP；原 ZIP 字节保持。
- 系统镜像：`public-image-r1` Release。该 Release 的自动生成 Source code 附件指向原标签快照；当前同步源码请使用 main 分支或首页的仓库源码 ZIP。

固件源码原归档还包含 `base/` 下的三个历史中控 ZIP，这些不是源文件，不重复放进当前源码目录。原 `build-V163.sh`/`package-V163.py` 保留为原版构建记录，若运行它们，需要自行准备相应 V162 基础包及原测试环境。新机器编译入口见 [BUILD.md](BUILD.md)。

## 验证范围

公开镜像此前已通过重新刷卡、首次配网、SSH、机器人通信和 R17 识别测试。

本次同步核对了 V164 内嵌固件与 control.40 源码包的 BUILD、原生程序及关键源码哈希；Rust 源码、两个中控的程序源码均按原交付文件逐字节核对，并核对当前说明、清单及编译脚本语法。顶层 BUILD 和源码索引的残留旧版本值已按实际发布记录修正，原记录保存在 `firmware/verification/source-package-original-*`。

`firmware/verification/v163/` 保存原编译阶段的验证记录：当前 Rust 范围 235 项、Python 范围 6 项、ARM64/QEMU 模型加载与首次推理 10 项通过。这些是原版记录，不代表本次重新编译或重新运行测试。实机滑轮起身及各模型的运动效果仍以各自实测记录为准。

本次没有重新编译机器人固件，没有连接 Zero 改动服务，也没有执行 GPU 长训练；没有修改机器人控制逻辑、机械、电控或 Policy。

## Known-Good 与下一步

Known-Good 软件发布参考：官方 **0.15.1**、**R17 V164 / control.40**、**Training R1.5.27**、已重刷验证的 **Public Image R1**；不同动作的验收范围仍以原记录为准。

**下一步唯一主任务：按公开安装说明完成新用户首次安装与本机标定的复现验证。** 继续一次只验证一个变量。
