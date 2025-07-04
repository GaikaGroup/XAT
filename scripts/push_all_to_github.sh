#!/bin/bash

# Script to push all branches to GitHub
# Usage: ./scripts/push_all_to_github.sh

set -e

# Check if GitHub remote exists
if ! git remote | grep -q "github"; then
    echo "Error: GitHub remote does not exist"
    echo "Please run ./scripts/setup_github_sync.sh <github_repo_url> first"
    exit 1
fi

# Get all branches
echo "Fetching all branches..."
git fetch origin

# Push all branches to GitHub
echo "Pushing all branches to GitHub..."
git push github --all

# Push all tags to GitHub
echo "Pushing all tags to GitHub..."
git push github --tags

echo "All branches and tags have been pushed to GitHub successfully!"
echo "GitHub remote: $(git remote get-url github)"