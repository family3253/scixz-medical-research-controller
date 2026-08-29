param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$OutputDirectory,
    [string]$Topic = '',
    [string]$TitleZh = '',
    [string]$TitleEn = '',
    [string]$Domain = 'Interdisciplinary Topic',
    [string]$ReviewType = 'Narrative Review',
    [ValidateSet('A', 'B', 'C', 'D')]
    [string]$GateProfile = 'B',
    [string]$Language = 'Chinese',
    [string]$Purpose = 'Submission-ready review project skeleton',
    [string]$TimeBoundary = 'Last 5 years',
    [string]$KeywordsZh = '',
    [string]$KeywordsEn = '',
    [string]$Subthemes = '',
    [switch]$Force,
    [switch]$SkipExisting
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

$arguments = @($scriptPath, $OutputDirectory)
foreach ($pair in @(
    @{ Name = '--topic'; Value = $Topic },
    @{ Name = '--title-zh'; Value = $TitleZh },
    @{ Name = '--title-en'; Value = $TitleEn },
    @{ Name = '--domain'; Value = $Domain },
    @{ Name = '--review-type'; Value = $ReviewType },
    @{ Name = '--gate-profile'; Value = $GateProfile },
    @{ Name = '--language'; Value = $Language },
    @{ Name = '--purpose'; Value = $Purpose },
    @{ Name = '--time-boundary'; Value = $TimeBoundary },
    @{ Name = '--keywords-zh'; Value = $KeywordsZh },
    @{ Name = '--keywords-en'; Value = $KeywordsEn },
    @{ Name = '--subthemes'; Value = $Subthemes }
)) {
    if ($pair.Value) {
        $arguments += $pair.Name
        $arguments += $pair.Value
    }
}
if ($Force) {
    $arguments += '--force'
}
if ($SkipExisting) {
    $arguments += '--skip-existing'
}

& $python.Source @arguments
$exitCode = $LASTEXITCODE
if ($null -eq $exitCode) {
    $exitCode = 0
}
exit $exitCode
