#!/bin/bash
set -e
REPO_DIR="/config/ha_brainstorm_repo"

echo "Syncing brainstorm files from Home Assistant..."
rsync -av --delete --exclude="__pycache__" /config/custom_components/brainstorm/ "$REPO_DIR/custom_components/brainstorm/"

echo "Brainstorm repository synchronized successfully."

