#!/usr/bin/env bash
# Run in Git Bash: bash ./push-microduck.sh
# The directory containing this script must be the unpacked repository root.
set -Eeuo pipefail

REPO_URL='https://github.com/kissqy/Microduck-kissqy.git'
BRANCH='main'
LIMIT=$((100 * 1024 * 1024))
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd -- "$SCRIPT_DIR"
TASK_TMP=''
LOG_FILE=''

cleanup() {
    if [[ -n "$TASK_TMP" && -d "$TASK_TMP" ]]; then rm -rf -- "$TASK_TMP"; fi
}
failed() {
    local code=$?
    trap - ERR
    printf '\n推送未完成，退出码：%s。上面保留了 Git 的原始错误。\n' "$code" >&2
    [[ -z "$LOG_FILE" ]] || printf '日志：%s\n' "$LOG_FILE" >&2
    printf '修复提示的问题后，可再次运行同一个脚本。\n' >&2
    exit "$code"
}
die() { printf '\n停止：%s\n' "$*" >&2; exit 1; }
step() { printf '\n[%s/7] %s\n' "$1" "$2"; }
trap cleanup EXIT
trap failed ERR

step 1 '确认源码文件夹与 Git'
command -v git >/dev/null || die '未找到 Git。请先安装 Git for Windows，重新打开 VS Code 并选择 Git Bash 终端。'
[[ -f README.md ]] || die '请把脚本放到解压后的 Microduck-kissqy 根目录，与 README.md 放在一起。'
printf '源码目录：%s\n仓库：%s\n分支：%s\n' "$SCRIPT_DIR" "$REPO_URL" "$BRANCH"
git --version
if [[ -e .git ]]; then
    ROOT="$(git rev-parse --show-toplevel)"
    [[ "$(cd -- "$ROOT" && pwd -P)" == "$SCRIPT_DIR" ]] || die '当前文件夹不是仓库根目录。'
    [[ "$(git symbolic-ref --quiet --short HEAD)" == "$BRANCH" ]] || die '现有仓库当前分支不是 main，请先切换到正确分支。'
else
    # Reject a folder nested inside a different Git repository.
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        die '此源码文件夹位于另一个 Git 仓库内。请将它移到独立文件夹后运行。'
    fi
    git init -b "$BRANCH"
fi
git config core.longpaths true
git config core.quotePath false
GIT_DIR="$(git rev-parse --absolute-git-dir)"
LOG_FILE="$GIT_DIR/microduck-push-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1
TASK_TMP="$(mktemp -d)"

