param(
    [Parameter(Mandatory = $true)]
    [string]$InputDir,

    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [int]$MaxThirdPageChars = 120,
    [single]$EmptyRowHeight = 6,
    [single]$RemarkRowHeight = 24,
    [single]$MinimumMargin = 54
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

function Fingerprints-Match {
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

function Compress-TableRows {
    param(
        [object]$Document,
        [ValidateSet("page2", "before_page3")]
        [string]$Scope,
        [single]$EmptyHeight,
        [single]$RemarkHeight
    )

    $table = $Document.Tables.Item($Document.Tables.Count)
    $rowText = @{}
    $rowCell = @{}
    $rowPage = @{}

    foreach ($cell in $table.Range.Cells) {
        $rowIndex = $cell.RowIndex
        if (-not $rowText.ContainsKey($rowIndex)) {
            $rowText[$rowIndex] = ""
            $rowCell[$rowIndex] = $cell
            $rowPage[$rowIndex] = [int]$cell.Range.Information(3)
        }
        $rowText[$rowIndex] += Normalize-Text $cell.Range.Text
    }

    $emptyRows = 0
    $remarkRows = 0
    foreach ($rowIndex in $rowText.Keys) {
        if ($rowText[$rowIndex] -eq "备注") {
            $rowCell[$rowIndex].Range.Rows.SetHeight($RemarkHeight, 2)
            $remarkRows++
            continue
        }

        $compressEmpty = (
            [string]::IsNullOrEmpty($rowText[$rowIndex]) -and
            (
                ($Scope -eq "page2" -and $rowPage[$rowIndex] -eq 2) -or
                ($Scope -eq "before_page3" -and $rowPage[$rowIndex] -lt 3)
            )
        )
        if ($compressEmpty) {
            $rowCell[$rowIndex].Range.Rows.SetHeight($EmptyHeight, 2)
            $emptyRows++
        }
    }

    return [pscustomobject]@{
        EmptyRows = $emptyRows
        RemarkRows = $remarkRows
    }
}

function Get-TargetMargin {
    param(
        [double]$Original,
        [double]$Reduction,
        [double]$Minimum
    )
    return [single][math]::Max($Minimum, $Original - $Reduction)
}

$inputRoot = (Resolve-Path -LiteralPath $InputDir).Path
$convertedDir = Join-Path $OutputRoot "docx_converted"
$compactDir = Join-Path $OutputRoot "docx_compact"
$pdfDir = Join-Path $OutputRoot "pdf_compact"
$attemptDir = Join-Path $OutputRoot "attempts"
New-Item -ItemType Directory -Path (
    $convertedDir, $compactDir, $pdfDir, $attemptDir
) -Force | Out-Null

$files = Get-ChildItem -LiteralPath $inputRoot -File |
    Where-Object { $_.Extension -in @(".doc", ".docx") } |
    Sort-Object Name

if ($files.Count -eq 0) {
    throw "No .doc or .docx files found in $inputRoot"
}

$variants = @(
    [pscustomobject]@{
        Name = "page2_rows"
        Scope = "page2"
        TopReduction = 0
        BottomReduction = 0
    },
    [pscustomobject]@{
        Name = "page2_rows_bottom6"
        Scope = "page2"
        TopReduction = 0
        BottomReduction = 6
    },
    [pscustomobject]@{
        Name = "page2_rows_bottom12"
        Scope = "page2"
        TopReduction = 0
        BottomReduction = 12
    },
    [pscustomobject]@{
        Name = "page2_rows_bottom18"
        Scope = "page2"
        TopReduction = 0
        BottomReduction = 18
    },
    [pscustomobject]@{
        Name = "page2_rows_top6_bottom18"
        Scope = "page2"
        TopReduction = 6
        BottomReduction = 18
    },
    [pscustomobject]@{
        Name = "page2_rows_top12_bottom18"
        Scope = "page2"
        TopReduction = 12
        BottomReduction = 18
    },
    [pscustomobject]@{
        Name = "page2_rows_top18_bottom18"
        Scope = "page2"
        TopReduction = 18
        BottomReduction = 18
    },
    [pscustomobject]@{
        Name = "all_empty_rows_top18_bottom18"
        Scope = "before_page3"
        TopReduction = 18
        BottomReduction = 18
    }
)

$word = $null
$results = [System.Collections.Generic.List[object]]::new()

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3

    foreach ($file in $files) {
        $convertedPath = Join-Path $convertedDir ($file.BaseName + ".docx")
        $sourceDocument = $word.Documents.Open($file.FullName, $false, $true)
        try {
            $sourceFingerprint = Get-Fingerprint $sourceDocument
            if ($file.Extension -eq ".doc") {
                $sourceDocument.SaveAs2($convertedPath, 16)
            }
            else {
                $sourceDocument.Close(0)
                Release-ComObject $sourceDocument
                $sourceDocument = $null
                Copy-Item -LiteralPath $file.FullName -Destination $convertedPath -Force
            }
        }
        finally {
            if ($null -ne $sourceDocument) {
                $sourceDocument.Close(0)
                Release-ComObject $sourceDocument
            }
        }

        $convertedDocument = $word.Documents.Open($convertedPath, $false, $true)
        try {
            $convertedDocument.Repaginate()
            $sourcePages = $convertedDocument.ComputeStatistics(2)
            $convertedFingerprint = Get-Fingerprint $convertedDocument
            $conversionValid = Fingerprints-Match (
                $sourceFingerprint
            ) $convertedFingerprint
            $originalTop = [double]$convertedDocument.Sections.Item(1).PageSetup.TopMargin
            $originalBottom = [double]$convertedDocument.Sections.Item(1).PageSetup.BottomMargin

            $page3Chars = 0
            if ($sourcePages -ge 3) {
                $page3Start = $convertedDocument.GoTo(1, 1, 3).Start
                $page3Range = $convertedDocument.Range(
                    $page3Start,
                    $convertedDocument.Content.End
                )
                $page3Chars = (Normalize-Text $page3Range.Text).Length
            }
        }
        finally {
            $convertedDocument.Close(0)
            Release-ComObject $convertedDocument
        }

        if (-not $conversionValid) {
            $results.Add([pscustomobject]@{
                source = $file.FullName
                status = "conversion_validation_failed"
                source_pages = $sourcePages
                page3_chars = $page3Chars
                variant = ""
                top_margin_after = ""
                bottom_margin_after = ""
                empty_rows_compressed = ""
                remark_rows_compressed = ""
                output_docx = ""
                output_pdf = ""
            })
            continue
        }

        if ($sourcePages -ne 3 -or $page3Chars -gt $MaxThirdPageChars) {
            $results.Add([pscustomobject]@{
                source = $file.FullName
                status = "not_candidate"
                source_pages = $sourcePages
                page3_chars = $page3Chars
                variant = ""
                top_margin_after = ""
                bottom_margin_after = ""
                empty_rows_compressed = ""
                remark_rows_compressed = ""
                output_docx = ""
                output_pdf = ""
            })
            continue
        }

        $accepted = $false
        foreach ($variant in $variants) {
            $attemptPath = Join-Path $attemptDir (
                "$($file.BaseName)_$($variant.Name).docx"
            )
            Copy-Item -LiteralPath $convertedPath -Destination $attemptPath -Force
            $document = $word.Documents.Open($attemptPath, $false, $false)

            try {
                $rowStats = Compress-TableRows `
                    -Document $document `
                    -Scope $variant.Scope `
                    -EmptyHeight $EmptyRowHeight `
                    -RemarkHeight $RemarkRowHeight

                $targetTop = Get-TargetMargin `
                    $originalTop $variant.TopReduction $MinimumMargin
                $targetBottom = Get-TargetMargin `
                    $originalBottom $variant.BottomReduction $MinimumMargin

                foreach ($section in $document.Sections) {
                    $section.PageSetup.TopMargin = $targetTop
                    $section.PageSetup.BottomMargin = $targetBottom
                }

                $document.Repaginate()
                $pages = $document.ComputeStatistics(2)
                $fingerprint = Get-Fingerprint $document
                $contentValid = Fingerprints-Match (
                    $convertedFingerprint
                ) $fingerprint

                if ($pages -eq 2 -and $contentValid) {
                    $finalWord = Join-Path $compactDir ($file.BaseName + ".docx")
                    $finalPdf = Join-Path $pdfDir ($file.BaseName + ".pdf")
                    $document.Save()
                    $document.ExportAsFixedFormat(
                        $finalPdf, 17, $false, 0, 0, 1, 1, 0,
                        $true, $true, 0, $true, $true, $false
                    )
                    $document.Close(0)
                    Release-ComObject $document
                    $document = $null
                    Move-Item -LiteralPath $attemptPath -Destination $finalWord -Force

                    $results.Add([pscustomobject]@{
                        source = $file.FullName
                        status = "accepted"
                        source_pages = $sourcePages
                        page3_chars = $page3Chars
                        variant = $variant.Name
                        top_margin_after = $targetTop
                        bottom_margin_after = $targetBottom
                        empty_rows_compressed = $rowStats.EmptyRows
                        remark_rows_compressed = $rowStats.RemarkRows
                        output_docx = $finalWord
                        output_pdf = $finalPdf
                    })
                    $accepted = $true
                    break
                }
            }
            finally {
                if ($null -ne $document) {
                    $document.Close(0)
                    Release-ComObject $document
                }
            }
        }

        if (-not $accepted) {
            $results.Add([pscustomobject]@{
                source = $file.FullName
                status = "not_compacted"
                source_pages = $sourcePages
                page3_chars = $page3Chars
                variant = ""
                top_margin_after = ""
                bottom_margin_after = ""
                empty_rows_compressed = ""
                remark_rows_compressed = ""
                output_docx = ""
                output_pdf = ""
            })
        }
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

$reportPath = Join-Path $OutputRoot "compaction_report.csv"
$results | Export-Csv -LiteralPath $reportPath -NoTypeInformation -Encoding UTF8
$results | Format-Table -AutoSize
