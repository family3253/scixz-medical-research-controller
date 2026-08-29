param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ProjectDirectory,
    [switch]$Strict
)

$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) {
    throw 'Python was not found. Run the adjacent .py script directly after installing Python.'
}

$baseName = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
$scriptPath = Join-Path $PSScriptRoot ($baseName + '.py')
if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw "Missing script: $scriptPath"
}

$arguments = @($scriptPath, $ProjectDirectory)
if ($Strict) {
    $arguments += "--strict"
}

& $python.Source @arguments
$exitCode = $LASTEXITCODE
if ($null -eq $exitCode) {
    $exitCode = 0
}
exit $exitCode
