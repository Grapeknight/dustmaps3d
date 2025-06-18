# dustmaps3d

**🌌 An all-sky 3D dust extinction map based on Gaia and LAMOST**

📄 *Wang et al. (2025),* *An all-sky 3D dust map based on Gaia and LAMOST*  
📌 DOI: [10.12149/101620](https://doi.org/10.12149/101620)

---

## 📦 Installation

Install via pip:

```bash
pip install dustmaps3d
```

**Note:** Installing the package does *not* include the data file.  
The ~700 MB model data will be **automatically downloaded** from GitHub on **first use**.

---

## 🚀 Usage

```python
from dustmaps3d import dustmaps3d

l = [120.0]    # Galactic longitude in degrees
b = [30.0]     # Galactic latitude in degrees
d = [1.5]      # Distance in kpc

EBV, dust, sigma, max_d = dustmaps3d(l, b, d)

print(f"EBV: {EBV.iloc[0]:.4f} [mag]")
print(f"Dust: {dust.iloc[0]:.4f} [mag/kpc]")
print(f"Sigma: {sigma[0]:.4f} [mag]")
print(f"Max distance: {max_d.iloc[0]:.4f} kpc")

```

---

## 🧠 Function Description

### `dustmaps3d(l, b, d)`

Estimates 3D dust extinction and related quantities for given galactic coordinates and distances.

| Input         | Type            | Description                          | Unit         |
|---------------|------------------|--------------------------------------|--------------|
| `l`           | float or array   | Galactic longitude                   | degrees (°)  |
| `b`           | float or array   | Galactic latitude                    | degrees (°)  |
| `d`           | float or array   | Heliocentric distance                | kpc          |

#### Returns:

| Output        | Type            | Description                                         | Unit         |
|---------------|------------------|-----------------------------------------------------|--------------|
| `EBV`         | array            | Cumulative extinction E(B–V)                        | mag          |
| `dust`        | array            | E(B–V) gradient (∂E/∂d), tracing dust density       | mmag / pc    |
| `sigma`       | array            | Estimated uncertainty in E(B–V)                     | mag          |
| `max_d`       | array            | Maximum reliable distance along the line of sight   | kpc          |

All inputs and outputs are NumPy arrays. Scalar inputs will be automatically converted to arrays.

---

## ⚡ Performance

- Fully vectorized implementation
- ~10 minutes to evaluate **100 million stars** on a modern desktop

---

## 📂 Data Version

This version uses `data_v2.parquet`, released under [v2.0](https://github.com/Grapeknight/dustmaps3d/releases/tag/v2.0).

---

## 📜 Citation

If you use this package or model, please cite:

> Wang, T. (2025). *An all-sky 3D dust map based on Gaia and LAMOST.*  
> DOI: [10.12149/101620](https://doi.org/10.12149/101620)

---

## 🛠️ License

This project is open-source and distributed under the MIT License.

---

## 📫 Contact

If you have any questions, suggestions, or encounter issues using this package,  
please feel free to contact the authors via GitHub issues or email.

- Prof. Yuan Haibo: yuanhb@bnu.edu.cn  
- Wang Tao: wt@mail.bnu.edu.cn

🔗 [GitHub Repository](https://github.com/Grapeknight/dustmaps3d)