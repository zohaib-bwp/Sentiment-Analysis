import os
from pathlib import Path
from typing import Optional

import pandas as pd


# Primary local dataset used by the project
FINAL_DATASET_PATH = Path("data/final_dataset.csv")

def _read_local_csv(path: Path) -> Optional[pd.DataFrame]:
    if path.exists():
        return pd.read_csv(path)
    return None


def load_books_dataset() -> Optional[pd.DataFrame]:
    """
    Try local files first; then try kagglehub if available.
    Returns a DataFrame or None.
    """
    # 1) Prefer any local copies
    candidates = [
        FINAL_DATASET_PATH,
        Path("data/books.csv"),
        Path("data/imdb_50k.csv"),
        Path("data/swiggy.csv"),
         Path("data/final_dataset.csv"),
    ]
    for p in candidates:
        df = _read_local_csv(p)
        if df is not None:
            print(f"Loaded local dataset: {p}")
            return df

    # 2) Try kagglehub (optional dependency)
    try:
        import kagglehub
        from kagglehub import KaggleDatasetAdapter

        file_path = ""
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "mihikaajayjadhav/books-dataset-15k-books-across-100-categories",
            file_path,
        )
        print("Loaded dataset via kagglehub (remote).")
        return df
    except Exception as e:
        # Broad except to handle ImportError, network or API errors gracefully.
        print("kagglehub unavailable or failed:", str(e))

    # 3) Try Kaggle CLI/data if installed (best-effort)
    try:
        # avoid import at top-level so linters won't fail if not installed
        import kaggle
        # example: download dataset and load a CSV if user has kaggle credentials configured
        dataset_ref = "mihikaajayjadhav/books-dataset-15k-books-across-100-categories"
        target_dir = Path("data/kaggle_books")
        target_dir.mkdir(parents=True, exist_ok=True)
        kaggle.api.dataset_download_files(dataset_ref, path=str(target_dir), unzip=True)
        # try to find a CSV in the downloaded folder
        for f in target_dir.iterdir():
            if f.suffix.lower() == ".csv":
                print("Loaded dataset via kaggle CLI.")
                return pd.read_csv(f)
    except Exception:
        pass

    print("No dataset available locally or via kaggle/kagglehub. To enable remote loading, install kagglehub or kaggle.")
    return None


if __name__ == "__main__":
    df = load_books_dataset()
    if df is not None:
        print("First 5 rows:\n", df.head())
    else:
        print("Dataset not loaded.")