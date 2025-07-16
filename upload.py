import os
import shutil
import subprocess
from pathlib import Path

# === 用户可配置项 ===
PACKAGE_NAME = "dustmaps3d"
VERSION = "2.1.0"
PARQUET_PATH = Path(r"D:\_3d_map_data\data_v2.1.parquet")
RELEASE_TAG = f"v{VERSION}"
RELEASE_NAME = f"{PACKAGE_NAME} {VERSION}"
RELEASE_NOTES = "Updated data_v2.1.parquet and version 2.1.0 build."
PYPI_REPO = "dustmaps3d"
# ====================

def run(cmd, cwd=None):
    """运行 shell 命令"""
    print(f"📦 Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def clean_previous_builds():
    """清理旧的 dist、build、egg-info、__pycache__ 等目录"""
    print("🧹 Cleaning previous build files...")

    for folder in ['build', 'dist', f'{PACKAGE_NAME}.egg-info']:
        shutil.rmtree(folder, ignore_errors=True)

    # 清除 __pycache__ 文件夹
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)

def build_package():
    """构建 tar.gz 和 .whl 包"""
    print("🛠️ Building package...")
    run("python -m build")

def upload_to_pypi():
    """上传构建好的包到 PyPI"""
    print("⬆️ Uploading to PyPI...")
    run(f"twine upload --repository {PYPI_REPO} dist/*")

def upload_to_github():
    """将 .parquet 数据文件上传至 GitHub Release"""
    print("⬆️ Uploading .parquet file to GitHub Release...")

    # 检查是否已有 release
    result = subprocess.run(
        ["gh", "release", "view", RELEASE_TAG],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if result.returncode != 0:
        # 创建 release
        run(f'gh release create {RELEASE_TAG} "{PARQUET_PATH}" -t "{RELEASE_NAME}" -n "{RELEASE_NOTES}"')
    else:
        # 更新 release 文件
        run(f'gh release upload {RELEASE_TAG} "{PARQUET_PATH}" --clobber')

def main():
    clean_previous_builds()
    build_package()
    upload_to_pypi()
    upload_to_github()
    print(f"✅ 发布完成：{PACKAGE_NAME}=={VERSION}")

if __name__ == "__main__":
    main()
