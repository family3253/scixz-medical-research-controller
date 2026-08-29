param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,

    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [int]$MaxThirdPageChars = 120
)

$ErrorActionPreference = "Stop"

function Release-ComObject {
    param([object]$Object)
    if ($null -ne $Object) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object)
    }
}

function Normalize-Text {
    param([string]$Text)
    return ($Text -replace "[\s`r`n`t`a`v`f]+", "")
}

function Get-FontFingerprint {
    param([object]$Document)
    $values = [System.Collections.Generic.List[string]]::new()
    foreach ($wordRange in $Document.Words) {
        $values.Add([string]$wordRange.Font.Size)
        Release-ComObject $wordRange
    }
    return $values -join ","
}

function Get-Fingerprint {
    param([object]$Document)
    return [pscustomobject]@{
        Text = $Document.Content.Text
        Tables = $Document.Tables.Count
        InlineShapes = $Document.InlineShapes.Count
        Shapes = $Document.Shapes.Count
        Sections = $Document.Sections.Count
        Fonts = Get-FontFingerprint $Document
    }
}

function Same-Fingerprint {
    param([object]$Before, [object]$After)
    return (
        $Before.Text -ceq $After.Text -and
        $Before.Tables -eq $After.Tables -and
        $Before.InlineShapes -eq $After.InlineShapes -and
        $Before.Shapes -eq $After.Shapes -and
        $Before.Sections -eq $After.Sections -and
        $Before.Fonts -ceq $After.Fonts
    )
}

function Compress-Rows {
    param(
        [object]$Document,
        [string]$Scope,
        [single]$EmptyHeight,
        [single]$RemarkHeight
    )
    $table = $Document.Tables.Item($Document.Tables.Count)
    $rowText = @{}
    $rowCell = @{}
    $rowPage = @{}

    foreach ($cell in $table.Range.Cells) {
        $idx = $cell.RowIndex
        if (-not $rowText.ContainsKey($idx)) {
            $rowText[$idx] = ""
            $rowCell[$idx] = $cell
            $rowPage[$idx] = [int]$cell.Range.Information(3)
        }
        $rowText[$idx] += Normalize-Text $cell.Range.Text
    }

    $empty = 0
    $remark = 0
    foreach ($idx in $rowText.Keys) {
        if ($rowText[$idx] -eq "备注") {
            $rowCell[$idx].Range.Rows.SetHeight($RemarkHeight, 2)
            $remark++
        }
        elseif (
            [string]::IsNullOrEmpty($rowText[$idx]) -and
            (
                ($Scope -eq "page2" -and $rowPage[$idx] -eq 2) -or
                ($Scope -eq "before_page3" -and $rowPage[$idx] -lt 3)
            )
        ) {
            $rowCell[$idx].Range.Rows.SetHeight($EmptyHeight, 2)
            $empty++
        }
    }

    return [pscustomobject]@{ Empty = $empty; Remark = $remark }
}

function Target-Margin {
    param([double]$Value, [double]$Reduction)
    return [single][math]::Max(54, $Value - $Reduction)
}

$inputPath = (Resolve-Path -LiteralPath $InputFile).Path
$outDoc = Join-Path $OutputRoot "doc_compact"
$outPdf = Join-Path $OutputRoot "pdf_compact"
$attemptDir = Join-Path $OutputRoot "attempts"
$reportDir = Join-Path $OutputRoot "reports"
New-Item -ItemType Directory -Path $outDoc, $outPdf, $attemptDir, $reportDir -Force |
    Out-Null

$baseName = [System.IO.Path]::GetFileNameWithoutExtension($inputPath)
$reportPath = Join-Path $reportDir ($baseName + ".csv")

$variants = @(
    [pscustomobject]@{ Name = "page2_rows"; Scope = "page2"; Top = 0; Bottom = 0 },
    [pscustomobject]@{ Name = "page2_rows_bottom6"; Scope = "page2"; Top = 0; Bottom = 6 },
    [pscustomobject]@{ Name = "page2_rows_bottom12"; Scope = "page2"; Top = 0; Bottom = 12 },
    [pscustomobject]@{ Name = "page2_rows_bottom18"; Scope = "page2"; Top = 0; Bottom = 18 },
    [pscustomobject]@{ Name = "page2_rows_top6_bottom18"; Scope = "page2"; Top = 6; Bottom = 18 },
    [pscustomobject]@{ Name = "page2_rows_top12_bottom18"; Scope = "page2"; Top = 12; Bottom = 18 },
    [pscustomobject]@{ Name = "page2_rows_top18_bottom18"; Scope = "page2"; Top = 18; Bottom = 18 },
    [pscustomobject]@{ Name = "all_empty_rows_top18_bottom18"; Scope = "before_page3"; Top = 18; Bottom = 18 }
)

