[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir 'generate_examples_index.py'

if (-not (Test-Path -LiteralPath $pythonScript)) {
    Write-Error "Python generator not found: $pythonScript"
    exit 1
}

python $pythonScript
exit $LASTEXITCODE
