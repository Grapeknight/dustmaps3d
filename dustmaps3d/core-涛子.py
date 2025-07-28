from pathlib import Path
from functools import lru_cache
import pandas as pd
import numpy as np
from astropy.table import Table
from tqdm import tqdm
from platformdirs import user_data_dir
from astropy_healpix import HEALPix
from astropy import units as u
import warnings
import requests
import locale
import gzip

APP_NAME = "dustmaps3d"
DATA_VERSION = "v3"
DATA_FILENAME = f"data_{DATA_VERSION}.fits"
COMPRESSED_FILENAME = f"{DATA_FILENAME}.gz"

NADC_URL = "https://nadc.china-vo.org/res/file_upload/download?id=51931"
GITHUB_URL = f"https://github.com/Grapeknight/dustmaps3d/releases/download/{DATA_VERSION}/{COMPRESSED_FILENAME}"

LOCAL_DATA_PATH = Path(user_data_dir(APP_NAME)) / DATA_FILENAME
LOCAL_GZ_PATH = LOCAL_DATA_PATH.with_suffix(".fits.gz")


warnings.filterwarnings("ignore", category=RuntimeWarning, message="overflow encountered in exp")

APP_NAME = "dustmaps3d"
DATA_VERSION = "v3"  # ← 可根据版本号调整
DATA_FILENAME = f"data_{DATA_VERSION}.fits"        # ← 下载后解压出的文件
DATA_FILENAME_GZ = DATA_FILENAME + ".gz"           # ← 云端存储的压缩文件名

# 云端源（根据版本号动态设置）
NADC_URL = f"https://nadc.china-vo.org/res/file_upload/download?id=51931"
GITHUB_URL = f"https://github.com/Grapeknight/dustmaps3d/releases/download/{DATA_VERSION}/{DATA_FILENAME_GZ}"

# 本地路径
LOCAL_DATA_PATH = Path(user_data_dir(APP_NAME)) / DATA_FILENAME


_HEALPIX = HEALPix(nside=1024, order='ring')


class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

