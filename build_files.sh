#!/bin/bash

# Install dependencies
python3.12 -m pip install -r requirements.txt --break-system-packages

# Create the folder manually so Vercel doesn't complain if it's empty
mkdir -p staticfiles_build/static

# Run collectstatic
python3.12 manage.py collectstatic --noinput --clear