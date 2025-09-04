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

## 📦 Data File Instructions

> ⚠️ The package **does not include the data file**. A ~400MB model file will be automatically downloaded on first use from GitHub or NADC.

### 🚀 Auto Download Mechanism

- When `dustmaps3d()` is called, it will try to download `data_v3.fits.gz`;
- After download, it will automatically extract the file to `data_v3.fits` and cache it locally;
- On future runs, the file will be read from the local cache without re-downloading.

- ✅ For international users, the primary source is: [GitHub Releases](https://github.com/Grapeknight/dustmaps3d/releases)
- 🌀 If GitHub download fails, it will automatically fallback to: [NADC Data Center](https://nadc.china-vo.org/res/file_upload/download?id=51939)

> On Chinese systems, the order is reversed — NADC is used as the primary source.

---

### 🌐 What if download fails?

If download fails (e.g. `connect timeout`), you can manually download and place the file in the cache directory:

1. Visit one of the following links:  
   🇨🇳 [NADC Data Center (for China)](https://nadc.china-vo.org/res/r101662/)  
   🌍 [GitHub Releases (global)](https://github.com/Grapeknight/dustmaps3d/releases)

2. Download: `data_v3.fits.gz`
3. Extract to: `data_v3.fits`
4. Place the extracted file in the local cache directory (the location is printed on first use)

> Example path (Windows):  
> `C:\Users\<username>\AppData\Local\dustmaps3d\data_v3.fits`

> Example path (Linux/macOS):  
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

**Batch example with CSV:**

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
## ⚙️ Tips for Advanced Users

To ensure broad compatibility and ease of use, the official `dustmaps3d` package makes certain design trade-offs that may come at the cost of peak performance.

If you have higher performance needs — such as support for multi-processing, command-line usage, or faster data loading and I/O — consider using the alternative implementation by [SunnyHina](https://github.com/SunnyHina):

👉 High-performance version: [SunnyHina/dustmaps3d](https://github.com/SunnyHina/dustmaps3d)

This version adopts a more modern data loading architecture and is better suited for advanced users working with large-scale or batch processing workflows.


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

# Reddening Coefficient

After obtaining $E(B-V)$, it is usually necessary to correct the observed magnitudes or color indices for extinction (reddening correction) in order to recover the intrinsic luminosity or color of stars.  
For extinction correction in any photometric band or reddening correction of any color index, the key is to determine the corresponding reddening coefficient $R_\lambda$ or $R_(a-b)$.

We provide a detailed explanation of how to obtain reddening coefficients on the [3D Dust Map Platform](https://nadc.china-vo.org/data/dustmaps/), along with an online calculator that allows users to quickly compute the required coefficients by simply entering the input parameters.

## 📜 Citation

If you use this model or the Python package, please cite both:

- Wang, T. et al. (2025), *An all-sky 3D dust map based on Gaia and LAMOST*. DOI: [10.12149/101620](https://doi.org/10.12149/101620)  
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