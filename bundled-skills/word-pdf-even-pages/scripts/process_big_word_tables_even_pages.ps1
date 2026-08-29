param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [string]$SourceDir,
    [string[]]$SourceFiles,
    [string]$Filter = "*.doc",
    [string]$Python = "python",
    [int]$MaxThirdPageChars = 120,
    [int]$PerFileTimeoutSeconds = 180,
    [string]$MergedPdfName = "merged_even_pages.pdf"
)

$ErrorActionPreference = "Stop"

function Release-ComObject {
    param([object]$Object)
    if ($null -ne $Object) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object)
    }
}

function Get-WordTableCount {
    param([string]$Path)

    $word = $null
    $doc = $null
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $word.DisplayAlerts = 0
        $word.AutomationSecurity = 3
        $doc = $word.Documents.Open($Path, $false, $true)
        return [int]$doc.Tables.Count
    }
    finally {
        if ($null -ne $doc) {
            $doc.Close(0)
            Release-ComObject $doc
        }
        if ($null -ne $word) {
            $word.Quit()
            Release-ComObject $word
        }
        [gc]::Collect()
        [gc]::WaitForPendingFinalizers()
    }
}

if (-not $SourceFiles -or $SourceFiles.Count -eq 0) {
    if ([string]::IsNullOrWhiteSpace($SourceDir)) {
        throw "Provide either -SourceFiles or -SourceDir."
    }
    $SourceFiles = Get-ChildItem -LiteralPath $SourceDir -Filter $Filter -File |
        Sort-Object Name |
        Select-Object -ExpandProperty FullName
}

if (-not $SourceFiles -or $SourceFiles.Count -eq 0) {
    throw "No source Word files found."
}

$scriptRoot = $PSScriptRoot
$splitScript = Join-Path $scriptRoot "split_big_word_tables_compat.ps1"
$resumeScript = Join-Path $scriptRoot "resume_big_word_person_flow.ps1"

$splitDocDir = Join-Path $OutputRoot "person_doc_split"
New-Item -ItemType Directory -Path $OutputRoot, $splitDocDir -Force | Out-Null

$globalIndex = 1
$allSplitRows = [System.Collections.Generic.List[object]]::new()

foreach ($source in $SourceFiles) {
    $sourcePath = (Resolve-Path -LiteralPath $source).Path
    $sourceName = [System.IO.Path]::GetFileNameWithoutExtension($sourcePath)
    $tableCount = Get-WordTableCount $sourcePath
    if ($tableCount -lt 1) {
        Write-Warning "Skipping $sourcePath because it has no tables."
        continue
    }

    $tempDir = Join-Path $OutputRoot ("split_tmp_" + $sourceName)
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    $tables = 1..$tableCount -join ","

    & $splitScript `
        -InputFile $sourcePath `
        -OutputDir $tempDir `
        -Tables $tables

    $splitReport = Import-Csv -LiteralPath (Join-Path $tempDir "compat_split_report.csv")
    foreach ($row in $splitReport) {
        $newName = "{0:D4}_{1}_{2}_from_{3}_t{4:D3}.doc" -f (
            $globalIndex,
            $row.student_id,
            $row.student_name,
            $sourceName,
            [int]$row.source_table
        )
        $newPath = Join-Path $splitDocDir $newName
        Move-Item -LiteralPath $row.output_doc -Destination $newPath -Force

        $allSplitRows.Add([pscustomobject]@{
            global_index = $globalIndex
            source_file = [System.IO.Path]::GetFileName($sourcePath)
            source_table = $row.source_table
            student_id = $row.student_id
            student_name = $row.student_name
            original_pages = $row.original_pages
            split_pages = $row.split_pages
            split_doc = $newPath
        })
        $globalIndex++
    }
}

if ($allSplitRows.Count -eq 0) {
    throw "No person documents were split from the source files."
}

$splitReportPath = Join-Path $OutputRoot "split_report.csv"
$allSplitRows | Export-Csv -LiteralPath $splitReportPath -NoTypeInformation -Encoding UTF8

& $resumeScript `
    -OutputRoot $OutputRoot `
    -Python $Python `
    -MaxThirdPageChars $MaxThirdPageChars `
    -PerFileTimeoutSeconds $PerFileTimeoutSeconds `
    -MergedPdfName $MergedPdfName

Write-Host "Output root: $OutputRoot"
Write-Host "Merged PDF: $(Join-Path $OutputRoot $MergedPdfName)"
