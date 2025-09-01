import os
import subprocess
from pathlib import Path
from datetime import date
import sys

# ====== 用户可修改的设置 ======
TAG = "v3"  # GitHub Release 标签
ASSET_PATH = Path("D:/_3d_map_data/data_v3.fits.gz")  # 数据文件路径
ASSET_NAME = "data_v3.fits.gz"  # 上传后文件名
REPO = "Grapeknight/dustmaps3d"
RELEASE_TITLE = "Dustmaps3D v3"
RELEASE_NOTES = f"""
📦 New compressed data release for Dustmaps3D

- 🔢 Version: {TAG}
- 📅 Date: {date.today()}
- 📁 File: `{ASSET_NAME}` (compressed FITS format)

This version replaces the previous Parquet format and is optimized for better compatibility and storage efficiency.

👉 If GitHub download fails due to network issues, you can get the data via:
🔗 NADC: https://nadc.china-vo.org/res/r101619/
""".strip()

# ====== 工具函数 ======
def run(cmd: str, cwd: Path = None, check=True, capture_output=False):
    """安全执行命令，可捕获输出"""
    print(f"📦 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=capture_output, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result

def is_repo_clean() -> bool:
    """检查工作区是否干净（无未提交更改）"""
    result = run("git diff-index --quiet HEAD --", capture_output=True, check=False)
    return result.returncode == 0

def has_changes_to_commit() -> bool:
    """检查是否有待提交的更改"""
    result = run("git status --porcelain", capture_output=True, check=False)
    return bool(result.stdout.strip())

def push_code_to_github():
    """仅当有代码变更时，才提交并推送"""
    print("🚀 Checking code changes...")

    if not has_changes_to_commit():
        print("✅ No changes to commit.")
        return

    if not is_repo_clean():
        print("📝 Changes detected, committing...")
        run('git add .')
        run('git commit -m "🔄 Update to v3: switch to FITS format and refresh data link"')

    print("📤 Pushing to GitHub (safe push, no --force)...")
    # 使用 git push --force-with-lease 更安全（仅当本地是最新时才推）
    run("git push --force-with-lease origin main")
    print("✅ Code pushed successfully.")

def release_exists(tag: str) -> bool:
    """检查指定 tag 的 release 是否已存在"""
    result = run(f"gh release view {tag} --repo {REPO}", capture_output=True, check=False)
    return result.returncode == 0

def upload_release_asset():
    """创建 release 或更新已有 release 的资产"""
    print(f"📤 Managing GitHub Release: {TAG}")

    if not ASSET_PATH.exists():
        print(f"❌ Asset file not found: {ASSET_PATH}")
        sys.exit(1)

    if release_exists(TAG):
        print(f"🔁 Release {TAG} already exists. Updating asset...")
        # 删除旧的同名 asset，再上传新的
        # 注意：GitHub CLI 不支持直接覆盖同名 asset，需先删后传
        delete_cmd = f'gh release delete-asset {TAG} {ASSET_NAME} --repo {REPO} --yes'
        result = run(delete_cmd, capture_output=True, check=False)
        if result.returncode != 0:
            print("⚠️ No existing asset to delete, or error ignored.")

        # 上传新 asset
        upload_cmd = f'gh release upload {TAG} "{ASSET_PATH}" --repo {REPO} --clobber'
        run(upload_cmd)
        print(f"✅ Asset updated in existing release {TAG}")

    else:
        print(f"🆕 Creating new release {TAG}...")
        create_cmd = (
            f'gh release create {TAG} '
            f'--repo {REPO} '
            f'--title "{RELEASE_TITLE}" '
            f'--notes "{RELEASE_NOTES}" '
            f'--latest '
        )
        run(create_cmd)

        # 单独上传 asset（避免路径空格问题）
        upload_cmd = f'gh release upload {TAG} "{ASSET_PATH}" --repo {REPO}'
        run(upload_cmd)
        print(f"✅ Release {TAG} created and asset uploaded.")

# ====== 主程序 ======
def main():
    try:
        push_code_to_github()
        upload_release_asset()
        print("🎉 All operations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ A command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()