#!/bin/bash
set -e
REPO_DIR="/config/ha_brainstorm_repo"

echo "Syncing brainstorm files from repository into Home Assistant..."
rsync -av --delete --exclude="__pycache__" "$REPO_DIR/custom_components/brainstorm/" /config/custom_components/brainstorm/
cp -f "$REPO_DIR/www/brainstorm-card.js" /config/www/brainstorm-card.js
cp -f "$REPO_DIR/www/brainstorm-mindmap-card.js" /config/www/brainstorm-mindmap-card.js
cp -f "$REPO_DIR/www/brainstorm-logo.png" /config/www/brainstorm-logo.png 2>/dev/null || true
cp -f "$REPO_DIR/www/brainstorm-logo.svg" /config/www/brainstorm-logo.svg 2>/dev/null || true
cp -f "$REPO_DIR/www/brainstorm-icon.png" /config/www/brainstorm-icon.png 2>/dev/null || true

echo "Home Assistant files updated successfully from repository."