step 2 '连接原仓库并读取 main 历史（下载进度）'
if ! git remote | grep -Fxq origin; then git remote add origin "$REPO_URL"; fi
is_expected_url() {
    [[ "$1" == "$REPO_URL" || "$1" == "${REPO_URL%.git}" ||
       "$1" == 'git@github.com:kissqy/Microduck-kissqy.git' ||
       "$1" == 'ssh://git@github.com/kissqy/Microduck-kissqy.git' ]]
}
mapfile -t FETCH_URLS < <(git remote get-url --all origin)
mapfile -t PUSH_URLS < <(git remote get-url --push --all origin)
[[ ${#FETCH_URLS[@]} == 1 && ${#PUSH_URLS[@]} == 1 ]] || die 'origin 配置了多个地址，请先核对。'
is_expected_url "${FETCH_URLS[0]}" || die '现有 origin 不是 kissqy/Microduck-kissqy，未修改该地址。'
is_expected_url "${PUSH_URLS[0]}" || die '现有 origin 推送地址不是 kissqy/Microduck-kissqy。'
git -c http.version=HTTP/1.1 fetch --progress --no-tags origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    # Only an unborn branch is attached to remote history. Source bytes stay intact.
    git reset --mixed --quiet "origin/$BRANCH"
else
    git merge-base --is-ancestor "origin/$BRANCH" HEAD ||
        die '远端 main 含有本地尚未合并的提交。请先处理同步；脚本不会重置已有提交或强推。'
fi
[[ ! -f "$GIT_DIR/MERGE_HEAD" && ! -d "$GIT_DIR/rebase-merge" && ! -d "$GIT_DIR/rebase-apply" ]] ||
    die '此仓库正在合并或 rebase，请先完成该操作。'
git ls-files -u > "$TASK_TMP/unmerged"
[[ ! -s "$TASK_TMP/unmerged" ]] || die '仓库含有未解决的冲突。'

step 3 '保留原仓库文件，准备提交'
# Treat the supplied package as an overlay: absent remote files are retained.
# This also retains the two existing original runtime ZIP packages.
git ls-files -z > "$TASK_TMP/tracked"
: > "$TASK_TMP/missing"
MISSING=0
while IFS= read -r -d '' file; do
    if [[ ! -e "$file" && ! -L "$file" ]]; then
        printf '%s\0' "$file" >> "$TASK_TMP/missing"
        MISSING=$((MISSING + 1))
    fi
done < "$TASK_TMP/tracked"
if (( MISSING > 0 )); then
    printf '补齐本地未包含的 %s 个原仓库文件（已有源码不覆盖）。\n' "$MISSING"
    git checkout-index -z --stdin < "$TASK_TMP/missing"
fi
# Local excludes only; the delivered project's .gitignore is not changed.
EXCLUDE="$GIT_DIR/info/exclude"
mkdir -p -- "$(dirname -- "$EXCLUDE")"
if ! grep -Fq '# Microduck local publishing helper' "$EXCLUDE" 2>/dev/null; then
    cat >> "$EXCLUDE" <<'IGNORE'

# Microduck local publishing helper
/push-microduck.sh
.venv/
venv/
node_modules/
__pycache__/
*.pyc
*.pyo
.DS_Store
.env
.env.local
.env.*.local
IGNORE
fi
if ! git var GIT_AUTHOR_IDENT >/dev/null 2>&1; then
    printf '首次提交需要设置作者信息，只保存在这个仓库。\n'
    read -r -p '提交者名称（回车使用 kissqy）：' AUTHOR_NAME
    git config user.name "${AUTHOR_NAME:-kissqy}"
    read -r -p '提交邮箱（填你的 GitHub 邮箱或 GitHub 设置中的隐私邮箱）：' AUTHOR_EMAIL
    [[ -n "$AUTHOR_EMAIL" ]] || die '未填写提交邮箱，可设置后重跑。'
    git config user.email "$AUTHOR_EMAIL"
fi

step 4 '分批整理文件（按文件数量显示百分比）'
git ls-files -z --modified --deleted --others --exclude-standard > "$TASK_TMP/candidates-unsorted"
sort -zu "$TASK_TMP/candidates-unsorted" > "$TASK_TMP/candidates"
TOTAL=0
while IFS= read -r -d '' file; do TOTAL=$((TOTAL + 1)); done < "$TASK_TMP/candidates"
DONE=0
COUNT=0
: > "$TASK_TMP/batch"
printf '待整理文件：%s\n' "$TOTAL"
while IFS= read -r -d '' file; do
    printf '%s\0' "$file" >> "$TASK_TMP/batch"
    COUNT=$((COUNT + 1))
    if (( COUNT >= 50 )); then
        git -c core.autocrlf=false --literal-pathspecs add -A --pathspec-from-file="$TASK_TMP/batch" --pathspec-file-nul
        DONE=$((DONE + COUNT))
        printf '整理文件：%3d%% (%d/%d)\n' "$((DONE * 100 / TOTAL))" "$DONE" "$TOTAL"
        COUNT=0
        : > "$TASK_TMP/batch"
    fi
done < "$TASK_TMP/candidates"
if (( COUNT > 0 )); then
    git -c core.autocrlf=false --literal-pathspecs add -A --pathspec-from-file="$TASK_TMP/batch" --pathspec-file-nul
    printf '整理文件：100%% (%d/%d)\n' "$TOTAL" "$TOTAL"
fi

step 5 '核对单文件大小，必要时转换为 Git LFS'
git ls-files --stage -z > "$TASK_TMP/index"
: > "$TASK_TMP/oids"
: > "$TASK_TMP/paths"
while IFS= read -r -d '' entry; do
    meta="${entry%%$'\t'*}"
    file="${entry#*$'\t'}"
    read -r mode oid stage_no <<< "$meta"
    [[ "$mode" != 160000 ]] || die "发现嵌套 Git 仓库/子模块：$file。请先确认它应当作为子模块还是普通源码发布。"
    printf '%s\n' "$oid" >> "$TASK_TMP/oids"
    printf '%s\0' "$file" >> "$TASK_TMP/paths"
done < "$TASK_TMP/index"
git cat-file --batch-check='%(objectsize)' < "$TASK_TMP/oids" > "$TASK_TMP/sizes"
: > "$TASK_TMP/large"
LARGE=0
while IFS= read -r bytes && IFS= read -r -d '' file <&3; do
    if (( bytes > LIMIT )); then
        printf '超过 100 MiB：%s (%s MiB)\n' "$file" "$((bytes / 1024 / 1024))"
        printf '%s\0' "$file" >> "$TASK_TMP/large"
        LARGE=$((LARGE + 1))
    fi
done < "$TASK_TMP/sizes" 3< "$TASK_TMP/paths"
if (( LARGE > 0 )); then
    git lfs version >/dev/null 2>&1 || die '需要 Git LFS，但当前未安装。请安装 Git LFS 后重跑；尚未创建本次提交。'
    git lfs install --local
    while IFS= read -r -d '' file; do git lfs track --filename -- "$file"; done < "$TASK_TMP/large"
    git -c core.autocrlf=false --literal-pathspecs add -- .gitattributes
    git -c core.autocrlf=false --literal-pathspecs add --pathspec-from-file="$TASK_TMP/large" --pathspec-file-nul
    # Verify conversion before committing; no raw oversized blob may enter the commit.
    while IFS= read -r -d '' file; do
        bytes="$(git cat-file -s ":$file")"
        (( bytes <= LIMIT )) || die "Git LFS 未成功转换：$file"
    done < "$TASK_TMP/large"
else
    printf '所有暂存文件均在普通 Git 单文件限制以内。\n'
fi

step 6 '创建源码提交'
if git diff --cached --quiet; then
    printf '没有新的文件变更，将继续推送已有本地提交。\n'
else
    git diff --cached --shortstat
    git commit -m "Publish Microduck source update $(date +%Y-%m-%d)"
fi

step 7 '上传 GitHub（压缩/上传进度、已传大小、速度）'
printf 'Git 登录窗口若弹出，请登录 kissqy。网络中断后可以重跑。\n'
GIT_LFS_FORCE_PROGRESS=1 git -c http.version=HTTP/1.1 push --progress --set-upstream origin "HEAD:refs/heads/$BRANCH"
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git -c http.version=HTTP/1.1 ls-remote origin "refs/heads/$BRANCH" | cut -f1)"
[[ "$LOCAL_SHA" == "$REMOTE_SHA" ]] || die '远端提交与本地不一致，请查看是否同时有其他人推送。'
printf '\n推送成功！GitHub main 已核对到本地提交 %s。\n' "${LOCAL_SHA:0:12}"
printf '打开：https://github.com/kissqy/Microduck-kissqy\n日志：%s\n' "$LOG_FILE"
