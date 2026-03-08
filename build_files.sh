#!/bin/bash

echo "Building the project..."

# Add the --break-system-packages flag to bypass the PEP 668 protection
python3.12 -m pip install -r requirements.txt --break-system-packages

echo "Collecting static files..."
# Use the same python version for manage.py
python3.12 manage.py collectstatic --noinput --clear