import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

# Vercel needs the app object to be named 'app' or exported as handler
handler = app