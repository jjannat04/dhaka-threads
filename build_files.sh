#!/bin/bash
python3.12 -m pip install -r requirements.txt --break-system-packages
# Ensure whitenoise is active
python3.12 -m pip install whitenoise --break-system-packages 

mkdir -p staticfiles_build/static

# The --clear flag ensures we don't have old broken paths
python3.12 manage.py collectstatic --noinput --clear