#!/bin/bash
npm config set prefix "$HOME/.npm-global"
mkdir -p "$HOME/.npm-global"

PROFILE_FILE=""
if [ -f "$HOME/.zshrc" ]; then
  PROFILE_FILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
  PROFILE_FILE="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
  PROFILE_FILE="$HOME/.bash_profile"
fi

if [ -n "$PROFILE_FILE" ]; then
  if ! grep -q "PATH=\"\$HOME/.npm-global/bin:\$PATH\"" "$PROFILE_FILE"; then
    echo "export PATH=\"\$HOME/.npm-global/bin:\$PATH\"" >> "$PROFILE_FILE"
    echo "Added npm-global to PATH in $PROFILE_FILE"
  else
    echo "PATH already contains npm-global in $PROFILE_FILE"
  fi
fi

npm init -y
npm install --save-dev tailwindcss postcss autoprefixer

if [ -f "package.json" ]; then
  if ! grep -q "\"tailwind\":" "package.json"; then
    sed -i.bak "/\"scripts\": {/a\
    \"tailwind\": \"tailwindcss\",\
    \"build:css\": \"tailwindcss -i ./src/input.css -o ./dist/output.css\",\
    \"watch:css\": \"tailwindcss -i ./src/input.css -o ./dist/output.css --watch\"," package.json
    echo "Added tailwind scripts to package.json"
  fi
fi

echo "prefix=" > .npmrc

echo "Please run the following command to apply changes to your current shell:"
echo "source $PROFILE_FILE"

echo "npm configuration fixed. You can now run:"
echo "npm run tailwind"
echo "npm run build:css"
echo "npm run watch:css"
