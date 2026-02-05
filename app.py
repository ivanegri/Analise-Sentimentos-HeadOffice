from flask import Flask, request, jsonify
from sentiment import SentimentAnalyzer

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    # 1. Check for file upload (multipart/form-data)
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        filename = file.filename.lower()
        text = ""
        
        if filename.endswith('.pdf'):
            from file_parser import parse_pdf
            text = parse_pdf(file)
        elif filename.endswith('.docx'):
            from file_parser import parse_docx
            text = parse_docx(file)
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8', errors='ignore')
        else:
            return jsonify({'error': 'Unsupported file type. Use PDF, DOCX or TXT.'}), 400
            
        if not text.strip():
             return jsonify({'error': 'Could not extract text from file or file is empty'}), 400
             
        result = SentimentAnalyzer.analyze_conversation(text)
        return jsonify(result)

    # 2. Check for JSON body
    data = request.get_json(force=True, silent=True)
    
    if not data:
        return jsonify({'error': 'Invalid request. Send JSON body or upload a file.'}), 400
        
    # Check if it's a list (batch) or single object
    if isinstance(data, list):
        results = []
        for item in data:
            result = SentimentAnalyzer.analyze_conversation(item)
            # Make sure to include some ID if present to map back
            cid = item.get('_id') or item.get('id')
            if cid:
                result['id'] = cid
            results.append(result)
        return jsonify(results)
    else:
        # Single mode
        result = SentimentAnalyzer.analyze_conversation(data)
        return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/version', methods=['GET'])
def version():
    """Returns version info to verify deployment"""
    return jsonify({
        'version': '3.0',
        'sentiment_levels': 7,
        'features': ['weighted_scoring', 'real_7_scores', 'reduced_neutral_bias'],
        'labels': [
            'Very Negative',
            'Negative', 
            'Slightly Negative',
            'Neutral',
            'Slightly Positive',
            'Positive',
            'Very Positive'
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
