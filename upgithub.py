import os
import subprocess
from pathlib import Path
from datetime import date

# ====== 用户可修改的设置 ======
TAG = "v2.1.0"  # GitHub Release 的标签
ASSET_PATH = Path("D:/_3d_map_data/data_v2.1.parquet")  # 要上传的数据文件路径
ASSET_NAME = "data_v2.1.parquet"  # 上传后在 release 中显示的文件名
REPO = "Grapeknight/dustmaps3d"  # GitHub 仓库名
RELEASE_TITLE = "Dustmaps3D v2.1.0"
RELEASE_NOTES = f"""
📦 Updated data release for Dustmaps3D

- 🔢 Version: {TAG}
- 📅 Date: {date.today()}
- 📁 File: `{ASSET_NAME}` (~350MB)

👉 If GitHub download fails due to network issues, you can get the data via:
🔗 NADC: https://nadc.china-vo.org/res/r101619/
"""

# ====== 工具函数 ======
def run(cmd: str, cwd: Path = None):
    print(f"📦 Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

# ====== 推送代码到 GitHub（包含 pyproject、README、核心代码等）======
def push_code_to_github():
    print("🚀 推送代码到 GitHub 仓库...")
    run("git add .")
    # 如果没有实际改动，跳过 commit 不报错
    run('git commit -m "🔄 Update version, docs, and data link" || echo \"✅ 无需提交\"')
    run("git push origin main")

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
