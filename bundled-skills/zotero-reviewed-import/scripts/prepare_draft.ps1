param(
    [string]$SourceBib,
    [string]$TargetDir,
    [string]$Title = "Draft",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Get-LatestVerifiedBib {
    param([string]$OutputsRoot)

    $latest = Get-ChildItem -Path $OutputsRoot -Directory |
        Sort-Object LastWriteTime -Descending |
        ForEach-Object {
            $candidate = Join-Path $_.FullName "verified.bib"
            if ((Test-Path $candidate) -and (Get-Item $candidate).Length -gt 0) {
                return $candidate
            }
        } |
        Select-Object -First 1

    return $latest
}

function Get-CiteKeys {
    param([string]$BibPath)

    $matches = Select-String -Path $BibPath -Pattern '@\w+\{([^,]+),' -AllMatches
    $keys = foreach ($match in $matches) {
        foreach ($group in $match.Matches) {
            $group.Groups[1].Value
        }
    }
    return @($keys | Where-Object { $_ } | Select-Object -Unique)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$outputsRoot = Join-Path $projectRoot "outputs"
$draftsRoot = Join-Path $projectRoot "drafts"

if (-not $SourceBib) {
    $SourceBib = Get-LatestVerifiedBib -OutputsRoot $outputsRoot
}

if (-not $SourceBib) {
    throw "No verified.bib found. Run scripts\verify_references.py first or pass -SourceBib explicitly."
}

$SourceBib = (Resolve-Path $SourceBib).Path

if (-not $TargetDir) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $TargetDir = Join-Path $draftsRoot $stamp
}

if ((Test-Path $TargetDir) -and -not $Force) {
    throw "Target directory already exists: $TargetDir. Use -Force to reuse it."
}

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

$referencesPath = Join-Path $TargetDir "references.bib"
Copy-Item -LiteralPath $SourceBib -Destination $referencesPath -Force

$citeKeys = Get-CiteKeys -BibPath $referencesPath
$sampleCitation = if ($citeKeys.Count -gt 0) {
    "[" + (($citeKeys | Select-Object -First 2 | ForEach-Object { "@$_" }) -join "; ") + "]"
} else {
    "[@yourcitekey]"
}

$qmdPath = Join-Path $TargetDir "draft.qmd"
$mdPath = Join-Path $TargetDir "draft.md"

$qmd = @"
---
title: "$Title"
bibliography: references.bib
format:
  html: default
  docx: default
---

# Introduction

Start writing here. Example citation: $sampleCitation.

# Notes

- Replace the placeholder title.
- Keep Zotero Desktop open if you plan to finalize dynamic citations in Word later.
- When handing off to WPS, export the Quarto output to ``docx``.
"@

$md = @"
# $Title

Start writing here. Example citation: $sampleCitation.

If you prefer Quarto, use ``draft.qmd`` in the same folder together with ``references.bib``.
"@

Set-Content -Path $qmdPath -Value $qmd -Encoding UTF8
Set-Content -Path $mdPath -Value $md -Encoding UTF8

[pscustomobject]@{
    source_bib = $SourceBib
    target_dir = (Resolve-Path $TargetDir).Path
    references_bib = $referencesPath
    draft_qmd = $qmdPath
    draft_md = $mdPath
    detected_citekeys = ($citeKeys -join ", ")
} | Format-List
