# dustmaps3d

**🌌 基于 Gaia 和 LAMOST 的全天三维尘埃消光图**

📄 *Wang et al. (2025),* *An all-sky 3D dust map based on Gaia and LAMOST* 
📌 DOI: [10.12149/101620](https://doi.org/10.12149/101620)

---

## 📦 安装方式

通过 pip 安装：

```bash
pip install dustmaps3d
```

⚠️ 安装时不会包含模型数据文件。  
首次运行时程序将自动从 GitHub 下载约 700MB 的模型数据（`data_v2.parquet`），无需手动下载。

---

## 🚀 使用示例

```python
from dustmaps3d import dustmaps3d

l = [120.0]    # 银经，单位：度
b = [30.0]     # 银纬，单位：度
d = [1.5]      # 距离，单位：kpc

EBV, dust, sigma, max_d = dustmaps3d(l, b, d)

print(f"EBV: {EBV.iloc[0]:.4f} [mag]")
print(f"Dust: {dust.iloc[0]:.4f} [mag/kpc]")
print(f"Sigma: {sigma[0]:.4f} [mag]")
print(f"Max distance: {max_d.iloc[0]:.4f} kpc")
```

---

## 🧠 函数说明

### `dustmaps3d(l, b, d)`

用于估算三维星际消光与相关物理量。

| 输入变量 | 类型           | 含义             | 单位       |
|----------|----------------|------------------|------------|
| `l`      | float / array  | 银经             | 度         |
| `b`      | float / array  | 银纬             | 度         |
| `d`      | float / array  | 日心距离         | kpc        |

#### 返回值：

| 输出变量   | 类型   | 含义                                     | 单位       |
|------------|--------|------------------------------------------|------------|
| `EBV`      | array  | 积分消光 E(B–V)                          | mag        |
| `dust`     | array  | E(B–V) 梯度，即尘埃密度近似             | mmag / pc  |
| `sigma`    | array  | E(B–V) 的估计不确定度                    | mag        |
| `max_d`    | array  | 本方向上模型可用的最大可靠距离          | kpc        |

所有输入输出均为 NumPy 数组，标量输入将自动转换为一维数组。

---

## ⚡ 计算效率

- 向量化实现，支持批量调用
- 在普通桌面计算机上处理 **1 亿颗恒星** 仅需约 10 分钟

---

## 📂 数据版本

本版本使用 `data_v2.parquet` 文件，首次运行时自动下载。  
下载地址：[GitHub Releases - v2.0](https://github.com/Grapeknight/dustmaps3d/releases/tag/v2.0)

---

## 📜 引用方式

> Wang, T. (2025). *An all-sky 3D dust map based on Gaia and LAMOST.*  
> DOI: [10.12149/101620](https://doi.org/10.12149/101620)

请在正式发表或研究中引用该论文以致谢作者工作。

---

## 📫 联系方式

如在使用本工具过程中有任何问题、建议或技术交流，欢迎通过 GitHub issue 或邮箱联系作者团队：

- 苑海波 教授: yuanhb@bnu.edu.cn  
- 王涛: wt@mail.bnu.edu.cn  

🔗 [GitHub Repository](https://github.com/Grapeknight/dustmaps3d)
