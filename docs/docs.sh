#!/bin/bash
# Run this script from repo root to serve site: > sh ./docs/docs.sh serve
# Then, navigate to localhost:8000/ to inspect site
# ctrl+c to exit

# Copy top-level repo files for docs display
for f in $(ls -f C*md); do cp $f ./docs/src/; done
cp ./LICENSE ./docs/src

# Generate files from yaml
python automation/main.py

# Get major version (for full, '[0-9]\.[0-9]+\.[a-z0-9]+')
export MAJOR_VERSION=$(cat ./automation/version.py | grep -oE '[0-9]\.[0-9]+')
echo $MAJOR_VERSION

# Generate site docs
mike deploy $MAJOR_VERSION --config ./docs/mkdocs.yml

# Label this version as latest, set as default
mike alias $MAJOR_VERSION latest --config ./docs/mkdocs.yml
mike set-default latest --config ./docs/mkdocs.yml

# # Serve site to localhost
if [ "$1" == "serve" ]; then # If first arg is serve, serve docs
    mike serve --config ./docs/mkdocs.yml
elif [ "$1" == "push" ]; then # if first arg is push
    if [ -z "$2" ]; then # When no second arg, use local git user
        export git_user=$(git config user.name)
    else # Otherwise, accept second arg as git user
        export git_user="${2}"
    fi # Push mike results to relevant branch
    git push https://github.com/$(git_user)/TheGame.git gh-page
else
    echo "Docs built. "
    echo "  Add 'serve' as script arg to serve. "
    echo "  Add 'push' to push to your fork."
    echo "  Use additional arg to dictate push-to fork"
fi