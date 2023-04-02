
# Sync the notebooks
jupytext --to py notebooks/*ipynb
# Move sync'd subdir
mv notebooks/*py notebooks/py_scripts/