$word = $null
$row = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3

    $src = $word.Documents.Open($inputPath, $false, $true)
    try {
        $srcPages = $src.ComputeStatistics(2)
        $fingerprint = Get-Fingerprint $src
        $top = [double]$src.Sections.Item(1).PageSetup.TopMargin
        $bottom = [double]$src.Sections.Item(1).PageSetup.BottomMargin
        $page3Chars = 0
        if ($srcPages -ge 3) {
            $start = $src.GoTo(1, 1, 3).Start
            $range = $src.Range($start, $src.Content.End)
            $page3Chars = (Normalize-Text $range.Text).Length
            Release-ComObject $range
        }
    }
    finally {
        $src.Close(0)
        Release-ComObject $src
    }

    if ($srcPages -ne 3 -or $page3Chars -gt $MaxThirdPageChars) {
        $row = [pscustomobject]@{
            file = [System.IO.Path]::GetFileName($inputPath)
            status = "not_candidate"
            source_pages = $srcPages
            page3_chars = $page3Chars
            variant = ""
            final_pages = ""
            output_doc = ""
            output_pdf = ""
            message = ""
        }
    }
    else {
        foreach ($variant in $variants) {
            $attempt = Join-Path $attemptDir ($baseName + "_" + $variant.Name + [System.IO.Path]::GetExtension($inputPath))
            Copy-Item -LiteralPath $inputPath -Destination $attempt -Force
            $doc = $word.Documents.Open($attempt, $false, $false)
            try {
                [void](Compress-Rows $doc $variant.Scope 6 24)
                foreach ($section in $doc.Sections) {
                    $section.PageSetup.TopMargin = Target-Margin $top $variant.Top
                    $section.PageSetup.BottomMargin = Target-Margin $bottom $variant.Bottom
                }
                $pages = $doc.ComputeStatistics(2)
                $after = Get-Fingerprint $doc
                if ($pages -eq 2 -and (Same-Fingerprint $fingerprint $after)) {
                    $finalDoc = Join-Path $outDoc ([System.IO.Path]::GetFileName($inputPath))
                    $finalPdf = Join-Path $outPdf ($baseName + ".pdf")
                    $doc.Save()
                    $doc.ExportAsFixedFormat(
                        $finalPdf, 17, $false, 0, 0, 1, 1, 0,
                        $true, $true, 0, $true, $true, $false
                    )
                    $doc.Close(0)
                    Release-ComObject $doc
                    $doc = $null
                    Move-Item -LiteralPath $attempt -Destination $finalDoc -Force
                    $row = [pscustomobject]@{
                        file = [System.IO.Path]::GetFileName($inputPath)
                        status = "accepted"
                        source_pages = $srcPages
                        page3_chars = $page3Chars
                        variant = $variant.Name
                        final_pages = 2
                        output_doc = $finalDoc
                        output_pdf = $finalPdf
                        message = ""
                    }
                    break
                }
            }
            finally {
                if ($null -ne $doc) {
                    $doc.Close(0)
                    Release-ComObject $doc
                }
            }
        }

        if ($null -eq $row) {
            $row = [pscustomobject]@{
                file = [System.IO.Path]::GetFileName($inputPath)
                status = "not_compacted"
                source_pages = $srcPages
                page3_chars = $page3Chars
                variant = ""
                final_pages = ""
                output_doc = ""
                output_pdf = ""
                message = ""
            }
        }
    }
}
catch {
    $row = [pscustomobject]@{
        file = [System.IO.Path]::GetFileName($inputPath)
        status = "failed"
        source_pages = ""
        page3_chars = ""
        variant = ""
        final_pages = ""
        output_doc = ""
        output_pdf = ""
        message = $_.Exception.Message
    }
}
finally {
    if ($null -ne $word) {
        $word.Quit()
        Release-ComObject $word
    }
    [gc]::Collect()
    [gc]::WaitForPendingFinalizers()
}

$row | Export-Csv -LiteralPath $reportPath -NoTypeInformation -Encoding UTF8
$row | Format-List
