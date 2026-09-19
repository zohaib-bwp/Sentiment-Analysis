import os
import joblib
import logging

logger = logging.getLogger(__name__)

BEST_PATH = 'models/model_best.joblib'
FALLBACK_MODEL_PATH = 'models/model_rnn_fallback.joblib'
FALLBACK_VECTOR_PATH = 'models/vectorizer_rnn_fallback.joblib'


def load_model():
    """Attempt to load the preferred model, fall back to (vectorizer + model) pair.
    Returns (model, vectorizer, source_path, error_messages).
    """
    errors = []
    model = None
    vectorizer = None
    source = None

    if os.path.exists(BEST_PATH):
        try:
            model = joblib.load(BEST_PATH)
            source = BEST_PATH
            logger.info(f'Loaded model from {BEST_PATH}')
            return model, None, source, errors
        except Exception as e:
            msg = f'Failed loading {BEST_PATH}: {e}'
            errors.append(msg)
            logger.warning(msg)

    # Try Keras RNN model (model + tokenizer)
    rnn_model_path = os.path.join('models', 'model_rnn.h5')
    rnn_tokenizer_path = os.path.join('models', 'tokenizer_rnn.pkl')
    if os.path.exists(rnn_model_path) and os.path.exists(rnn_tokenizer_path):
        try:
            # import lazily to avoid hard TF dependency unless used
            from tensorflow.keras.models import load_model
            import pickle
            tokenizer = None
            model = load_model(rnn_model_path)
            with open(rnn_tokenizer_path, 'rb') as fh:
                tokenizer = pickle.load(fh)
            source = rnn_model_path
            logger.info(f'Loaded Keras RNN model from {rnn_model_path}')
            return model, tokenizer, source, errors
        except Exception as e:
            msg = f'Failed loading Keras RNN model/tokenizer: {e}'
            errors.append(msg)
            logger.warning(msg)

    # Try fallback pair
    if os.path.exists(FALLBACK_MODEL_PATH) and os.path.exists(FALLBACK_VECTOR_PATH):
        try:
            vectorizer = joblib.load(FALLBACK_VECTOR_PATH)
            model = joblib.load(FALLBACK_MODEL_PATH)
            source = FALLBACK_MODEL_PATH
            logger.info(f'Loaded fallback model + vectorizer from {FALLBACK_MODEL_PATH}')
            return model, vectorizer, source, errors
        except Exception as e:
            msg = f'Failed loading fallback model/vectorizer: {e}'
            errors.append(msg)
            logger.warning(msg)

    errors.append('No usable model found in models/.')
    logger.warning('No usable model found in models/. Please train or provide a model.')
    return None, None, None, errors
