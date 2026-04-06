#!/usr/bin/env bash
set -euo pipefail
# Packaging script for Kid Classes Alexa Skill

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo "Cleaning previous build..."
rm -rf package function.zip

echo "Installing dependencies into package/"
python3 -m pip install -r requirements.txt -t package/

echo "Copying skill code..."
cp skill.py package/

echo "Creating function.zip..."
cd package
zip -r ../function.zip .
cd "$HERE"

echo "Created: $HERE/function.zip"
