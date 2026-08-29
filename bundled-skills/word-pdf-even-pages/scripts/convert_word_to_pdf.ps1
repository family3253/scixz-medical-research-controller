param(
    [Parameter(Mandatory = $true)]
    [string]$InputDir,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [switch]$Recurse,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Release-ComObject {
    param([object]$Object)
    if ($null -ne $Object) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object)
    }
}

$inputRoot = (Resolve-Path -LiteralPath $InputDir).Path
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$outputRoot = (Resolve-Path -LiteralPath $OutputDir).Path

$files = Get-ChildItem -LiteralPath $inputRoot -File -Recurse:$Recurse |
    Where-Object { $_.Extension -in @(".doc", ".docx") } |
    Sort-Object FullName

if ($files.Count -eq 0) {
    throw "No .doc or .docx files found in $inputRoot"
}

$duplicateNames = $files | Group-Object BaseName | Where-Object Count -gt 1
if ($duplicateNames) {
    throw "Duplicate base names would overwrite PDFs: $($duplicateNames.Name -join ', ')"
}

$word = $null
$results = [System.Collections.Generic.List[object]]::new()

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3

    $index = 0
    foreach ($file in $files) {
        $index++
        $pdfPath = Join-Path $outputRoot ($file.BaseName + ".pdf")
        $document = $null
        $status = "converted"
        $message = ""

        Write-Host "[$index/$($files.Count)] $($file.Name)"

        if ((Test-Path -LiteralPath $pdfPath) -and -not $Force) {
            $results.Add([pscustomobject]@{
                source = $file.FullName
                pdf = $pdfPath
                status = "skipped_existing"
                message = ""
            })
            continue
        }

        try {
            $document = $word.Documents.Open($file.FullName, $false, $true)
            $document.ExportAsFixedFormat(
                $pdfPath, 17, $false, 0, 0, 1, 1, 0,
                $true, $true, 0, $true, $true, $false
            )
        }
        catch {
            $status = "failed"
            $message = $_.Exception.Message
        }
        finally {
            if ($null -ne $document) {
                $document.Close(0)
                Release-ComObject $document
            }
        }

        $results.Add([pscustomobject]@{
            source = $file.FullName
            pdf = $pdfPath
            status = $status
            message = $message
        })
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

$logPath = Join-Path $outputRoot "conversion_log.csv"
$results | Export-Csv -LiteralPath $logPath -NoTypeInformation -Encoding UTF8

$failed = @($results | Where-Object status -eq "failed")
if ($failed.Count -gt 0) {
    throw "$($failed.Count) conversion(s) failed. See $logPath"
}

Write-Host "Processed $($results.Count) Word files. Log: $logPath"

