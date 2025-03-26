from flask import Flask, render_template, jsonify
import requests
import os
import datetime
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from app.py
from app import app

# This is the handler for Vercel serverless functions
def handler(request, context):
    return app