#!/usr/bin/env python3
"""
Simple run script for Jishu Backend
Alternative to running python app.py directly
"""

from app import app

if __name__ == '__main__':
  
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
