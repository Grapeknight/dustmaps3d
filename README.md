**Read this in: [English](README.md) | [中文](README.zh-CN.md)**


# dustmaps3d

🌌 **An all-sky 3D dust extinction map based on Gaia and LAMOST**

📄 *Wang et al. (2025),* *An all-sky 3D dust map based on Gaia and LAMOST*  
📌 DOI: [10.12149/101620](https://doi.org/10.12149/101620)

📦 *A Python package for easy access to the 3D dust map*  
📌 DOI: [10.12149/101619](https://nadc.china-vo.org/res/r101619/)

---

## 📦 Installation

Install via pip:

```bash
pip install dustmaps3d
```

## 📦 Data File Notice

> ⚠️ The package **does not include the data file**. Upon first use, a ~400MB model file will be automatically downloaded from GitHub or the NADC mirror.

### 🚀 Automatic Download Mechanism

- When `dustmaps3d()` is called, the package will attempt to download the file `data_v3.fits.gz`;
- After the download, the file will be automatically decompressed into `data_v3.fits` and cached locally;
- Subsequent calls will directly load from the cache without re-downloading.

### 🌐 What If the Download Fails?

If you're outside China, the default download source is GitHub. However, network issues (like `connect timeout`) may still occur. The package supports fallback to an alternative mirror:

- ✅ **Primary source** (international users): [GitHub Releases](https://github.com/Grapeknight/dustmaps3d/releases)
- 🌀 **Backup source** (Chinese mirror): NADC (currently under review, coming soon)

If both sources fail, you can manually download the data file.

### 📥 Manual Download (Recommended for Chinese Users)

1. Visit the mirror link (coming soon)
2. Download the file: `data_v3.fits.gz`
3. Decompress it into `data_v3.fits`
4. Place the file in the local cache directory (the location will be printed the first time you run the package)

> Example path on Windows:  
> `C:\Users\<username>\AppData\Local\dustmaps3d\data_v3.fits`

> Example path on Linux/macOS:  
> `/home/<username>/.local/share/dustmaps3d/data_v3.fits`

---

## 🚀 Usage

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

**Batch example with FITS:**

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


## 🧠 Function Description

### `dustmaps3d(l, b, d, n_process=None)`

Estimates 3D dust extinction and related quantities for given galactic coordinates and distances.

| Input       | Type         | Description                        | Unit     |
|-------------|--------------|------------------------------------|----------|
| `l`         | np.ndarray   | Galactic longitude                 | degrees  |
| `b`         | np.ndarray   | Galactic latitude                  | degrees  |
| `d`         | np.ndarray   | Distance                           | kpc      |

#### Returns:

| Output       | Type         | Description                           | Unit     |
|--------------|--------------|---------------------------------------|----------|
| `EBV`        | np.ndarray   | E(B–V) extinction                     | mag      |
| `dust`       | np.ndarray   | Dust density (d(EBV)/dx)             | mag/kpc  |
| `sigma`      | np.ndarray   | Estimated uncertainty in E(B–V)      | mag      |
| `max_d`      | np.ndarray   | Maximum reliable distance            | kpc      |

> If `d` contains `NaN`, it will be automatically replaced by the maximum reliable distance along that line of sight (`max_d`).
> 
> If the input `d` exceeds `max_d`, it indicates the point lies beyond the model's reliable range. The returned values in this case are extrapolated and **not guaranteed to be accurate**.

---

## ⚡ Performance

- Fully vectorized and optimized with NumPy
- On a modern personal computer, evaluating **100 million stars takes only ~100 seconds**

---


## 📜 Citation

If you use this model or the Python package, please cite both:

- Wang, T. (2025), *An all-sky 3D dust map based on Gaia and LAMOST*. DOI: [10.12149/101620](https://doi.org/10.12149/101620)  
- *dustmaps3d: A Python package for easy access to the 3D dust map*. DOI: [10.12149/101619](https://nadc.china-vo.org/res/r101619/)

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