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
- 下载完成后自动解压为 `data_v3.fits`，并缓存于本地；
- 下次使用将直接读取缓存，无需重复下载。

- ✅ 国内用户会自动识别并优先从国家天文数据中心下载数据，无需翻墙：[NADC 数据中心](https://nadc.china-vo.org/res/file_upload/download?id=51939)
- 🌀 如果下载失败将自动切换为备选源：[GitHub Releases](https://github.com/Grapeknight/dustmaps3d/releases)

> 对于非中文系统用户，默认下载顺序将反转，优先使用 GitHub。

---

### 🌐 下载失败怎么办？

如果下载失败（例如 `connect timeout`），你也可以手动下载数据文件并放入缓存目录：

1. 打开镜像链接：  
   国内用户：[NADC 数据中心](https://nadc.china-vo.org/res/r101662/)  
   国际用户：[GitHub Releases](https://github.com/Grapeknight/dustmaps3d/releases)

2. 下载文件：`data_v3.fits.gz`
3. 解压得到：`data_v3.fits`
4. 将其放入本地缓存目录（首次调用时终端会打印出路径提示）

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

**CSV 文件批量处理示例：**

```python
import numpy as np
import pandas as pd
from dustmaps3d import dustmaps3d

df = pd.read_csv("input.csv",)

l = df["l"]
b = df["b"]
d = df["d"]

EBV, dust, sigma, max_d = dustmaps3d(l, b, d)

df["EBV_3d"] = np.asarray(EBV)
df["dust"]   = np.asarray(dust)
df["sigma"]  = np.asarray(sigma)
df["max_distance"] = np.asarray(max_d)

df.to_csv("output.csv", index=False)

```
## ⚙️ 进阶用户提示

为了兼容性和易用性，本 dustmaps3d 做了一定的优化权衡，牺牲了部分性能以确保广泛环境下的稳定运行。

如果您对性能有更高要求（如支持多进程并行计算、通过命令行使用、更快的加载和 I/O 速度等），欢迎尝试由开发者 [SunnyHina](https://github.com/SunnyHina) 提供的实现：

👉 高性能版本地址：[SunnyHina/dustmaps3d](https://github.com/SunnyHina/dustmaps3d)

该版本采用更加现代化的数据加载方案，适合需要大规模批量处理的高级用户。

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

# 红化系数（Reddening Coefficient）

在获得 $E(B-V)$ 后，通常需要对观测到的星等或色指数进行消光校正（红化修正），以恢复恒星的内禀光度或颜色。对于任意波段的消光校正或色指数的红化修正，关键在于确定该波段或颜色对应的红化系数 $R_\lambda$。

## 红化修正公式

对某一观测波段或色指数 $\lambda_{\text{obs}}$ 进行消光校正，其内禀亮度或颜色 $\lambda_0$ 可通过下式计算：

$$
\lambda_0 = \lambda_{\text{obs}} - R_\lambda \cdot E(B-V)
$$

其中：
- $\lambda_{\text{obs}}$：观测得到的视星等或色指数；
- $R_\lambda$：该波段或色指数相对于 $ E(B-V) $ 的红化系数。

> **注意**：对于色指数（如 $G_{\rm BP}-G_{\rm RP}$），应使用对应色指数的红化系数 $ R_{\text{BP-RP}} $，而非单个波段的 $R_\lambda$。这里的 $R_\lambda$ 作为通用符号表示任意波段或颜色的红化系数。

## 推荐红化系数来源：Zhang et al. (2024)

**Zhang et al. (2024)** 基于 Gaia DR3 与 LAMOST DR7 中约 **500 万个共同源** 的 Gaia XP 光谱，采用恒星配对法对银河系消光曲线进行了直接测量，并利用其中约 **37 万个高质量光谱** 构建了银河系平均消光曲线。该工作提供了 **XP_Extinction_Toolkit** 工具包，支持基于实测消光曲线精确计算任意波段或色指数的红化系数。

- 📚 论文原文：[Zhang et al. (2024), ApJ, 972, 207](https://iopscience.iop.org/article/10.3847/1538-4357/ad613e)
- 💻 工具包地址：[https://github.com/vnohhf/XP_Extinction_Toolkit](https://github.com/vnohhf/XP_Extinction_Toolkit)

### 工具包核心功能函数：
- `star_ext(wavelength_or_band)`：计算指定波长或测光波段的红化系数 $R_\lambda$
- `star_reddening(color_index)`：计算指定色指数（如 `'BP-RP'`）的红化系数 $R_{\text{color}}$

## 快速查询工具

若仅需快速估算某一波段或色指数的红化系数，我们提供一个基于 Zhang et al. (2024) 数据的在线查询工具，用户可输入波长、波段名称或色指数，即时获取对应的 $R_\lambda$ 或 $R_{\text{color}}$ 值。

🌐 在线红化系数查询：  
[https://nadc.china-vo.org/data/dustmaps/](https://nadc.china-vo.org/data/dustmaps/)

> 该工具由中国虚拟天文台（China-VO）国家天文科学数据中心（NADC）提供支持，数据源自 Zhang et al. (2024) 的银河系平均消光曲线。

## 📜 引用说明

如果您在研究中使用了该工作或包，请引用以下两项：

- Wang, T. et al. (2025), *An all-sky 3D dust map based on Gaia and LAMOST*  
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