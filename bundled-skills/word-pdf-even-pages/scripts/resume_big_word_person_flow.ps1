param(
    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [string]$Python = "python",

    [int]$MaxThirdPageChars = 120,
    [int]$PerFileTimeoutSeconds = 90,
    [string]$CompactRootName = "person_doc_compact_attempt_isolated_v2",
    [string]$MergedPdfName = "merged_even_pages.pdf"
)

$ErrorActionPreference = "Stop"

$pythonExe = $Python
$skillDir = Split-Path -Parent $PSScriptRoot
$childPowerShell = (Get-Command pwsh -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty Source)
if (-not $childPowerShell) {
    $childPowerShell = (Get-Command powershell.exe -ErrorAction Stop).Source
}
$splitDocDir = Join-Path $OutputRoot "person_doc_split"
$compactRoot = Join-Path $OutputRoot $CompactRootName
$rawPdfDir = Join-Path $OutputRoot "person_pdf_raw"
$candidatePdfDir = Join-Path $OutputRoot "person_pdf_candidates"
$evenPdfDir = Join-Path $OutputRoot "person_pdf_even"
$mergedPdf = Join-Path $OutputRoot $MergedPdfName
$summaryPath = Join-Path $OutputRoot "final_summary.csv"

New-Item -ItemType Directory -Path (
    $compactRoot,
    $rawPdfDir,
    $candidatePdfDir,
    $evenPdfDir
) -Force | Out-Null

if (-not (Test-Path -LiteralPath $splitDocDir)) {
    throw "Missing split directory: $splitDocDir"
}

function Quote-PowerShellString {
    param([string]$Value)
    return "'" + ($Value -replace "'", "''") + "'"
}

$splitReportPath = Join-Path $OutputRoot "split_report.csv"
if (-not (Test-Path -LiteralPath $splitReportPath)) {
    throw "Missing split report: $splitReportPath"
}

$splitPagesByBase = @{}
foreach ($row in (Import-Csv -LiteralPath $splitReportPath)) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($row.split_doc)
    $splitPagesByBase[$base] = [int]$row.split_pages
}

$reportDir = Join-Path $compactRoot "reports"
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null

$files = Get-ChildItem -LiteralPath $splitDocDir -Filter "*.doc" -File |
    Sort-Object Name