@lru_cache(maxsize=1)
def load_data():
    def is_china_user():
        try:
            lang, _ = locale.getdefaultlocale()
            return lang and lang.startswith("zh")
        except:
            return False

    def cleanup():
        for f in LOCAL_DATA_PATH.parent.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass

    def is_fits_valid(path):
        try:
            df = Table.read(path).to_pandas()
            return "max_distance" in df.columns and df.shape[0] > 100_000
        except Exception as e:
            print(f"[dustmaps3d] Invalid FITS file: {e}")
            return False

    def download_with_resume(url, path, max_retries=10, chunk_size=1024 * 1024):
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = path.with_suffix(".part")

        print(f"[dustmaps3d] Starting download from: {url}")
        for attempt in range(1, max_retries + 1):
            try:
                existing = temp_file.stat().st_size if temp_file.exists() else 0
                headers = {"Range": f"bytes={existing}-"} if existing else {}

                with requests.get(url, stream=True, headers=headers, timeout=30) as r:
                    if existing and r.status_code != 206:
                        print("[dustmaps3d] Server didn't support resume. Restarting.")
                        temp_file.unlink(missing_ok=True)
                        return download_with_resume(url, path, max_retries)

                    total = int(r.headers.get("Content-Length", 0)) + existing
                    with open(temp_file, "ab") as f, tqdm(
                        initial=existing,
                        total=total,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=path.name,
                    ) as bar:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
                break
            except Exception as e:
                print(f"[dustmaps3d] Download failed (attempt {attempt}/{max_retries}): {e}")
        else:
            raise RuntimeError("[dustmaps3d] Failed to download after multiple attempts.")

        temp_file.rename(path)
        print(f"[dustmaps3d] ✅ Data has been saved to: {path}")

    # === 主逻辑 ===
    if not LOCAL_DATA_PATH.exists() or not is_fits_valid(LOCAL_DATA_PATH):
        print(f"[dustmaps3d] Downloading {DATA_FILENAME} (~400MB)...")
        cleanup()
        primary_url = NADC_URL if is_china_user() else GITHUB_URL
        backup_url = GITHUB_URL if is_china_user() else NADC_URL

        try:
            print("[dustmaps3d] Trying primary source...")
            download_with_resume(primary_url, LOCAL_GZ_PATH)
        except Exception as e1:
            print("[dustmaps3d] Primary source failed. Trying backup...")
            cleanup()
            try:
                download_with_resume(backup_url, LOCAL_GZ_PATH)
            except Exception as e2:
                cleanup()
                raise RuntimeError(
                    f"[dustmaps3d] Failed to download from both sources.\n"
                    f"Primary: {e1}\nBackup: {e2}"
                )

        # 解压
        try:
            with gzip.open(LOCAL_GZ_PATH, 'rb') as f_in:
                with open(LOCAL_DATA_PATH, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            LOCAL_GZ_PATH.unlink()
            print(f"[dustmaps3d] ✅ Uncompressed to: {LOCAL_DATA_PATH}")
        except Exception as e:
            raise RuntimeError(f"[dustmaps3d] Failed to decompress file: {e}")

        # 再验证一次
        if not is_fits_valid(LOCAL_DATA_PATH):
            cleanup()
            raise RuntimeError("[dustmaps3d] Downloaded file is still invalid after extraction.")

    # 返回 DataFrame
    return Table.read(LOCAL_DATA_PATH).to_pandas()




def bubble_diffuse(x,h,b_lim,diffuse_dust_rho,bubble): 
    span = 0.01
    span_0 = h / np.sin(np.deg2rad(np.abs(b_lim)))
    Cum_EBV_0 = span_0 * diffuse_dust_rho
    C_0 = Cum_EBV_0 * (1 - np.exp(- (bubble) / span_0))
    f = (Cum_EBV_0 * (1 - np.exp(-x / span_0))) - C_0
    exp_n = np.exp(5 * bubble /span)
    a = 1 / exp_n
    b = 1 / (1 + exp_n)
    c = 0.5
    deta = C_0/((1+a)*(c-b))
    return np.where(x < (bubble), 0, f) + deta*(1+a)*((1 / (1 + np.exp(-5 * ((x - bubble)/span))) )-b)

def component4(x, b_lim, bubble, diffuse_dust_rho, h, distance_1, span_1, Cum_EBV_1, distance_2, span_2, Cum_EBV_2, distance_3, span_3, Cum_EBV_3, distance_4, span_4, Cum_EBV_4):
    Numerator_1 = Cum_EBV_1*(1/np.exp(5 * (distance_1 + (span_1*2) + bubble) /span_1) + 1)
    Numerator_2 = Cum_EBV_2*(1/np.exp(5 * (distance_2 + (span_2*2) + bubble)/span_2) + 1)
    Numerator_3 = Cum_EBV_3*(1/np.exp(5 * (distance_3 + (span_3*2) + bubble)/span_3) + 1)
    Numerator_4 = Cum_EBV_4*(1/np.exp(5 * (distance_4 + (span_4*2) + bubble)/span_4) + 1)
    
    return (bubble_diffuse(x,h,b_lim,diffuse_dust_rho,bubble)
                     
                    +((Numerator_1/ (1 + np.exp(-5 * ((x) - (distance_1 + (span_1*2) + bubble))/span_1))) 
                    -(Numerator_1 / (1 + np.exp(5 * (distance_1 + (span_1*2) + bubble)/span_1))))
                    
                    +((Numerator_2 / (1 + np.exp(-5 * ((x) - (distance_2 + (span_2*2) + bubble))/span_2))) 
                    -(Numerator_2 / (1 + np.exp(5 * ((distance_2 + (span_2*2) + bubble))/span_2))))

                    +((Numerator_3 / (1 + np.exp(-5 * ((x) - (distance_3 + (span_3*2) + bubble))/span_3))) 
                    -(Numerator_3 / (1 + np.exp(5 * ((distance_3 + (span_3*2) + bubble))/span_3))))

                    +((Numerator_4 / (1 + np.exp(-5 * ((x) - (distance_4 + (span_4*2) + bubble))/span_4))) 
                    -(Numerator_4 / (1 + np.exp(5 * ((distance_4 + (span_4*2) + bubble))/span_4))))
                    )       
 
def diffusion_derived_function(x, b_lim, diffuse_dust_rho, h ):
    span_0 = h / np.sin(np.deg2rad(np.abs(b_lim)))
    return diffuse_dust_rho * (np.exp(- x / span_0))

def sigmoid(x, a, b, c):
    return c / (1 + np.exp(-b * (x - a)))

def derivative_of_sigmoid(x, a, b, c):
    return b * c * sigmoid(x, a, b, 1) * (1 - (sigmoid(x, a, b, 1)))

def sigmoid_of_component(bubble, distance, span, Cum_EBV):
    a = distance + (2*span) + bubble
    b = 5 / span
    c = Cum_EBV*(1/np.exp(5 * a /span) + 1)
    return a, b, c

def derivative_of_component4(x, b_lim, bubble, diffuse_dust_rho, h, distance_1, span_1, Cum_EBV_1, distance_2, span_2, Cum_EBV_2, distance_3, span_3, Cum_EBV_3, distance_4, span_4, Cum_EBV_4):
    a_1, b_1, c_1 = sigmoid_of_component(bubble, distance_1, span_1, Cum_EBV_1)
    a_2, b_2, c_2 = sigmoid_of_component(bubble, distance_2, span_2, Cum_EBV_2)
    a_3, b_3, c_3 = sigmoid_of_component(bubble, distance_3, span_3, Cum_EBV_3)
    a_4, b_4, c_4 = sigmoid_of_component(bubble, distance_4, span_4, Cum_EBV_4)
    return (np.where(x < bubble, 0, diffusion_derived_function(x, b_lim, diffuse_dust_rho, h)) 
            + derivative_of_sigmoid(x, a_1, b_1, c_1) 
            + derivative_of_sigmoid(x, a_2, b_2, c_2) 
            + derivative_of_sigmoid(x, a_3, b_3, c_3) 
            + derivative_of_sigmoid(x, a_4, b_4, c_4) 
            )

def read_map(df):
    distance = df['distance'].fillna(df['max_distance'])
    EBV = component4(distance, df['b_lim'], df['bubble'], df['diffuse_dust_rho'], df['h'], 
                    df['distance_1'], df['span_1'], df['Cum_EBV_1'], 
                    df['distance_2'], df['span_2'], df['Cum_EBV_2'],
                    df['distance_3'], df['span_3'], df['Cum_EBV_3'],
                    df['distance_4'], df['span_4'], df['Cum_EBV_4'])
    dust = derivative_of_component4(distance, df['b_lim'], df['bubble'], df['diffuse_dust_rho'], df['h'], 
                    df['distance_1'], df['span_1'], df['Cum_EBV_1'], 
                    df['distance_2'], df['span_2'], df['Cum_EBV_2'],
                    df['distance_3'], df['span_3'], df['Cum_EBV_3'],
                    df['distance_4'], df['span_4'], df['Cum_EBV_4']) 
    sigma_finally = np.empty_like(df['sigma'], dtype=float)
    mask = distance < 1
    sigma_finally[mask] = np.nanmin(np.array([df['sigma'][mask], df['sigma_0_2'][mask]]), axis=0)
    mask = (distance >= 1) & (distance < 2)
    sigma_finally[mask] = np.nanmin(np.array([df['sigma'][mask], df['sigma_0_2'][mask], df['sigma_1_4'][mask]]), axis=0)
    mask = (distance >= 2) & (distance < 4)
    sigma_finally[mask] = np.nanmin(np.array([df['sigma_1_4'][mask], df['sigma_2_max'][mask]]), axis=0)
    mask = distance >= 4
    sigma_finally[mask] = df['sigma_2_max'][mask]
    return EBV, dust, pd.Series(sigma_finally, index=df.index), df['max_distance']



def _dustmaps3d_worker(args):
    l_chunk, b_chunk, d_chunk = args
    results = [dustmaps3d(l, b, d) for l, b, d in zip(l_chunk, b_chunk, d_chunk)]
    return list(zip(*results))  # (EBV, dust, sigma, max_d)

def dustmaps3d(l, b, d):
    """
    3D dust map (Wang et al. 2025).

    Parameters
    ----------
    l : np.ndarray
        Galactic longitude in degrees.
    b : np.ndarray
        Galactic latitude in degrees.
    d : np.ndarray
        Distance in kpc.
    n_process : int, optional
        Number of parallel processes to use. If None (default), the function runs in single-threaded mode.
        When set to an integer >= 1, the input data is split evenly across processes, and
        each process independently computes the dust values in parallel.

    Returns
    -------
    EBV : np.ndarray
        E(B–V) extinction value along the line of sight.
    dust : np.ndarray
        Dust density (d(EBV)/dx) in mag/kpc.
    sigma : np.ndarray
        Estimated uncertainty in E(B–V).
    max_distance : np.ndarray
        Maximum reliable distance along the line of sight for each direction.

    Notes
    -----
    - When using `n_process`, make sure `l`, `b`, `d` are arrays of equal length.
    - This function uses `multiprocessing.Pool` internally and is safe for CPU-bound batch queries.
    """

    l = np.atleast_1d(l)
    b = np.atleast_1d(b)
    d = np.atleast_1d(d)

    if not (len(l) == len(b) == len(d)):
        raise ValueError("l, b, d must be the same length")

    if np.isnan(l).any() or np.isnan(b).any():
        print("[dustmaps3d] Error: Input `l` and `b` must not contain NaN values.")
        raise ValueError("NaN values detected in `l` or `b`. These are not supported by HEALPix mapping.")
    
    df = load_data()
    pix_ids = _HEALPIX.lonlat_to_healpix(l * u.deg, b * u.deg)
    rows = df.iloc[pix_ids].copy()
    rows['distance'] = d
    EBV, dust, sigma_finally, max_d = read_map(rows)
    return EBV, dust, sigma_finally, max_d
