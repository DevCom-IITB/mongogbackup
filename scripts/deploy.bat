@echo off
echo Building the project...
python -m build

if %errorlevel% neq 0 (
    echo Build failed!
    exit /b %errorlevel%
)

echo Uploading the distributions to PyPI...
twine upload dist\*

if %errorlevel% neq 0 (
    echo Upload failed!
    exit /b %errorlevel%
)

echo Deployment successful!
