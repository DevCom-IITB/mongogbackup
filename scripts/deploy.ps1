Write-Output "Building the project..."
python -m build

if ($LASTEXITCODE -ne 0) {
    Write-Output "Build failed!"
    exit $LASTEXITCODE
}

Write-Output "Uploading the distributions to PyPI..."
twine upload dist/*

if ($LASTEXITCODE -ne 0) {
    Write-Output "Upload failed!"
    exit $LASTEXITCODE
}

Write-Output "Deployment successful!"
