#!/bin/bash
# Run this script from repo root: > sh ./docs/docs.sh serve

# Copy top-level repo files for docs display
for f in $(ls -f C*md); do cp $f ./docs/src/; done
cp ./LICENSE ./docs/src

# Get major version (for full, '[0-9]\.[0-9]+\.[a-z0-9]+')
export MAJOR_VERSION=$(cat ./automation/version.py | grep -oE '[0-9]\.[0-9]+')
echo $MAJOR_VERSION

# Generate site docs
mike deploy $MAJOR_VERSION --config ./docs/mkdocs.yml

# Label this version as latest, set as default
mike alias $MAJOR_VERSION latest --config ./docs/mkdocs.yml
mike set-default latest --config ./docs/mkdocs.yml

# # Serve site to localhost
if [ "$1" == "serve" ]; then
    mike serve --config ./docs/mkdocs.yml
elif [ "$1" == "push" ]; then
    git push https://github.com/$(git config user.name)/TheGame.git gh-page
else
    echo "Docs built. "
    echo "  Add 'serve' as script arg to serve. "
    echo "  Add 'push' to push to your fork."
fi