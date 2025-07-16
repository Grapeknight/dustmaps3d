import os
import subprocess
from pathlib import Path
from datetime import date

# ====== 用户可修改的设置 ======
TAG = "v2.1"  # GitHub Release 的标签
ASSET_PATH = Path("D:/_3d_map_data/data_v2.1.parquet")  # 要上传的数据文件路径
ASSET_NAME = "data_v2.1.parquet"  # 上传后在 release 中显示的文件名
REPO = "Grapeknight/dustmaps3d"  # GitHub 仓库名
RELEASE_TITLE = "Dustmaps3D v2.1"
RELEASE_NOTES = f"""
📦 Updated data release for Dustmaps3D

- 🔢 Version: {TAG}
- 📅 Date: {date.today()}
- 📁 File: `{ASSET_NAME}` (~400MB)

👉 If GitHub download fails due to network issues, you can get the data via:
🔗 NADC: https://nadc.china-vo.org/res/r101619/
"""

# ====== 工具函数 ======
def run(cmd: str, cwd: Path = None):
    print(f"📦 Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

# ====== 推送代码到 GitHub（包含 pyproject、README、核心代码等）======
def push_code_to_github():
    print("🚀 Pushing code to GitHub...")

    # 不再拉取远程分支，直接添加所有文件
    run("git add .")
    
    result = subprocess.run(
        "git diff-index --quiet HEAD || echo 'has_changes'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if 'has_changes' in result.stdout:
        run('git commit -m "🔄 Update version, docs, and data link"')
        run("git push --force origin main")
    else:
        print("✅ No changes to commit.")
        
# ====== 创建 release 并上传数据文件 ======
def upload_release_asset():
    print("📤 创建 GitHub Release 并上传数据文件...")

    # 确保已登录 gh（用户之前已登录）
    # 创建/更新 Release
    run(f'gh release create {TAG} "{ASSET_PATH}" '
        f'--repo {REPO} '
        f'--title "{RELEASE_TITLE}" '
        f'--notes "{RELEASE_NOTES.strip()}" '
        f'--latest '
        f'--clobber')  # 可覆盖上传同名文件

# ====== 主程序 ======
def main():
    push_code_to_github()
    upload_release_asset()

if __name__ == "__main__":
    main()
