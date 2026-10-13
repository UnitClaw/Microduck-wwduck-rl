**简体中文** | [English](README.en.md)

# 飞特 HD1910 已编译固件 · control.40

这是用于 **Radxa ZERO 3W 的 ARM64 机器人服务安装包**，基于官方 Microduck 0.15.1，配套 R17 V164 中控，IPC API40。包内已包含编译好的 `robotd`、`padd`、`robotctl`、摄像头服务、推理库、10 个运动模型及安装脚本，**普通使用不需要从源码编译**。

[⬇️ 下载已编译固件 .tar.gz](https://github.com/kissqy/Microduck-kissqy/raw/refs/heads/main/microduck-hd1910/firmware/console/updates/Microduck-Robotd-FT6-R17.tar.gz) · [SHA256 校验文件](Microduck-Robotd-FT6-R17.sha256) · [包身份与核验记录](firmware-control40.json) · [项目首页](../README.md)

## 和镜像、中控是什么关系

| 文件 | 用途 |
| --- | --- |
| 系统镜像 `.img.xz` | 新装 TF 卡；已预装 control.40 和机器人环境。 |
| 机器人中控 V164 `.zip` | 电脑端操作工具；`updates/` 中包含同一个已编译固件包。 |
| 本页独立固件 `.tar.gz` | 从 V164 的固件载荷原样提供，供已有系统单独升级服务。 |

**普通用户用「系统镜像＋机器人中控」即可。** 刷好当前镜像后，不需要为了取得编译好的固件再单独下载安装。本包是 ZERO 的 Linux 服务包，HAT / IMU 单片机固件另有 `.bin`；`.tar.gz` 不能作为 TF 卡系统镜像刷写。

## 用中控安装

完整解压 [机器人中控 V164](https://github.com/kissqy/Microduck-kissqy/raw/refs/heads/main/release-assets/Microduck-Console-R17-V164.zip)，运行 `start.cmd`（macOS/Linux 用 `bash start.command`），通过 SSH 连接 ZERO，在 **系统维护 → 随包固件** 安装。中控已自带本页的固件，因此走此流程不用另外下载 `.tar.gz`。

中控的本地固件导入接受 ZIP，不直接接受 `.tar.gz`。如果已经下载本页固件，可在 Windows PowerShell 将它原样放入 ZIP：

```powershell
Compress-Archive -Path .\Microduck-Robotd-FT6-R17.tar.gz -DestinationPath .\Microduck-Firmware-control40.zip
```

然后在 V164 中控的固件导入处选择这个 ZIP。保留内部文件名 `Microduck-Robotd-FT6-R17.tar.gz`；中控会核对其 SHA256 是否与本版随包固件一致。

## 用 SSH 单独安装

用于已经具备官方 Microduck 0.15.1 或本项目 Public Image R1 环境的 ZERO。**以下命令在 ZERO 的 SSH 终端执行**；空白 TF 卡首次安装请使用系统镜像。

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

下载显示进度；校验失败会停止。安装使用现有 `service.sh upgrade` 流程，读取并优先保留有效本机标定及已保存参数。完成后等待机器人服务 1/4～4/4 就绪，再按这台机器的装配核对关节和 IMU；完成 HOME 后启用运动。

## 版本与校验

| 项目 | 值 |
| --- | --- |
| 构建标识 | `1fa8438-feetech-ft6-control.40` |
| 官方基线 / API | `0.15.1` / `40` |
| 配套中控 | `R17 V164`；固件由 V163 编译，V164 沿用 |
| 架构 | Linux AArch64 / ARM64 |
| 文件大小 | 34,554,759 字节（约 32.95 MiB） |
| SHA256 | `cba2a3d1fa486713c72f1155fed42d102c2fe3aea9bb3aaf0aad337e046b9afd` |

本次核对确认独立下载与 V164 ZIP 中的固件逐字节一致，160 项包内校验通过，8 个程序／运行库的哈希、长度与 AArch64 ELF 身份匹配已有 BUILD 记录。这次提供独立入口，没有重新编译或操作实机；原始构建测试范围见 [V163 构建记录](../microduck-hd1910/firmware/V163-构建说明.md)。

[固件源码及版本说明](../microduck-hd1910/firmware/README-R17.zh-CN.md) · [从源码编译](../microduck-hd1910/docs/BUILD.md) · [分项许可](../microduck-hd1910/LICENSE)
