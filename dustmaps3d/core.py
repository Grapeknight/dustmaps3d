from pathlib import Path
from functools import lru_cache
import pandas as pd
import numpy as np
import urllib.request
from tqdm import tqdm
from platformdirs import user_data_dir
from astropy_healpix import HEALPix
from astropy import units as u
import warnings
import requests
from multiprocessing import Pool, cpu_count

warnings.filterwarnings("ignore", category=RuntimeWarning, message="overflow encountered in exp")

APP_NAME = "dustmaps3d"
DATA_VERSION = "v2.2"
DATA_FILENAME = f"data_{DATA_VERSION}.parquet"
DATA_URL = f"https://github.com/Grapeknight/dustmaps3d/releases/download/{DATA_VERSION}/{DATA_FILENAME}"
LOCAL_DATA_PATH = Path(user_data_dir(APP_NAME)) / DATA_FILENAME

_HEALPIX = HEALPix(nside=1024, order='ring')


class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

@lru_cache(maxsize=1)
def load_data():
    def is_parquet_valid(path):
        try:
            if path.stat().st_size < 100 * 1024 * 1024:
                raise ValueError("File too small to be valid.")
            with open(path, "rb") as f:
                head = f.read(1024)
                if b"<html" in head.lower():
                    raise ValueError("File appears to be an HTML error page.")
            pd.read_parquet(path, engine="fastparquet", columns=["max_distance"])
            return True
        except Exception as e:
            print(f"[dustmaps3d] Detected corrupt or incomplete file: {e}")
            return False

    def cleanup():
        for f in LOCAL_DATA_PATH.parent.glob("*"):
            try:
                f.unlink()
            except Exception as e:
                print(f"[dustmaps3d] Failed to delete {f}: {e}")

    def download_with_resume(url, path, chunk_size=1024 * 1024, max_retries=10):
        import time
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = path.with_suffix(path.suffix + ".part")

        for attempt in range(1, max_retries + 1):
            try:
                existing_size = temp_file.stat().st_size if temp_file.exists() else 0
                headers = {"Range": f"bytes={existing_size}-"} if existing_size > 0 else {}

                with requests.get(url, stream=True, headers=headers, timeout=30) as response:
                    if existing_size > 0 and response.status_code != 206:
                        print("[dustmaps3d] Warning: server did not honor Range request. Restarting download.")
                        temp_file.unlink(missing_ok=True)
                        return download_with_resume(url, path, chunk_size, max_retries)

                    total_size = int(response.headers.get("Content-Length", 0)) + existing_size

                    with open(temp_file, "ab") as f, tqdm(
                        initial=existing_size,
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=path.name,
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
                break
            except Exception as e:
                print(f"[dustmaps3d] Download failed (attempt {attempt}/{max_retries}): {e}")
                time.sleep(2 ** attempt)
        else:
            raise RuntimeError(f"[dustmaps3d] Download failed after {max_retries} attempts.")

        if path.exists():
            path.unlink()
        temp_file.rename(path)

    if not LOCAL_DATA_PATH.exists() or not is_parquet_valid(LOCAL_DATA_PATH):
        print(f"[dustmaps3d] Downloading {DATA_FILENAME} with resume support (~400MB)...")
        cleanup()
        try:
            download_with_resume(DATA_URL, LOCAL_DATA_PATH)
        except Exception as e:
            cleanup()
            raise RuntimeError(f"[dustmaps3d] Failed to download {DATA_FILENAME}: {e}")

        if not is_parquet_valid(LOCAL_DATA_PATH):
            print("[dustmaps3d] File appears invalid even after download. Cleaning up and retrying...")
            cleanup()
            return load_data()

    return pd.read_parquet(LOCAL_DATA_PATH, engine="fastparquet")




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


def _process_chunk(df_chunk):
    """
    Worker function for multiprocessing. Processes a chunk of the DataFrame.
    It's defined at the top level of the module to be pickleable.
    """
    load_data() 
    
    try:
        ebv, dust, sigma, max_d = dustmaps3d(df_chunk['l'].values, df_chunk['b'].values, df_chunk['d'].values)
        
        df_chunk['EBV'] = ebv.values
        df_chunk['dust'] = dust.values
        df_chunk['sigma'] = sigma.values
        df_chunk['max_distance'] = max_d.values
        
        return df_chunk
    except Exception as e:
        print(f"A worker process failed with an error: {e}")
        return pd.DataFrame()


def dustmaps3d_from_df(df, l_col='l', b_col='b', d_col='d', n_process=8, chunk_size=100_000):
    """
    Calculates dust properties for a large dataset in a pandas DataFrame using multiprocessing.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing sky coordinates and distances.
    l_col : str, optional
        Column name for Galactic longitude in degrees, by default 'l'.
    b_col : str, optional
        Column name for Galactic latitude in degrees, by default 'b'.
    d_col : str, optional
        Column name for distance in kpc, by default 'd'.
    n_process : int, optional
        Number of parallel processes to use, by default 8.
    chunk_size : int, optional
        Number of rows each process handles at a time, by default 100,000.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with calculated dust properties ('EBV', 'dust', 'sigma', 'max_distance') appended.
    """
    for col in [l_col, b_col, d_col]:
        if col not in df.columns:
            raise ValueError(f"Input DataFrame must contain column '{col}'")

    input_df = df[[l_col, b_col, d_col]].rename(columns={l_col: 'l', b_col: 'b', d_col: 'd'})
    
    tasks = [input_df.iloc[i:i + chunk_size] for i in range(0, len(input_df), chunk_size)]
    
    results = []
    print(f"[dustmaps3d] Starting parallel processing with {n_process} cores...")
    
    with Pool(processes=n_process) as pool:
        pbar = tqdm(pool.imap_unordered(_process_chunk, tasks), total=len(tasks), desc="Processing Chunks")
        for res_chunk in pbar:
            results.append(res_chunk)

    print("[dustmaps3d] Parallel processing finished. Merging results...")
    
    if not results:
        print("[dustmaps3d] Warning: No results were returned from worker processes.")
        return df.copy()

    result_df = pd.concat(results).sort_index()
    
    final_df = df.copy()
    final_df['EBV'] = result_df['EBV']
    final_df['dust'] = result_df['dust']
    final_df['sigma'] = result_df['sigma']
    final_df['max_distance'] = result_df['max_distance']
    
    return final_df