from pathlib import Path
from functools import lru_cache
import pandas as pd
import numpy as np
import urllib.request
from tqdm import tqdm
from platformdirs import user_data_dir
from astropy_healpix import HEALPix
from astropy import units as u
import multiprocessing as mp
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")

APP_NAME = "dustmaps3d"
DATA_VERSION = "v2.1"
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
    if not LOCAL_DATA_PATH.exists():
        print(f"[dustmaps3d] Downloading {DATA_FILENAME} (~700MB)...")
        LOCAL_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=DATA_FILENAME) as t:
            urllib.request.urlretrieve(DATA_URL, LOCAL_DATA_PATH, reporthook=t.update_to)
    return pd.read_parquet(LOCAL_DATA_PATH)


def bubble_diffuse(x, h, b_lim, diffuse_dust_rho, bubble):
    span = 0.01
    span_0 = h / np.sin(np.deg2rad(np.abs(b_lim)))
    Cum_EBV_0 = span_0 * diffuse_dust_rho
    C_0 = Cum_EBV_0 * (1 - np.exp(-bubble / span_0))

    exp_term = np.exp(5 * bubble / span)
    a = 1 / exp_term
    b = 1 / (1 + exp_term)
    c = 0.5
    deta = C_0 / ((1 + a) * (c - b))

    res = np.zeros_like(x)
    mask = x >= bubble
    res[mask] = (Cum_EBV_0 * (1 - np.exp(-x[mask] / span_0)) - C_0)[mask]
    res += deta * (1 + a) * ((1 / (1 + np.exp(-5 * ((x - bubble) / span)))) - b)
    return res


def component4(x, b_lim, bubble, diffuse_dust_rho, h,
               d1, s1, c1, d2, s2, c2, d3, s3, c3, d4, s4, c4):
    def sigmoid_contrib(d, s, c):
        term = d + 2 * s + bubble
        numerator = c * (1 / np.exp(5 * term / s) + 1)
        return numerator, term, s

    terms = [sigmoid_contrib(d, s, c) for d, s, c in [(d1, s1, c1), (d2, s2, c2), (d3, s3, c3), (d4, s4, c4)]]

    result = bubble_diffuse(x, h, b_lim, diffuse_dust_rho, bubble)
    for numerator, term, s in terms:
        result += numerator / (1 + np.exp(-5 * (x - term) / s)) - numerator / (1 + np.exp(5 * term / s))
    return result


def diffusion_derived_function(x, b_lim, diffuse_dust_rho, h):
    span_0 = h / np.sin(np.deg2rad(np.abs(b_lim)))
    return diffuse_dust_rho * np.exp(-x / span_0)


def sigmoid(x, a, b, c):
    return c / (1 + np.exp(-b * (x - a)))


def derivative_of_sigmoid(x, a, b, c):
    sig = sigmoid(x, a, b, 1)
    return b * c * sig * (1 - sig)


def sigmoid_of_component(bubble, distance, span, Cum_EBV):
    a = distance + 2 * span + bubble
    b = 5 / span
    c = Cum_EBV * (1 / np.exp(5 * a / span) + 1)
    return a, b, c


def derivative_of_component4(x, b_lim, bubble, diffuse_dust_rho, h,
                             d1, s1, c1, d2, s2, c2, d3, s3, c3, d4, s4, c4):
    a1, b1, c1 = sigmoid_of_component(bubble, d1, s1, c1)
    a2, b2, c2 = sigmoid_of_component(bubble, d2, s2, c2)
    a3, b3, c3 = sigmoid_of_component(bubble, d3, s3, c3)
    a4, b4, c4 = sigmoid_of_component(bubble, d4, s4, c4)

    base = np.zeros_like(x)
    mask = x >= bubble
    base[mask] = diffusion_derived_function(x[mask], b_lim[mask], diffuse_dust_rho[mask], h[mask])

    return base + \
        derivative_of_sigmoid(x, a1, b1, c1) + \
        derivative_of_sigmoid(x, a2, b2, c2) + \
        derivative_of_sigmoid(x, a3, b3, c3) + \
        derivative_of_sigmoid(x, a4, b4, c4)


def map(df):
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

    mask1 = distance < 1
    sigma_finally[mask1] = np.nanmin([df['sigma'][mask1], df['sigma_0_2'][mask1]], axis=0)

    mask2 = (distance >= 1) & (distance < 2)
    sigma_finally[mask2] = np.nanmin([df['sigma'][mask2], df['sigma_0_2'][mask2], df['sigma_1_4'][mask2]], axis=0)

    mask3 = (distance >= 2) & (distance < 4)
    sigma_finally[mask3] = np.nanmin([df['sigma_1_4'][mask3], df['sigma_2_max'][mask3]], axis=0)

    sigma_finally[distance >= 4] = df['sigma_2_max'][distance >= 4]

    return EBV, dust, sigma_finally, df['max_distance']




def _dustmaps3d_worker(args):
    l_chunk, b_chunk, d_chunk = args
    results = [dustmaps3d(l, b, d) for l, b, d in zip(l_chunk, b_chunk, d_chunk)]
    return list(zip(*results))  # (EBV, dust, sigma, max_d)

def dustmaps3d(l, b, d, n_process: int = None):
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

    if n_process is None or len(l) == 1:
        df = load_data()
        pix_ids = _HEALPIX.lonlat_to_healpix(l * u.deg, b * u.deg)
        rows = df.iloc[pix_ids].copy()
        rows['distance'] = d
        EBV, dust, sigma_finally, max_d = map(rows)
        return EBV, dust, sigma_finally, max_d

    else:
        chunks = np.array_split(np.arange(len(l)), n_process)
        args = [(l[chunk], b[chunk], d[chunk]) for chunk in chunks if len(chunk) > 0]

        with mp.Pool(processes=n_process) as pool:
            results = pool.map(_dustmaps3d_worker, args)

        ebv_list, dust_list, sigma_list, maxd_list = [], [], [], []
        for ebv, dust, sigma, maxd in results:
            ebv_list.append(np.concatenate(ebv))
            dust_list.append(np.concatenate(dust))
            sigma_list.append(np.concatenate(sigma))
            maxd_list.append(np.concatenate(maxd))

        return (
            np.concatenate(ebv_list),
            np.concatenate(dust_list),
            np.concatenate(sigma_list),
            np.concatenate(maxd_list)
        )