$scriptPath = Join-Path $PSScriptRoot "compact_one_compat_doc_direct.ps1"
$index = 0
foreach ($file in $files) {
    $index++
    $reportPath = Join-Path $reportDir ($file.BaseName + ".csv")
    if (Test-Path -LiteralPath $reportPath) {
        Write-Host "[$index/$($files.Count)] skip $($file.Name)"
        continue
    }

    $knownPages = $splitPagesByBase[$file.BaseName]
    if ($knownPages -ne 3) {
        Write-Host "[$index/$($files.Count)] no compact needed $($file.Name)"
        [pscustomobject]@{
            file = $file.Name
            status = "not_candidate"
            source_pages = $knownPages
            page3_chars = ""
            variant = ""
            final_pages = ""
            output_doc = ""
            output_pdf = ""
            message = "Skipped because split_pages is not 3"
        } | Export-Csv -LiteralPath $reportPath -NoTypeInformation -Encoding UTF8
        continue
    }

    Write-Host "[$index/$($files.Count)] compact $($file.Name)"
    $startTime = Get-Date
    $beforeWord = @(Get-Process WINWORD -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty Id)
    $stdout = Join-Path $compactRoot ("logs\" + $file.BaseName + ".out.txt")
    $stderr = Join-Path $compactRoot ("logs\" + $file.BaseName + ".err.txt")
    New-Item -ItemType Directory -Path (Split-Path -Parent $stdout) -Force |
        Out-Null

    $command = "& $(Quote-PowerShellString $scriptPath) " +
        "-InputFile $(Quote-PowerShellString $file.FullName) " +
        "-OutputRoot $(Quote-PowerShellString $compactRoot) " +
        "-MaxThirdPageChars $MaxThirdPageChars"
    $encodedCommand = [Convert]::ToBase64String(
        [System.Text.Encoding]::Unicode.GetBytes($command)
    )
    $args = "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $encodedCommand"
    $proc = Start-Process -FilePath $childPowerShell `
        -ArgumentList $args `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr

    if (-not $proc.WaitForExit($PerFileTimeoutSeconds * 1000)) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $afterWord = @(Get-Process WINWORD -ErrorAction SilentlyContinue |
            Where-Object {
                $_.StartTime -ge $startTime -and
                ($beforeWord -notcontains $_.Id) -and
                $_.Path -like "*WINWORD*"
            })
        foreach ($wordProc in $afterWord) {
            Stop-Process -Id $wordProc.Id -Force -ErrorAction SilentlyContinue
        }
        [pscustomobject]@{
            file = $file.Name
            status = "timeout_skip"
            source_pages = ""
            page3_chars = ""
            variant = ""
            final_pages = ""
            output_doc = ""
            output_pdf = ""
            message = "Timed out after $PerFileTimeoutSeconds seconds"
        } | Export-Csv -LiteralPath $reportPath -NoTypeInformation -Encoding UTF8
    }
    else {
        $proc.Refresh()
        if ($proc.ExitCode -ne 0 -and -not (Test-Path -LiteralPath $reportPath)) {
            $message = ""
            if (Test-Path -LiteralPath $stderr) {
                $message = (Get-Content -LiteralPath $stderr -Raw)
            }
            [pscustomobject]@{
                file = $file.Name
                status = "failed_invocation"
                source_pages = $knownPages
                page3_chars = ""
                variant = ""
                final_pages = ""
                output_doc = ""
                output_pdf = ""
                message = $message
            } | Export-Csv -LiteralPath $reportPath -NoTypeInformation -Encoding UTF8
        }
    }
}

$compactReports = Get-ChildItem -LiteralPath $reportDir -Filter "*.csv" -File |
    Sort-Object Name |
    ForEach-Object { Import-Csv -LiteralPath $_.FullName }
$compactReportPath = Join-Path $compactRoot "direct_compaction_report.csv"
$compactReports | Export-Csv -LiteralPath $compactReportPath -NoTypeInformation -Encoding UTF8

& (Join-Path $skillDir "scripts\convert_word_to_pdf.ps1") `
    -InputDir $splitDocDir `
    -OutputDir $rawPdfDir `
    -Force

$acceptedByBase = @{}
foreach ($row in $compactReports) {
    if ($row.status -eq "accepted") {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($row.file)
        $acceptedByBase[$base] = $row.output_pdf
    }
}

Get-ChildItem -LiteralPath $candidatePdfDir -Filter "*.pdf" -File |
    Remove-Item -Force

foreach ($pdf in Get-ChildItem -LiteralPath $rawPdfDir -Filter "*.pdf" -File |
    Sort-Object Name) {
    $base = $pdf.BaseName
    $destination = Join-Path $candidatePdfDir $pdf.Name
    if ($acceptedByBase.ContainsKey($base)) {
        Copy-Item -LiteralPath $acceptedByBase[$base] -Destination $destination -Force
    }
    else {
        Copy-Item -LiteralPath $pdf.FullName -Destination $destination -Force
    }
}

& $pythonExe -X utf8 (Join-Path $skillDir "scripts\enforce_even_pages.py") `
    $candidatePdfDir `
    $evenPdfDir

& $pythonExe -X utf8 (Join-Path $skillDir "scripts\merge_pdfs.py") `
    $evenPdfDir `
    $mergedPdf

$splitReport = Import-Csv -LiteralPath (Join-Path $OutputRoot "split_report.csv")
$pageReport = Import-Csv -LiteralPath (Join-Path $OutputRoot "page_processing_report.csv")
$summary = foreach ($split in $splitReport) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($split.split_doc)
    $comp = $compactReports | Where-Object {
        [System.IO.Path]::GetFileNameWithoutExtension($_.file) -eq $base
    } | Select-Object -First 1
    $page = $pageReport | Where-Object {
        [System.IO.Path]::GetFileNameWithoutExtension($_.filename) -eq $base
    } | Select-Object -First 1
    [pscustomobject]@{
        global_index = $split.global_index
        source_file = $split.source_file
        source_table = $split.source_table
        student_id = $split.student_id
        student_name = $split.student_name
        original_pages = $split.original_pages
        split_pages = $split.split_pages
        compaction_status = $comp.status
        compaction_variant = $comp.variant
        candidate_pdf_pages = $page.original_pages
        even_rule_action = $page.action
        final_pages = $page.final_pages
    }
}
$summary | Export-Csv -LiteralPath $summaryPath -NoTypeInformation -Encoding UTF8
$summary | Group-Object compaction_status | Select-Object Name,Count |
    Format-Table -AutoSize
$summary | Group-Object even_rule_action | Select-Object Name,Count |
    Format-Table -AutoSize
Write-Host "Merged PDF: $mergedPdf"
