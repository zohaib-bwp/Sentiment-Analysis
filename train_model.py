import os
import joblib
import json
import hashlib
import subprocess
from datetime import datetime
import pandas as pd
import numpy as _np
import sklearn as _sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

DATA_PATH = 'data/imdb_50k.csv'
MODEL_DIR = 'models'
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data(limit=None):
    df = pd.read_csv(DATA_PATH)
    
    # Check if the expected columns exist
    if 'review' not in df.columns or 'sentiment' not in df.columns:
        print(f"Error: Expected columns 'review' and 'sentiment' not found.")
        print(f"Available columns: {df.columns.tolist()}")
        print("\nPlease ensure the data file has been downloaded and processed correctly.")
        print("Run: python download_data.py")
        raise KeyError("Missing 'review' and/or 'sentiment' columns in CSV")
    
    if limit:
        df = df.sample(limit, random_state=42)
    return df['review'].values, df['sentiment'].values

def train_and_eval():
    X, y = load_data()
    # dataset info
    dataset_rows = len(X)
    dataset_sha256 = None
    try:
        if os.path.exists(DATA_PATH):
            h = hashlib.sha256()
            with open(DATA_PATH, 'rb') as fh:
                for chunk in iter(lambda: fh.read(8192), b''):
                    h.update(chunk)
            dataset_sha256 = h.hexdigest()
    except Exception:
        dataset_sha256 = None

    # CHECKSUM VERIFICATION: optional expected checksum via env var or .sha256 file
    expected_sha = os.environ.get('EXPECTED_DATASET_SHA256')
    sha_file_paths = [DATA_PATH + '.sha256', os.path.join(os.path.dirname(DATA_PATH), 'dataset.sha256')]
    for p in sha_file_paths:
        try:
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as fh:
                    txt = fh.read().strip()
                    if txt:
                        # support formats like "<sha>  filename" or just sha
                        expected_sha = txt.split()[0]
                        break
        except Exception:
            pass

    if expected_sha:
        if dataset_sha256 is None:
            raise RuntimeError('Unable to compute dataset checksum; aborting training.')
        if dataset_sha256 != expected_sha:
            raise RuntimeError(f"Dataset checksum mismatch: computed {dataset_sha256} != expected {expected_sha}. Aborting training.")

    # git info (optional)
    git_info = None
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
        status = subprocess.check_output(['git', 'status', '--porcelain'], stderr=subprocess.DEVNULL).decode().strip()
        git_info = {'commit': commit, 'dirty': bool(status)}
    except Exception:
        git_info = None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    models = {
        'nb': MultinomialNB(),
        'lr': LogisticRegression(max_iter=1000),
        'svm': LinearSVC(max_iter=10000)
    }
    results = {}
    for name, clf in models.items():
        print(f'\nTraining {name}...')
        pipe = Pipeline([('tfidf', TfidfVectorizer(max_features=20000, ngram_range=(1,2))), ('clf', clf)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print('Accuracy:', acc)
        print(classification_report(y_test, preds))
        results[name] = {'model': pipe, 'accuracy': acc}
        model_path = os.path.join(MODEL_DIR, f'model_{name}.joblib')
        joblib.dump(pipe, model_path)
        # Build metadata
        metadata = {
            'name': name,
            'accuracy': float(acc),
            'saved_at': datetime.utcnow().isoformat() + 'Z',
            'sklearn_version': _sklearn.__version__,
            'numpy_version': _np.__version__,
            'model_file': os.path.basename(model_path),
        }
        # include dataset and git info when available
        try:
            metadata['dataset'] = {
                'path': DATA_PATH,
                'rows': int(dataset_rows) if dataset_rows is not None else None,
                'sha256': dataset_sha256,
            }
        except Exception:
            pass
        if git_info is not None:
            metadata['git'] = git_info
        # Attempt to collect vectorizer info
        try:
            if hasattr(pipe, 'named_steps') and 'tfidf' in pipe.named_steps:
                tf = pipe.named_steps['tfidf']
                vocab = None
                try:
                    vocab = len(tf.vocabulary_)
                except Exception:
                    vocab = None
                metadata['vectorizer'] = {
                    'type': type(tf).__name__,
                    'vocabulary_size': vocab,
                    'ngram_range': getattr(tf, 'ngram_range', None),
                    'max_features': getattr(tf, 'max_features', None)
                }
        except Exception:
            pass
        # Write metadata next to model file
        try:
            with open(model_path + '.metadata.json', 'w', encoding='utf-8') as fh:
                json.dump(metadata, fh, indent=2)
        except Exception as e:
            print('Warning: failed to write metadata for', model_path, e)
    # Save best
    best = max(results.items(), key=lambda x: x[1]['accuracy'])
    best_model_path = os.path.join(MODEL_DIR, 'model_best.joblib')
    joblib.dump(best[1]['model'], best_model_path)
    # Save metadata for best model
    best_meta = {
        'selected': best[0],
        'accuracy': float(best[1]['accuracy']),
        'saved_at': datetime.utcnow().isoformat() + 'Z',
        'sklearn_version': _sklearn.__version__,
        'numpy_version': _np.__version__,
        'model_file': os.path.basename(best_model_path),
    }
    # include dataset and git info for best
    try:
        best_meta['dataset'] = {
            'path': DATA_PATH,
            'rows': int(dataset_rows) if dataset_rows is not None else None,
            'sha256': dataset_sha256,
        }
    except Exception:
        pass
    if git_info is not None:
        best_meta['git'] = git_info
    try:
        # attempt to include vectorizer info if present
        pipe = best[1]['model']
        if hasattr(pipe, 'named_steps') and 'tfidf' in pipe.named_steps:
            tf = pipe.named_steps['tfidf']
            try:
                vocab = len(tf.vocabulary_)
            except Exception:
                vocab = None
            best_meta['vectorizer'] = {
                'type': type(tf).__name__,
                'vocabulary_size': vocab,
                'ngram_range': getattr(tf, 'ngram_range', None),
                'max_features': getattr(tf, 'max_features', None)
            }
    except Exception:
        pass
    try:
        with open(best_model_path + '.metadata.json', 'w', encoding='utf-8') as fh:
            json.dump(best_meta, fh, indent=2)
    except Exception as e:
        print('Warning: failed to write metadata for best model', e)
    print('\nBest model:', best[0], 'accuracy=', best[1]['accuracy'])

if __name__ == '__main__':
    train_and_eval()
