@echo off
:: Generate HTML documentation
pdoc --html ./mongogbackup/ -o ./docs/

:: Move contents of ./docs/mongogbackup/ to ./docs
move ./docs/mongogbackup\* ./docs

:: Delete the ./docs/mongogbackup/ directory
rmdir /s /q ./docs/mongogbackup/
