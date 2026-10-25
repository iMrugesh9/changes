#!/usr/bin/env bash
# Script to synchronize the changes documentation repository to Git remote

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check if there are modified or untracked files
if [ -n "$(git status --porcelain)" ]; then
    echo "[$TIMESTAMP] Changes detected in $REPO_DIR. Staging..."
    git add -A

    # Find which markdown files were added or modified
    MODIFIED_DOCS=$(git diff --cached --name-only | tr '\n' ', ' | sed 's/, $//')
    COMMIT_MSG="docs: sync updates (${MODIFIED_DOCS})"
    
    echo "[$TIMESTAMP] Committing: ${COMMIT_MSG}"
    git commit -m "${COMMIT_MSG}"
else
    echo "[$TIMESTAMP] Working tree clean. No changes to commit."
fi

# Push to remote if origin is configured
if git remote get-url origin >/dev/null 2>&1; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "[$TIMESTAMP] Pushing to origin/${CURRENT_BRANCH}..."
    if git push -u origin "${CURRENT_BRANCH}"; then
        echo "[$TIMESTAMP] Sync to Git remote completed successfully."
    else
        echo "[$TIMESTAMP] Warning: Failed to push to remote. Check network connection or remote credentials." >&2
        exit 1
    fi
else
    echo "[$TIMESTAMP] Notice: Remote 'origin' not configured yet. Committed locally only."
fi
