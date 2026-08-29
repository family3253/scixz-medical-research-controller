param(
    [string]$TargetRoot = '',
    [string]$Name = 'cross-disciplinary-review-writer',
    [switch]$Force,
    [switch]$DryRun
)

if (-not $TargetRoot) {
    $TargetRoot = Join-Path $HOME '.config\opencode\skills'
}

$sourceDir = Split-Path $PSScriptRoot -Parent
$skillMd = Join-Path $sourceDir 'SKILL.md'
if (-not (Test-Path -LiteralPath $skillMd)) {
    throw "Missing SKILL.md: $skillMd"
}

$resolvedTargetRoot = [System.IO.Path]::GetFullPath($TargetRoot)
$targetDir = Join-Path $resolvedTargetRoot $Name

if ($DryRun) {
    Write-Output "DRY-RUN source=$sourceDir"
    Write-Output "DRY-RUN target=$targetDir"
    exit 0
}

$null = New-Item -ItemType Directory -Path $resolvedTargetRoot -Force
if (Test-Path -LiteralPath $targetDir) {
    if (-not $Force) {
        throw "Target directory exists: $targetDir. Use -Force to replace it."
    }
    Remove-Item -LiteralPath $targetDir -Recurse -Force
}

$excludePatterns = @('__pycache__', '*.pyc', '*.pyo')
Copy-Item -LiteralPath $sourceDir -Destination $targetDir -Recurse -Force -Exclude $excludePatterns
Write-Output "OK installed skill: $targetDir"
