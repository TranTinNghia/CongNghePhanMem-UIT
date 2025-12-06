#!/bin/bash
# Build script for Render to use Python 3.10.12

# Install Python 3.10.12 using pyenv (if available)
if command -v pyenv &> /dev/null; then
    pyenv install -s 3.10.12
    pyenv local 3.10.12
fi

# Use Python 3.10 explicitly
python3.10 --version || python3 --version

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

