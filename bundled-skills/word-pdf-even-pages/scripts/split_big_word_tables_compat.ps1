param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [Parameter(Mandatory = $true)]
    [string]$Tables
)

$ErrorActionPreference = "Stop"

function Release-ComObject {
    param([object]$Object)
    if ($null -ne $Object) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object)
    }
}

function Normalize-FilePart {
    param([string]$Text)
    $safe = ($Text -replace '[\\/:*?"<>|]', '_').Trim()
    if ([string]::IsNullOrWhiteSpace($safe)) { return "unknown" }
    return $safe
}

function Get-StudentInfo {
    param([string]$TableText)
    $linear = ($TableText -replace "[`r`a`v`f]+", "|") -replace "\s+", " "
    $linear = $linear.Trim(" ", "|")
    $match = [regex]::Match($linear, "学号\|(?<id>[^|]+)\|姓名\|(?<name>[^|]+)")
    if ($match.Success) {
        return [pscustomobject]@{
            Id = Normalize-FilePart $match.Groups["id"].Value
            Name = Normalize-FilePart $match.Groups["name"].Value
        }
    }
    return [pscustomobject]@{ Id = "noid"; Name = "noname" }
}

function Copy-PageSetup {
    param([object]$Source, [object]$Target)
    $Target.PageWidth = $Source.PageWidth
    $Target.PageHeight = $Source.PageHeight
    $Target.Orientation = $Source.Orientation
    $Target.TopMargin = $Source.TopMargin
    $Target.BottomMargin = $Source.BottomMargin
    $Target.LeftMargin = $Source.LeftMargin
    $Target.RightMargin = $Source.RightMargin
    $Target.HeaderDistance = $Source.HeaderDistance
    $Target.FooterDistance = $Source.FooterDistance
}

$inputPath = (Resolve-Path -LiteralPath $InputFile).Path
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$outRoot = (Resolve-Path -LiteralPath $OutputDir).Path
$tableNumbers = $Tables.Split(",", [System.StringSplitOptions]::RemoveEmptyEntries) |
    ForEach-Object { [int]$_.Trim() } |
    Sort-Object -Unique

$word = $null
$rows = [System.Collections.Generic.List[object]]::new()

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3

    $sourceDoc = $word.Documents.Open($inputPath, $false, $true)
    try {
        $compatibilityMode = $sourceDoc.CompatibilityMode
        foreach ($tableNumber in $tableNumbers) {
            $table = $sourceDoc.Tables.Item($tableNumber)
            $start = $table.Range.Duplicate
            $start.Collapse(1)
            $end = $table.Range.Duplicate
            $end.Collapse(0)
            $originalPages = [int]$end.Information(3) - [int]$start.Information(3) + 1
            $info = Get-StudentInfo $table.Range.Text
            $stem = "{0:D3}_{1}_{2}_compat{3}" -f (
                $tableNumber,
                $info.Id,
                $info.Name,
                $compatibilityMode
            )
            $docPath = Join-Path $outRoot ($stem + ".doc")
            $docxPath = Join-Path $outRoot ($stem + ".docx")
            $pdfPath = Join-Path $outRoot ($stem + ".pdf")

            $newDoc = $word.Documents.Add()
            try {
                Copy-PageSetup `
                    -Source $sourceDoc.Sections.Item(1).PageSetup `
                    -Target $newDoc.Sections.Item(1).PageSetup
                $newDoc.Content.FormattedText = $table.Range.FormattedText
                $newDoc.SaveAs2($docPath, 0)
                $newDoc.Close(0)
                Release-ComObject $newDoc
                $newDoc = $word.Documents.Open($docPath, $false, $false)
                $newDoc.ExportAsFixedFormat(
                    $pdfPath, 17, $false, 0, 0, 1, 1, 0,
                    $true, $true, 0, $true, $true, $false
                )
                $pages = $newDoc.ComputeStatistics(2)
                $mode = $newDoc.CompatibilityMode
            }
            finally {
                $newDoc.Close(0)
                Release-ComObject $newDoc
            }

            $rows.Add([pscustomobject]@{
                source_table = $tableNumber
                student_id = $info.Id
                student_name = $info.Name
                original_pages = $originalPages
                split_pages = $pages
                compatibility_mode = $mode
                output_doc = $docPath
                output_pdf = $pdfPath
            })
        }
    }
    finally {
        $sourceDoc.Close(0)
        Release-ComObject $sourceDoc
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

$report = Join-Path $outRoot "compat_split_report.csv"
$rows | Export-Csv -LiteralPath $report -NoTypeInformation -Encoding UTF8
$rows | Format-Table -AutoSize
