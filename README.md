# Sentiment Project

Quick commands and troubleshooting.

Run training (wrapper):

```powershell
python train.py
```

Start API server:

```powershell
python app.py
# or, for deterministic runs without reloader:
python -c "from app import app; app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)"
```

Test `/predict` (PowerShell):

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/predict' -Method Post -ContentType 'application/json' -Body '{"text":"This movie was amazing!"}'
```

Run tests locally:

```powershell
python -m pip install -r requirements.txt
pytest -q
```

Re-download dataset (PowerShell script):

```powershell
.
\scripts\redownload_dataset.ps1
```

CI: a GitHub Actions workflow is included at `.github/workflows/ci.yml` to run the tests.
# Sentiment Analysis Project (IMDB 50k)

This project contains code to reproduce a Sentiment Analysis pipeline on the IMDB 50k Movie Reviews dataset.
It includes scripts to download and prepare the dataset, train classical ML models (TF-IDF + Logistic Regression / Naive Bayes / SVM),
evaluate results, and run a small Flask API for predictions.

## Contents
- download_data.py         # Download & prepare dataset (from Stanford / Kaggle)
- train_model.py           # Train models and save best model
- predict.py               # Simple script to load model and predict
- app.py                   # Minimal Flask app to serve predictions
- notebook.ipynb           # Jupyter notebook with end-to-end steps (exported as .py too)
- requirements.txt         # Python dependencies
- README.md                # This file

## How to use (quick)
1. Create a virtual environment and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Download and prepare dataset:
   ```bash
   python download_data.py
   ```
   This will download the IMDB Large Movie Review dataset from Stanford and create `data/imdb_50k.csv`.
3. Train models:
   ```bash
   python train_model.py
   ```
 
![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)
   Trained model and TF-IDF vectorizer are saved in `models/`.
4. Evaluate & predict using `predict.py` or run the Flask app:
   ```bash
   python app.py
   ```

## Dataset sources / references
- Large Movie Review Dataset (Stanford). Download link used by script: http://ai.stanford.edu/~amaas/data/sentiment/.
- Kaggle mirrors of IMDB 50k dataset are also available.

For more details see the Jupyter notebook included.
 
## Notes: metadata, checksums and Docker

- Metadata: training saves a `.metadata.json` file next to each model in `models/` (e.g. `model_best.joblib.metadata.json`).
   These files include accuracy, saved timestamp, scikit-learn and numpy versions, vectorizer info when available, dataset SHA256 and git commit (if available).

- Dataset checksum verification: training will check the dataset SHA256 if you provide it via the `EXPECTED_DATASET_SHA256` environment variable or by creating a `data/imdb_50k.csv.sha256` (or `data/dataset.sha256`) file containing the expected hex checksum. If the checksum doesn't match, training aborts.

- Docker: a `Dockerfile` is included. Build and run:

```bash
docker build -t sentiment-app .
docker run -p 5000:5000 sentiment-app
```

## Development tips

- To inspect model metadata from Python:

```python
from model_metadata import load_metadata, list_all_metadata
print(load_metadata('model_best.joblib'))
```

- To run the Flask app behind gunicorn locally (recommended for production-like testing):

```bash
gunicorn -w 1 -b 0.0.0.0:5000 app:app
```
