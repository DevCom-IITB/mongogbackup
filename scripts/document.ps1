# Generate HTML documentation
pdoc --html ./mongogbackup/ -o ./docs/

# Move contents of ./docs/mongogbackup/ to ./docs
Move-Item -Path ./docs/mongogbackup/* -Destination ./docs

# Delete the ./docs/mongogbackup/ directory
Remove-Item -Path ./docs/mongogbackup/ -Recurse -Force
