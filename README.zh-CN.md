**阅读语言：[English](README.md) | [中文](README.zh-CN.md)**

# dustmaps3d

🌌 **一份基于 Gaia 和 LAMOST 构建的全天空三维尘埃消光图**

📄 *Wang et al. (2025)，An all-sky 3D dust map based on Gaia and LAMOST*  
📌 DOI: [10.12149/101620](https://doi.org/10.12149/101620)

📦 *一个用于便捷访问 3D 尘埃图的 Python 包*  
📌 DOI: [10.12149/101619](https://nadc.china-vo.org/res/r101619/)

---

## 📦 安装

通过 pip 安装：

```bash
pip install dustmaps3d
```

**注意：** 安装包本身并不包含模型数据。  
约 350MB 的数据文件将在**首次使用时自动从 GitHub 下载**。  
⚠️ 若遇到网络连接问题，也可从 NADC 手动下载数据：  
🔗 https://nadc.china-vo.org/res/r101619/

---

## 🚀 使用示例

```python
from dustmaps3d import dustmaps3d

l = [120.0]
b = [30.0]
d = [1.5]

EBV, dust, sigma, max_d = dustmaps3d(l, b, d)

print(f"EBV: {EBV[0]:.4f} [mag]")
print(f"Dust: {dust[0]:.4f} [mag/kpc]")
print(f"Sigma: {sigma[0]:.4f} [mag]")
print(f"Max distance: {max_d[0]:.4f} kpc")
```

**FITS 文件批量处理示例：**

```python
import numpy as np
from astropy.io import fits
from astropy.table import Table
from dustmaps3d import dustmaps3d

data = Table.read('input.fits')
l = data['l'].astype(float)
b = data['b'].astype(float)
d = data['distance'].astype(float)

EBV, dust, sigma, max_d = dustmaps3d(l, b, d)

data['EBV_3d'] = EBV
data['dust'] = dust
data['sigma'] = sigma
data['max_distance'] = max_d

data.write('output.fits', overwrite=True)
```

---

## 🧠 函数说明

### `dustmaps3d(l, b, d, n_process=None)`

根据输入的银河坐标 `(l, b)` 和距离 `d`，返回对应的尘埃消光信息。

| 输入         | 类型         | 描述                        | 单位     |
|--------------|--------------|-----------------------------|----------|
| `l`          | np.ndarray   | 银河经                      | 度       |
| `b`          | np.ndarray   | 银河纬                      | 度       |
| `d`          | np.ndarray   | 日心距离                    | kpc      |
| `n_process`  | int, 可选    | 并行处理的进程数量，如设为 None 则默认使用单线程 | – |

#### 返回：

| 输出         | 类型         | 描述                              | 单位     |
|--------------|--------------|-----------------------------------|----------|
| `EBV`        | np.ndarray   | E(B–V) 消光值                     | mag      |
| `dust`       | np.ndarray   | 尘埃密度（d(EBV)/dx）             | mag/kpc  |
| `sigma`      | np.ndarray   | E(B–V) 的不确定度估计             | mag      |
| `max_d`      | np.ndarray   | 每条视线方向上可靠的最大距离      | kpc      |

> 如果输入的 `d` 为 `NaN`，程序将自动替换为该方向上的最大可靠距离。

---

## ⚡ 性能

- 基于 NumPy 完全向量化实现
- 支持通过 `n_process` 并行处理大批量数据
- 在普通个人计算机上，处理 **一亿颗恒星** 仅需约 **100 秒**

---

## 📂 数据版本

当前版本使用数据文件：`data_v2.1.parquet`，来自发布版本 [v2.1](https://github.com/Grapeknight/dustmaps3d/releases/tag/v2.1)

---

## 📜 引用说明

如果您在研究中使用了该模型或包，请引用以下两项：

- Wang, T. (2025), *An all-sky 3D dust map based on Gaia and LAMOST*  
  DOI: [10.12149/101620](https://doi.org/10.12149/101620)
- *dustmaps3d: A Python package for easy access to the 3D dust map*  
  DOI: [10.12149/101619](https://nadc.china-vo.org/res/r101619/)

---

## 🛠️ 授权协议

MIT License
