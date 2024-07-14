#!/bin/bash

echo "Building the project..."
python3 -m build

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo "Uploading the distributions to PyPI..."
twine upload dist/*

if [ $? -ne 0 ]; then
    echo "Upload failed!"
    exit 1
fi

echo "Deployment successful!"
