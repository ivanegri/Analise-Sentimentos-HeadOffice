#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
# The Pysentimiento model will download on the first run if not cached.
python app.py
