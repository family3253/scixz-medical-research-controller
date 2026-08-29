param(
    [Parameter(Mandatory = $true)]
    [string]$SelectedInventory,

    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot
)

$ErrorActionPreference = "Stop"

$repo = (Resolve-Path -LiteralPath $RepositoryRoot).Path
$destRoot = Join-Path $repo "bundled-skills"
if (-not (Test-Path -LiteralPath $destRoot)) {
    New-Item -ItemType Directory -Path $destRoot | Out-Null
}

$resolvedDestRoot = (Resolve-Path -LiteralPath $destRoot).Path
if (-not $resolvedDestRoot.StartsWith($repo, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Destination outside repository: $resolvedDestRoot"
}

$selected = Get-Content -LiteralPath $SelectedInventory -Raw | ConvertFrom-Json

$excludeDirs = @(
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "projects",
    "runs",
    "run_manifests",
    "outputs",
    "state",
    "memory",
    "private-journal-profiles",
    ".next",
    ".cache",
    "playwright-report",
    "test-results"
)

$excludeFiles = @(
    "*.pyc",
    "*.pyo",
    "*.log",
    "*.tmp",
    "*.bak",
    ".DS_Store",
    "Thumbs.db",
    "*.sqlite-journal",
    "*.db-journal"
)

$copied = 0
foreach ($skill in $selected) {
    $safeFolder = ($skill.name -replace "[^A-Za-z0-9._-]", "-")
    if ([string]::IsNullOrWhiteSpace($safeFolder)) {
        $safeFolder = ($skill.folder -replace "[^A-Za-z0-9._-]", "-")
    }

    $dest = Join-Path $resolvedDestRoot $safeFolder
    if (Test-Path -LiteralPath $dest) {
        $resolvedExisting = (Resolve-Path -LiteralPath $dest).Path
        if (-not $resolvedExisting.StartsWith($resolvedDestRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove outside bundled-skills: $resolvedExisting"
        }
        Remove-Item -LiteralPath $resolvedExisting -Recurse -Force
    }

    $args = @(
        $skill.path,
        $dest,
        "/E",
        "/R:1",
        "/W:1",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS",
        "/NP"
    )

    foreach ($dir in $excludeDirs) {
        $args += @("/XD", (Join-Path $skill.path $dir))
    }
    foreach ($file in $excludeFiles) {
        $args += @("/XF", $file)
    }

    & robocopy @args | Out-Null
    if ($LASTEXITCODE -ge 8) {
        throw "robocopy failed for $($skill.name) with exit code $LASTEXITCODE"
    }
    $copied += 1
}

[pscustomobject]@{
    copied = $copied
    destination = $resolvedDestRoot
} | ConvertTo-Json
