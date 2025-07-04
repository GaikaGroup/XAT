#!/bin/bash

# Script to set up automatic syncing to GitHub
# Usage: ./scripts/setup_github_sync.sh <github_repo_url>

set -e

# Check if GitHub repository URL is provided
if [ -z "$1" ]; then
    echo "Error: GitHub repository URL is required"
    echo "Usage: ./scripts/setup_github_sync.sh <github_repo_url>"
    exit 1
fi

GITHUB_REPO_URL="$1"

# Add GitHub as a remote
echo "Adding GitHub as a remote..."
if git remote | grep -q "github"; then
    echo "GitHub remote already exists, updating URL..."
    git remote set-url github "$GITHUB_REPO_URL"
else
    echo "Adding new GitHub remote..."
    git remote add github "$GITHUB_REPO_URL"
fi

# Create post-commit hook to automatically push to both remotes
HOOK_PATH=".git/hooks/post-commit"
echo "Setting up post-commit hook at $HOOK_PATH..."

cat > "$HOOK_PATH" << 'EOF'
#!/bin/bash

# Get the current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Push to GitLab (origin)
echo "Pushing to GitLab (origin)..."
git push origin "$BRANCH"

# Push to GitHub
echo "Pushing to GitHub..."
git push github "$BRANCH"

echo "Changes pushed to both GitLab and GitHub successfully!"
EOF

# Make the hook executable
chmod +x "$HOOK_PATH"

echo "Setup complete! All commits will now be automatically pushed to both GitLab and GitHub."
echo "GitLab remote: $(git remote get-url origin)"
echo "GitHub remote: $(git remote get-url github)"
echo ""
echo "To test, make a commit and it should automatically push to both remotes."