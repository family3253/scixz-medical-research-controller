param(
    [string]$Path = '<USER_HOME>/Downloads/PlotCase-win-x64-1.0.3/PlotCase-win-x64-1.0.3/PlotCase.exe'
)

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Error "PlotCase executable not found: $Path"
    exit 1
}

Start-Process -FilePath $Path | Out-Null
Write-Output 'PlotCase started'
