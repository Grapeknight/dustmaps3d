**Read this in: [English](README.md) | [中文](README.zh-CN.md)**

# dustmaps3d

🌌 **基于 Gaia 和 LAMOST 构建的全天三维尘埃消光图**

📄 *Wang et al. (2025)，An all-sky 3D dust map based on Gaia and LAMOST*  
📌 DOI: [10.12149/101620](https://doi.org/10.12149/101620)

📦 *A Python package for easy access to the 3D dust map*   
📌 DOI: [10.12149/101619](https://nadc.china-vo.org/res/r101619/)

---

## 📦 安装

通过 pip 安装：

```bash
pip install dustmaps3d
```

## 📦 数据文件说明

> ⚠️ 安装包本身**不包含数据文件**。首次使用时将自动从 GitHub 或 NADC 下载约 400MB 的模型数据文件。

### 🚀 自动下载机制

- 调用 `dustmaps3d()` 时会自动尝试下载数据文件 `data_v3.fits.gz`；
- 下载完成后会自动解压为 `data_v3.fits`，并缓存于本地；
- 下次使用将直接读取缓存，无需重复下载。

### 🌐 下载失败怎么办？

如果你在国内使用，可能会遇到 GitHub 下载失败（如 `connect timeout`），这是正常的网络问题。本包已内置了国内镜像源：

- ✅ 首选源（国内用户）：[NADC 数据中心]（暂时还在申请，稍好上线）
- 🌀 备选源（国际用户）：GitHub Releases 

如两个源都无法连接，建议手动下载。

### 📥 手动下载方式（推荐国内用户）

1. 打开镜像链接：（暂时还在申请，稍好上线）
2. 下载文件：`data_v3.fits.gz`
3. 解压得到 `data_v3.fits`
4. 将其放入本地缓存目录（首次使用包时终端会打印缓存路径提示）

> 示例路径（Windows）：  
> `C:\Users\<用户名>\AppData\Local\dustmaps3d\data_v3.fits`

> 示例路径（Linux/macOS）：  
> `/home/<用户名>/.local/share/dustmaps3d/data_v3.fits`

---

## 🚀 使用示例

```python
from dustmaps3d import dustmaps3d

l = [120.0]
b = [30.0]
d = [1.5]

EBV, dust, sigma, max_d = dustmaps3d(l, b, d)

print(f"EBV: {EBV.values[0]:.4f} [mag]")
print(f"Dust: {dust.values[0]:.4f} [mag/kpc]")
print(f"Sigma: {sigma.values[0]:.4f} [mag]")
print(f"Max distance: {max_d.values[0]:.4f} kpc")
```

**FITS 文件批量处理示例：**

```python
import numpy as np
from astropy.table import Table
from dustmaps3d import dustmaps3d

data = Table.read('input.fits')   
l = data['l'].astype(float)
b = data['b'].astype(float)
d = data['d'].astype(float)

EBV, dust, sigma, max_d = dustmaps3d(l, b, d)

data['EBV_3d'] = EBV
data['dust'] = dust
data['sigma'] = sigma
data['max_distance'] = max_d
data.write('output.fits', overwrite=True)

```

---
## 🧠 函数说明

### `dustmaps3d(l, b, d)`

根据输入的银河坐标 `(l, b)` 和距离 `d`，返回对应的尘埃消光信息。

| 输入         | 类型         | 描述                        | 单位     |
|--------------|--------------|-----------------------------|----------|
| `l`          | np.ndarray   | 银经                      | 度       |
| `b`          | np.ndarray   | 银纬                      | 度       |
| `d`          | np.ndarray   | 距离                      | kpc      |

#### 返回：

| 输出         | 类型         | 描述                              | 单位     |
|--------------|--------------|-----------------------------------|----------|
| `EBV`        | np.ndarray   | E(B–V) 消光值                     | mag      |
| `dust`       | np.ndarray   | 尘埃密度（d(EBV)/dx）             | mag/kpc  |
| `sigma`      | np.ndarray   | E(B–V) 的不确定度估计             | mag      |
| `max_d`      | np.ndarray   | 每条视线方向上可靠的最大距离      | kpc      |

> 如果输入的 `d` 中包含 `NaN`，程序将自动将其替换为该视线方向的最大可靠距离（`max_d`）。
>
> 如果输入的 `d` 超过了 `max_d`，则说明该点超出了模型的可靠范围。此时返回的值是通过外推计算的，**不具有可靠性**。

---

## ⚡ 性能

- 基于 NumPy 完全向量化实现
- 在普通个人计算机上，单线程处理 **一亿颗恒星** 仅需约 **100 秒**

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

## 📫 联系方式

如在使用本工具过程中有任何问题、建议或技术交流，欢迎通过 GitHub issue 或邮箱联系作者团队：

- Prof. Yuan Haibo（苑海波 教授）: yuanhb@bnu.edu.cn  
- Wang Tao（王涛）: wt@mail.bnu.edu.cn  

🔗 [GitHub Repository](https://github.com/Grapeknight/dustmaps3d)