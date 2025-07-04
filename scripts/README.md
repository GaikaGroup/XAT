# GitHub Synchronization Scripts

This directory contains scripts to set up automatic synchronization between GitLab and GitHub repositories.

## Setup Instructions

### 1. Create a GitHub Repository

First, create a new repository on GitHub that will mirror your GitLab repository.

### 2. Set Up GitHub Remote and Automatic Sync

Run the setup script with your GitHub repository URL:

```bash
./scripts/setup_github_sync.sh <github_repo_url>
```

For example:

```bash
./scripts/setup_github_sync.sh https://github.com/username/HugDimonXat.git
```

This script will:
- Add GitHub as a remote repository
- Create a post-commit hook that automatically pushes all new commits to both GitLab and GitHub

### 3. Push All Existing Branches to GitHub

To push all existing branches and tags to GitHub:

```bash
./scripts/push_all_to_github.sh
```

## How It Works

The synchronization works through a Git post-commit hook that automatically pushes changes to both repositories whenever you make a commit.

### Post-Commit Hook

The post-commit hook is installed in `.git/hooks/post-commit` and contains the following logic:

1. Get the current branch
2. Push to GitLab (origin)
3. Push to GitHub

### Manual Push

If you need to manually push to both remotes:

```bash
# Push current branch to both remotes
git push origin <branch>
git push github <branch>

# Push all branches to both remotes
git push --all origin
git push --all github
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues with GitHub:

1. Ensure you have the correct permissions for the GitHub repository
2. Check that your GitHub credentials are properly configured
3. Consider using SSH URLs instead of HTTPS if you have SSH keys set up

### Merge Conflicts

If the repositories have diverged, you might encounter merge conflicts. In this case:

1. Pull from both remotes
2. Resolve conflicts
3. Commit and push again

```bash
git pull origin <branch>
git pull github <branch>
# Resolve conflicts
git commit -am "Resolve merge conflicts"
```

## Maintenance

The synchronization setup is persistent and will continue to work for all future commits. If you need to change the GitHub repository URL, simply run the setup script again with the new URL.