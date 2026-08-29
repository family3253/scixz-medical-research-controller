param(
    [Parameter(Mandatory=$true)]
    [string]$Query,
    [int]$Top = 5,
    [ValidateSet('Text', 'Json')]
    [string]$OutputFormat = 'Text',
    [string]$Category,
    [string]$Ext
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir 'search_examples.py'

if (-not (Test-Path -LiteralPath $pythonScript)) {
    Write-Error "Python search helper not found: $pythonScript"
    exit 1
}

$argsList = @('--query', $Query, '--top', $Top, '--output-format', $OutputFormat)
if ($Category) {
    $argsList += @('--category', $Category)
}
if ($Ext) {
    $argsList += @('--ext', $Ext)
}

python $pythonScript @argsList
exit $LASTEXITCODE
