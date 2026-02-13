"""
Feedback Store — persists user corrections for model refinement.
Stores feedbacks in feedbacks.json and calculates correction offsets.
"""

import json
import os
from datetime import datetime
from collections import defaultdict

DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedbacks.json')

# Map labels to numeric positions for offset calculation
LABEL_ORDER = [
    'Very Negative',
    'Negative',
    'Slightly Negative',
    'Neutral',
    'Slightly Positive',
    'Positive',
    'Very Positive'
]

LABEL_TO_INDEX = {label: i for i, label in enumerate(LABEL_ORDER)}


def load_feedbacks() -> list:
    """Load all stored feedbacks."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_feedback(conversation_id: str, original_label: str, corrected_label: str, original_score: float):
    """Save a single user correction."""
    feedbacks = load_feedbacks()
    
    # Remove existing feedback for same conversation (allow re-correction)
    feedbacks = [fb for fb in feedbacks if fb.get('conversation_id') != conversation_id]
    
    feedbacks.append({
        'conversation_id': conversation_id,
        'original_label': original_label,
        'corrected_label': corrected_label,
        'original_score': original_score,
        'timestamp': datetime.now().isoformat()
    })
    
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)


def clear_feedbacks():
    """Delete all feedbacks."""
    if os.path.exists(FEEDBACK_FILE):
        os.remove(FEEDBACK_FILE)


def get_correction_offsets() -> dict:
    """
    Calculate a score offset based on accumulated feedbacks.
    
    Returns a dict with:
      - 'score_offset': float — value to add to raw score (can be negative)
      - 'label_shifts': dict — per original_label, the average shift in labels
      - 'count': int — total feedbacks used
    
    The idea: if the user keeps correcting "Neutral" → "Positive",
    we learn to push borderline scores upward.
    """
    feedbacks = load_feedbacks()
    
    if not feedbacks:
        return {'score_offset': 0.0, 'label_shifts': {}, 'count': 0}
    
    # Calculate average label shift per original label
    shifts_by_label = defaultdict(list)
    all_shifts = []
    
    for fb in feedbacks:
        orig = fb.get('original_label', '')
        corr = fb.get('corrected_label', '')
        
        if orig in LABEL_TO_INDEX and corr in LABEL_TO_INDEX:
            shift = LABEL_TO_INDEX[corr] - LABEL_TO_INDEX[orig]
            shifts_by_label[orig].append(shift)
            all_shifts.append(shift)
    
    if not all_shifts:
        return {'score_offset': 0.0, 'label_shifts': {}, 'count': 0}
    
    # Global score offset: each label step ≈ ~14.3 score points (100/7)
    avg_shift = sum(all_shifts) / len(all_shifts)
    score_offset = avg_shift * 14.3
    
    # Per-label average shifts
    label_shifts = {}
    for label, shifts in shifts_by_label.items():
        label_shifts[label] = round(sum(shifts) / len(shifts), 2)
    
    return {
        'score_offset': round(score_offset, 2),
        'label_shifts': label_shifts,
        'count': len(feedbacks)
    }


def get_feedback_stats() -> dict:
    """Get summary statistics of feedbacks."""
    feedbacks = load_feedbacks()
    
    if not feedbacks:
        return {'total': 0, 'corrections_by_label': {}}
    
    corrections = defaultdict(lambda: defaultdict(int))
    for fb in feedbacks:
        orig = fb.get('original_label', 'Unknown')
        corr = fb.get('corrected_label', 'Unknown')
        corrections[orig][corr] += 1
    
    return {
        'total': len(feedbacks),
        'corrections_by_label': dict(corrections)
    }
