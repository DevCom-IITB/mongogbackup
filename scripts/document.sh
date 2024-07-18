#!/bin/bash

# Generate HTML documentation
pdoc --html ./mongogbackup/ -o ./docs/

# Move contents of ./docs/mongogbackup/ to ./docs
mv ./docs/mongogbackup/* ./docs

# Delete the ./docs/mongogbackup/ directory
rm -r ./docs/mongogbackup/
