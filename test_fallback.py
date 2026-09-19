import joblib, os, sys, traceback

mpath='models/model_rnn_fallback.joblib'
vpath='models/vectorizer_rnn_fallback.joblib'
print('MODEL EXISTS:', os.path.exists(mpath))
print('VECT EXISTS :', os.path.exists(vpath))
if not os.path.exists(mpath) or not os.path.exists(vpath):
    print('Missing fallback model or vectorizer files')
    sys.exit(2)
try:
    vec=joblib.load(vpath)
    clf=joblib.load(mpath)
    print('Loaded types:', type(vec), type(clf))
    text='This movie was amazing!'
    X=vec.transform([text])
    pred=clf.predict(X)
    print('PRED:', pred.tolist())
    if hasattr(clf,'predict_proba'):
        print('PROBA:', clf.predict_proba(X).tolist())
except Exception:
    traceback.print_exc()
    sys.exit(1)
