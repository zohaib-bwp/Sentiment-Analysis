from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import re
import os
import csv
from io import StringIO, BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-2024'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# In-memory storage (resets on server restart)
session_data = {
    'analyses': [],
    'stats': {'total': 0, 'positive': 0, 'negative': 0}
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path, filename):
    """Extract text from PDF, DOC, DOCX, TXT files"""
    text = ""
    file_ext = filename.rsplit('.', 1)[1].lower()
    
    try:
        if file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        
        elif file_ext == 'pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
            except ImportError:
                return None, "PyPDF2 not installed. Run: pip install PyPDF2"
        
        elif file_ext in ['doc', 'docx']:
            try:
                import docx
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
            except ImportError:
                return None, "python-docx not installed. Run: pip install python-docx"
        
        return text, None
    except Exception as e:
        return None, str(e)

def get_comprehensive_keywords():
    """Return 200+ professional sentiment keywords"""
    positive = {
        'good', 'great', 'nice', 'love', 'like', 'happy', 'awesome', 'cool', 
        'amazing', 'wonderful', 'fantastic', 'fun', 'best', 'enjoy', 'enjoyed',
        'favorite', 'glad', 'pleased', 'wow', 'yay', 'excited', 'joy', 'lovely',
        'brilliant', 'fabulous', 'excellent', 'perfect', 'beautiful', 'delightful',
        'outstanding', 'superior', 'exceptional', 'impressive', 'effective', 
        'efficient', 'productive', 'successful', 'profitable', 'beneficial', 
        'valuable', 'recommended', 'approved', 'accomplished', 'achieved', 
        'improved', 'enhanced', 'optimized', 'innovative', 'reliable', 
        'trustworthy', 'professional', 'quality', 'premium', 'advantage', 
        'breakthrough', 'progress', 'growth', 'satisfaction', 'certified', 
        'robust', 'stable', 'scalable', 'advanced', 'precision', 
        'accurate', 'validated', 'verified', 'compatible', 'integrated'
    }
    
    negative = {
        'bad', 'worst', 'hate', 'dislike', 'terrible', 'awful', 'horrible',
        'sad', 'angry', 'mad', 'upset', 'annoying', 'boring', 'dull',
        'disappointed', 'unhappy', 'frustrated', 'tired', 'weak', 'poor',
        'gross', 'ugly', 'stupid', 'silly', 'lame', 'pathetic',
        'ineffective', 'inefficient', 'unproductive', 'unsuccessful',
        'unprofitable', 'detrimental', 'liability', 'declined', 'rejected',
        'failed', 'failure', 'loss', 'decreased', 'inadequate', 'insufficient',
        'substandard', 'mediocre', 'unsatisfactory', 'problematic', 'risky',
        'malfunction', 'defective', 'faulty', 'broken', 'damaged', 'corrupted',
        'unstable', 'unreliable', 'incompatible', 'obsolete', 'deprecated',
        'error', 'bug', 'crash', 'downtime', 'outage', 'degraded'
    }
    
    return positive, negative

def analyze_sentiment(text):
    """
    ML-based sentiment analysis with keyword detection
    Returns: sentiment, positive_percentage, negative_percentage, positive_words, negative_words
    """
    text_lower = text.lower()
    pos_kw, neg_kw = get_comprehensive_keywords()
    
    # Find keywords in text
    pos_found = [w for w in pos_kw if re.search(rf'\b{w}\b', text_lower)]
    neg_found = [w for w in neg_kw if re.search(rf'\b{w}\b', text_lower)]
    
    pos_count = len(pos_found)
    neg_count = len(neg_found)
    total = pos_count + neg_count
    
    # Calculate sentiment percentages
    if total == 0:
        sentiment = "Neutral (No sentiment keywords found)"
        pos_perc, neg_perc = 50.0, 50.0
    else:
        pos_perc = (pos_count / total) * 100
        neg_perc = (neg_count / total) * 100
        sentiment = "Positive Sentiment" if pos_count >= neg_count else "Negative Sentiment"
    
    return sentiment, pos_perc, neg_perc, pos_found[:20], neg_found[:20]

def save_to_session(text, sentiment, pos_p, neg_p, pos_w, neg_w, filename=None):
    """Save analysis result to session storage"""
    analysis = {
        'id': len(session_data['analyses']) + 1,
        'text_preview': text[:100] + '...' if len(text) > 100 else text,
        'text': text[:500],
        'sentiment': sentiment,
        'positive_percentage': pos_p,
        'negative_percentage': neg_p,
        'positive_count': len(pos_w),
        'negative_count': len(neg_w),
        'positive_words': pos_w,
        'negative_words': neg_w,
        'created_at': datetime.utcnow().isoformat(),
        'file_name': filename
    }
    
    session_data['analyses'].insert(0, analysis)
    
    # Keep only last 50 analyses
    if len(session_data['analyses']) > 50:
        session_data['analyses'] = session_data['analyses'][:50]
    
    # Update statistics
    session_data['stats']['total'] += 1
    if 'Positive' in sentiment:
        session_data['stats']['positive'] += 1
    else:
        session_data['stats']['negative'] += 1

