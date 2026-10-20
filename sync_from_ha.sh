#!/bin/bash
set -e
REPO_DIR="/config/ha_brainstorm_repo"

echo "Syncing brainstorm files from Home Assistant..."
rsync -av --delete --exclude="__pycache__" /config/custom_components/brainstorm/ "$REPO_DIR/custom_components/brainstorm/"
cp -f /config/www/brainstorm-card.js "$REPO_DIR/www/brainstorm-card.js"
cp -f /config/www/brainstorm-logo.png "$REPO_DIR/www/brainstorm-logo.png" 2>/dev/null || true

echo "Brainstorm repository synchronized successfully."
