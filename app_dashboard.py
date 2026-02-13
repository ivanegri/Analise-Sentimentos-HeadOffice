"""
Sentiment Analysis Dashboard — Flask Web Application
Runs on port 5001, independent from the API on port 5000.
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from sentiment import SentimentAnalyzer
from feedback_store import (
    save_feedback, load_feedbacks, clear_feedbacks,
    get_correction_offsets, get_feedback_stats
)
import json
import uuid
import os
import gc
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory session results store (keyed by session_id)
# For production, this could be Redis or a database
analysis_sessions = {}

# Directory to store session results on disk
SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sessions')
os.makedirs(SESSIONS_DIR, exist_ok=True)


def label_to_css_class(label: str) -> str:
    """Convert a sentiment label to a CSS class name."""
    return label.lower().replace(' ', '-')


def get_message_preview(conversation: dict) -> str:
    """Extract a preview of the customer messages from a conversation."""
    messages = conversation.get('Full Conversation', [])
    customer_msgs = []
    for m in messages:
        if not m.get('sender') or m.get('sender') == []:
            msg = m.get('message', '').strip()
            if msg:
                customer_msgs.append(msg)
    
    if customer_msgs:
        return ' | '.join(customer_msgs[:3])[:120]
    
    # Fallback: first message
    if messages:
        return messages[0].get('message', '')[:120]
    
    return '(sem mensagens)'


def save_session(session_id: str, data: dict):
    """Persist session results to disk."""
    path = os.path.join(SESSIONS_DIR, f'{session_id}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def load_session(session_id: str) -> dict | None:
    """Load session results from disk."""
    path = os.path.join(SESSIONS_DIR, f'{session_id}.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def list_sessions() -> list:
    """List all saved analysis sessions."""
    sessions = []
    if not os.path.exists(SESSIONS_DIR):
        return sessions
    
    for fname in sorted(os.listdir(SESSIONS_DIR), reverse=True):
        if fname.endswith('.json'):
            sid = fname.replace('.json', '')
            data = load_session(sid)
            if data:
                sessions.append({
                    'id': sid,
                    'filename': data.get('filename', 'Desconhecido'),
                    'count': data.get('count', 0),
                    'date': data.get('date', '')
                })
    return sessions[:10]  # Show last 10


@app.route('/')
def index():
    """Upload page."""
    sessions = list_sessions()
    return render_template('upload.html', sessions=sessions)


@app.route('/upload', methods=['POST'])
def upload():
    """Process uploaded JSON file."""
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado.', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('index'))
    
    if not file.filename.lower().endswith('.json'):
        flash('Formato não suportado. Use um arquivo JSON.', 'error')
        return redirect(url_for('index'))
    
    try:
        data = json.load(file)
    except json.JSONDecodeError:
        flash('Arquivo JSON inválido.', 'error')
        return redirect(url_for('index'))
    
    if not isinstance(data, list):
        flash('O JSON deve conter uma lista de conversas.', 'error')
        return redirect(url_for('index'))
    
    # Check if refinement is available
    offsets = get_correction_offsets()
    use_refinement = offsets['count'] > 0
    
    # Process each conversation
    results = []
    for i, conversation in enumerate(data):
        conv_id = conversation.get('_id') or conversation.get('id') or str(i)
        
        try:
            if use_refinement:
                analysis = SentimentAnalyzer.analyze_conversation_with_refinement(conversation)
            else:
                analysis = SentimentAnalyzer.analyze_conversation(conversation)
                analysis['refined'] = False
        except Exception as e:
            print(f"Error analyzing conversation {conv_id}: {e}")
            analysis = {
                'score': 50.0,
                'sentiment_label': 'Neutral',
                'level_scores': {},
                'refined': False
            }
        
        results.append({
            'id': conv_id,
            'score': analysis['score'],
            'sentiment_label': analysis['sentiment_label'],
            'level_scores': analysis.get('level_scores', {}),
            'refined': analysis.get('refined', False),
            'preview': get_message_preview(conversation),
            'ai_agent': conversation.get('AI Agent', '').strip(),
            'link': conversation.get('Link', ''),
            'created_at': conversation.get('CreatedAt', ''),
            'human_escalation': conversation.get('HumanEscalation', False),
            'css_class': label_to_css_class(analysis['sentiment_label']),
            'messages': conversation.get('Full Conversation', [])
        })
        
        # Garbage collection every 50 items
        if (i + 1) % 50 == 0:
            gc.collect()
    
    # Create session
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
    session_data = {
        'filename': file.filename,
        'count': len(results),
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'results': results,
        'refinement_active': use_refinement,
        'feedback_count': offsets['count']
    }
    
    save_session(session_id, session_data)
    
    return redirect(url_for('results', session_id=session_id))


@app.route('/results/<session_id>')
def results(session_id):
    """Display analysis results."""
    data = load_session(session_id)
    
    if not data:
        flash('Sessão de análise não encontrada.', 'error')
        return redirect(url_for('index'))
    
    results_list = data['results']
    
    # Calculate metrics
    scores = [r['score'] for r in results_list]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    
    positive_labels = {'Very Positive', 'Positive', 'Slightly Positive'}
    negative_labels = {'Very Negative', 'Negative', 'Slightly Negative'}
    
    positive_count = sum(1 for r in results_list if r['sentiment_label'] in positive_labels)
    negative_count = sum(1 for r in results_list if r['sentiment_label'] in negative_labels)
    total = len(results_list)
    
    positive_pct = round(positive_count / total * 100, 1) if total else 0
    negative_pct = round(negative_count / total * 100, 1) if total else 0
    
    # Distribution
    label_order = [
        ('Very Positive', 'very-positive'),
        ('Positive', 'positive'),
        ('Slightly Positive', 'slightly-positive'),
        ('Neutral', 'neutral'),
        ('Slightly Negative', 'slightly-negative'),
        ('Negative', 'negative'),
        ('Very Negative', 'very-negative'),
    ]
    
    label_counts = {}
    for r in results_list:
        lbl = r['sentiment_label']
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
    
    distribution = []
    for label, css_class in label_order:
        count = label_counts.get(label, 0)
        pct = round(count / total * 100, 1) if total else 0
        distribution.append({
            'label': label,
            'css_class': css_class,
            'count': count,
            'pct': pct
        })
    
    return render_template('results.html',
        session=data,
        results=results_list,
        avg_score=avg_score,
        positive_pct=positive_pct,
        negative_pct=negative_pct,
        distribution=distribution,
        refinement_active=data.get('refinement_active', False),
        feedback_count=data.get('feedback_count', 0)
    )


@app.route('/feedback', methods=['POST'])
def feedback():
    """Save a user correction (AJAX endpoint)."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    conversation_id = data.get('conversation_id')
    original_label = data.get('original_label')
    corrected_label = data.get('corrected_label')
    original_score = data.get('original_score', 50.0)
    
    if not all([conversation_id, original_label, corrected_label]):
        return jsonify({'error': 'Missing fields'}), 400
    
    if original_label == corrected_label:
        return jsonify({'error': 'Same label, no correction needed'}), 400
    
    save_feedback(conversation_id, original_label, corrected_label, original_score)
    
    return jsonify({
        'success': True,
        'message': f'Correção salva: {original_label} → {corrected_label}'
    })


@app.route('/feedbacks')
def feedbacks_page():
    """Show all feedbacks."""
    feedbacks = load_feedbacks()
    stats = get_feedback_stats()
    offsets = get_correction_offsets()
    
    return render_template('feedbacks.html',
        feedbacks=feedbacks,
        stats=stats,
        offsets=offsets
    )


@app.route('/feedbacks/clear', methods=['POST'])
def clear_feedbacks_route():
    """Clear all feedbacks."""
    clear_feedbacks()
    flash('Todos os feedbacks foram removidos. O modelo voltou ao comportamento original.', 'success')
    return redirect(url_for('feedbacks_page'))


if __name__ == '__main__':
    print("=" * 50)
    print("  Sentiment Analysis Dashboard")
    print("  http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)
