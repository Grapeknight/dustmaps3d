import subprocess
import os
import sys
from pathlib import Path

# 仓库基础信息
REPO = "Grapeknight/dustmaps3d"
RELEASE_TAG = "v2.1.0"
RELEASE_NAME = "dustmaps3d v2.1.0"
RELEASE_DESC = "📦 Updated 3D dust map data and documentation."
DATA_PATH = Path(r"D:\_3d_map_data\data_v2.1.parquet")  # 修改为你的文件路径
BRANCH = "main"

def run(cmd, cwd=None, allow_error=False):
    """运行 shell 命令并显示输出"""
    print(f"📦 Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        if allow_error:
            print("⚠️ 命令失败，但继续执行...")
        else:
            print("❌ 命令执行失败！")
            sys.exit(1)

def check_git_config():
    """检查 git 用户信息是否设置"""
    print("🔍 检查 Git 用户配置...")
    name = subprocess.getoutput("git config user.name")
    email = subprocess.getoutput("git config user.email")

    if not name.strip() or not email.strip():
        print("⚠️ Git 用户信息未配置，正在设置...")
        run('git config --global user.name "Grapeknight"')
        run('git config --global user.email "wt@mail.bnu.edu.cn"')
    else:
        print(f"✅ Git 用户已设置为：{name} <{email}>")

def check_git_remote():
    """检查远程是否使用 SSH，建议更换为 SSH 提高稳定性"""
    print("🔍 检查 Git 远程地址...")
    remote = subprocess.getoutput("git remote get-url origin")
    if remote.startswith("https://"):
        print("⚠️ 当前远程使用 HTTPS，推荐改为 SSH 更稳定")
        print("👉 正在修改为 SSH...")
        run(f"git remote set-url origin git@github.com:{REPO}.git")
    else:
        print("✅ Git 远程地址已是 SSH")

def push_code_to_github():
    """将本地改动推送到 GitHub"""
    print("🚀 推送代码到 GitHub 仓库...")

    # 添加所有更改
    run("git add .")

    # 尝试提交（若无变更不会出错）
    run('git commit -m "🔄 Update version, docs, and data link"', allow_error=True)

    # 推送到远程仓库
    run(f"git push origin {BRANCH}")

def upload_release_asset():
    """将数据文件上传至 GitHub Releases"""
    print("📤 上传数据文件到 GitHub Releases...")

    if not DATA_PATH.exists():
        print(f"❌ 文件未找到: {DATA_PATH}")
        sys.exit(1)

    # 创建 release（如果不存在则忽略错误）
    run(f'gh release create {RELEASE_TAG} "{DATA_PATH}" --title "{RELEASE_NAME}" --notes "{RELEASE_DESC}"', allow_error=True)

    # 或者追加上传
    run(f'gh release upload {RELEASE_TAG} "{DATA_PATH}" --clobber')

def main():
    check_git_config()
    check_git_remote()
    push_code_to_github()
    upload_release_asset()
    print("✅ 所有操作已完成！")

if __name__ == "__main__":
    main()
