#!/bin/bash
set -e
REPO_DIR="/config/ha_brainstorm_repo"

echo "Syncing brainstorm files from repository into Home Assistant..."
rsync -av --delete --exclude="__pycache__" "$REPO_DIR/custom_components/brainstorm/" /config/custom_components/brainstorm/

echo "Home Assistant files updated successfully from repository."