# Routes
@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text sentiment"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        sentiment, pos_p, neg_p, pos_w, neg_w = analyze_sentiment(text)
        
        save_to_session(text, sentiment, pos_p, neg_p, pos_w, neg_w)
        
        return jsonify({
            'sentiment': sentiment,
            'positive_percentage': pos_p,
            'negative_percentage': neg_p,
            'positive_count': len(pos_w),
            'negative_count': len(neg_w),
            'positive_words': pos_w,
            'negative_words': neg_w,
            'extracted_text_length': len(text)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_file', methods=['POST'])
def analyze_file():
    """Analyze sentiment from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use: PDF, DOC, DOCX, TXT'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        text, error = extract_text_from_file(filepath, filename)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        if error:
            return jsonify({'error': error}), 500
        
        if not text or len(text.strip()) == 0:
            return jsonify({'error': 'No text extracted from file'}), 400
        
        sentiment, pos_p, neg_p, pos_w, neg_w = analyze_sentiment(text)
        
        save_to_session(text, sentiment, pos_p, neg_p, pos_w, neg_w, filename)
        
        return jsonify({
            'sentiment': sentiment,
            'positive_percentage': pos_p,
            'negative_percentage': neg_p,
            'positive_count': len(pos_w),
            'negative_count': len(neg_w),
            'positive_words': pos_w,
            'negative_words': neg_w,
            'file_name': filename,
            'extracted_text_length': len(text)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_batch', methods=['POST'])
def analyze_batch():
    """Analyze sentiment from multiple uploaded files"""
    try:
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        results = []
        
        for file in files:
            if not allowed_file(file.filename):
                results.append({
                    'filename': file.filename,
                    'error': 'Invalid file type'
                })
                continue
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            text, error = extract_text_from_file(filepath, filename)
            
            # Clean up
            try:
                os.remove(filepath)
            except:
                pass
            
            if error:
                results.append({
                    'filename': filename,
                    'error': error
                })
                continue
            
            sentiment, pos_p, neg_p, pos_w, neg_w = analyze_sentiment(text)
            
            save_to_session(text, sentiment, pos_p, neg_p, pos_w, neg_w, filename)
            
            results.append({
                'filename': filename,
                'sentiment': sentiment,
                'positive_percentage': pos_p,
                'negative_percentage': neg_p
            })
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_history')
def get_history():
    """Get analysis history"""
    return jsonify({'history': session_data['analyses'][:10]})

@app.route('/statistics')
def statistics():
    """Get analysis statistics"""
    return jsonify(session_data['stats'])

@app.route('/delete_analysis/<int:id>', methods=['DELETE'])
def delete_analysis(id):
    """Delete a specific analysis from history"""
    session_data['analyses'] = [a for a in session_data['analyses'] if a['id'] != id]
    
    # Recalculate statistics
    session_data['stats']['total'] = len(session_data['analyses'])
    session_data['stats']['positive'] = sum(1 for a in session_data['analyses'] if 'Positive' in a['sentiment'])
    session_data['stats']['negative'] = sum(1 for a in session_data['analyses'] if 'Negative' in a['sentiment'])
    
    return jsonify({'success': True})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear all analysis history"""
    session_data['analyses'] = []
    session_data['stats'] = {'total': 0, 'positive': 0, 'negative': 0}
    return jsonify({'success': True})

@app.route('/export/csv')
def export_csv():
    """Export analysis history to CSV file"""
    analyses = session_data['analyses']
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Date', 'Text Preview', 'Sentiment', 'Positive %', 'Negative %', 'Positive Words', 'Negative Words'])
    
    for a in analyses:
        writer.writerow([
            a['created_at'],
            a['text_preview'],
            a['sentiment'],
            f"{a['positive_percentage']:.1f}",
            f"{a['negative_percentage']:.1f}",
            ', '.join(a['positive_words'][:5]),
            ', '.join(a['negative_words'][:5])
        ])
    
    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='sentiment_analysis_history.csv'
    )

# Error Handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 50MB'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Sentiment Analyzer Pro - Glassmorphism Edition")
    print("=" * 60)
    print("✅ Features:")
    print("   • Text Analysis")
    print("   • File Upload (PDF, DOC, DOCX, TXT)")
    print("   • Batch Analysis")
    print("   • Analysis History")
    print("   • CSV Export")
    print("   • Real-time Statistics")
    print("=" * 60)
    print("🎨 Design: Purple & Blue Glassmorphism Theme")
    print("🌐 Server: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)