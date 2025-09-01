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

After obtaining $E(B-V)$, it is often necessary to apply extinction (reddening) corrections to the observed magnitudes or color indices in order to recover the intrinsic luminosity or color of a star. For extinction correction in any band or reddening correction of any color index, the key quantity is the reddening coefficient $R_\lambda$ for that band or color.

## Reddening–correction formula

To de-redden an observed band or color index $\lambda_{\text{obs}}$, the intrinsic value $\lambda_0$ is computed as
$$
\lambda_0 = \lambda_{\text{obs}} - R_\lambda \cdot E(B-V),
$$
where
- $\lambda_{\text{obs}}$: the observed apparent magnitude or color index;
- $R_\lambda$: the reddening coefficient of the band or color relative to $E(B-V)$.

> **Note.** For a color index (e.g., $G_{\rm BP}-G_{\rm RP}$), you should use the reddening coefficient for that color, $R_{\text{BP-RP}}$, rather than the single-band $R_\lambda$. Here, $R_\lambda$ is used as a generic symbol for the reddening coefficient of any band or color.

## Recommended source of reddening coefficients: Zhang et al. (2024)

**Zhang et al. (2024)** directly measured the Galactic extinction curve using Gaia DR3 and LAMOST DR7 Gaia XP spectra for roughly **5 million cross-matched sources**, and constructed a Galactic mean extinction curve from about **370,000 high-quality spectra** via a stellar-pair method. They provide the **XP_Extinction_Toolkit**, which enables precise computation of reddening coefficients for arbitrary bands or color indices based on the empirically derived extinction curve.

- 📚 Paper: [Zhang et al. (2024), ApJ, 972, 207](https://iopscience.iop.org/article/10.3847/1538-4357/ad613e)
- 💻 Toolkit: [https://github.com/vnohhf/XP_Extinction_Toolkit](https://github.com/vnohhf/XP_Extinction_Toolkit)

### Core functions in the toolkit
- `star_ext(wavelength_or_band)`: computes the reddening coefficient $R_\lambda$ for a specified wavelength or photometric band.
- `star_reddening(color_index)`: computes the reddening coefficient $R_{\text{color}}$ for a specified color index (e.g., `'BP-RP'`).

## Quick lookup tool

For a rapid estimate of the reddening coefficient for a given band or color index, an online query service based on the Zhang et al. (2024) extinction curve is available. Users can input a wavelength, band name, or color index to obtain the corresponding $R_\lambda$ or $R_{\text{color}}$.

🌐 Online reddening-coefficient query:  
[https://nadc.china-vo.org/data/dustmaps/](https://nadc.china-vo.org/data/dustmaps/)

> This service is provided by the National Astronomical Data Center (NADC) of the China-VO, with data derived from the Galactic mean extinction curve in Zhang et al. (2024).

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