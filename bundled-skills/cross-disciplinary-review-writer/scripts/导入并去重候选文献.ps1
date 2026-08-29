param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string[]]$InputFiles,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [string]$DatabaseName = '',
    [string]$BatchName = '',
    [string]$RetrievalDate = '',
    [string]$DefaultSubtheme = ''
)

$schema = Import-PowerShellDataFile -Path (Join-Path $PSScriptRoot 'review_project_schema.psd1')
$candidateHeaders = $schema.CandidateHeaders
$schemaVersion = $schema.SchemaVersion

if (-not $BatchName) {
    $BatchName = 'import-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
}
if (-not $RetrievalDate) {
    $RetrievalDate = Get-Date -Format 'yyyy-MM-dd'
}

$yesTokens = @('1', 'true', 'yes', 'y', '是', '可获取', 'open', 'oa')
$sourceAliases = @{
    title    = @('题名', 'title', 'ArticleTitle')
    authors  = @('作者', 'authors', 'authorString', 'Authors')
    year     = @('年份', 'year', 'pubYear', 'Year')
    venue    = @('来源期刊/会议/出版社', 'journal', 'journalTitle', 'source', 'Source')
    doi      = @('DOI/链接', 'doi', 'DOI')
    pmid     = @('pmid', 'PMID')
    pmcid    = @('pmcid', 'PMCID')
    type     = @('文献类型', 'title_type', 'publication_type', 'category')
    design   = @('研究设计/方法类型', 'evidence_hint', 'study_type')
    subtheme = @('子主题标签', 'subtheme', 'source_queries')
    oa       = @('是否可获取全文', 'oa', 'isOpenAccess', 'open_access')
}

function Normalize-Text {
    param([string]$Value)
    if ($null -eq $Value) { return '' }
    $normalized = ($Value.Trim().ToLowerInvariant() -replace [string][char]0xfeff, '')
    foreach ($token in @(' ', "`t", "`r", "`n", '_', '-', '/', '\')) {
        $normalized = $normalized.Replace($token, '')
    }
    return $normalized
}

function Test-Truthy {
    param([string]$Value)
    $normalized = Normalize-Text $Value
    if (-not $normalized) { return $false }
    foreach ($token in $yesTokens) {
        if ($normalized -eq (Normalize-Text $token)) {
            return $true
        }
    }
    return $false
}

function Get-RowValue {
    param(
        [pscustomobject]$Row,
        [string[]]$Aliases
    )
    $aliasSet = @{}
    foreach ($alias in $Aliases) {
        $normalizedAlias = Normalize-Text $alias
        if ($normalizedAlias) {
            $aliasSet[$normalizedAlias] = $true
        }
    }
    foreach ($property in $Row.PSObject.Properties) {
        $normalizedName = Normalize-Text $property.Name
        if ($normalizedName -and $aliasSet.ContainsKey($normalizedName)) {
            return [string]$property.Value
        }
    }
    return ''
}

function Get-CanonicalKey {
    param([pscustomobject]$Row)
    foreach ($fieldName in @('doi', 'pmid', 'pmcid', 'title')) {
        $value = Get-RowValue -Row $Row -Aliases $sourceAliases[$fieldName]
        if ($value) {
            return Normalize-Text $value
        }
    }
    return ''
}

function Get-Identifier {
    param(
        [pscustomobject]$Row,
        [int]$Sequence
    )
    foreach ($fieldName in @('pmid', 'pmcid', 'doi')) {
        $value = Get-RowValue -Row $Row -Aliases $sourceAliases[$fieldName]
        if ($value) {
            return $value
        }
    }
    return ('IMPORT-{0:d4}' -f $Sequence)
}

function Get-SourceType {
    param([string[]]$Headers)
    $normalized = @{}
    foreach ($header in $Headers) {
        $normalizedHeader = Normalize-Text $header
        if ($normalizedHeader) {
            $normalized[$normalizedHeader] = $true
        }
    }
    if ($normalized.ContainsKey('pmid') -or $normalized.ContainsKey('pmcid') -or $normalized.ContainsKey('sourcequeries')) {
        return 'europepmc'
    }
    if ($normalized.ContainsKey('articletitle') -and $normalized.ContainsKey('authors') -and $normalized.ContainsKey('pmid')) {
        return 'pubmed'
    }
    return 'generic'
}

$rowsOut = New-Object System.Collections.Generic.List[object]
$seenKeys = @{}
$duplicateCount = 0
$importedCount = 0

foreach ($inputFile in $InputFiles) {
    $resolvedInput = [System.IO.Path]::GetFullPath($inputFile)
    $rows = Import-Csv -LiteralPath $resolvedInput -Encoding UTF8
    $headers = @()
    if ($rows.Count -gt 0) {
        $headers = $rows[0].PSObject.Properties.Name
    }
    $sourceType = Get-SourceType -Headers $headers
    $currentDatabaseName = if ($DatabaseName) { $DatabaseName } else { $sourceType }

    foreach ($row in $rows) {
        $importedCount += 1
        $key = Get-CanonicalKey -Row $row
        $duplicateTarget = if ($key -and $seenKeys.ContainsKey($key)) { $seenKeys[$key] } else { $null }

        $mapped = [ordered]@{}
        foreach ($header in $candidateHeaders) {
            $mapped[$header] = ''
        }

        $mapped['文献编号'] = Get-Identifier -Row $row -Sequence $importedCount
        $mapped['检索批次'] = $BatchName
        $mapped['数据库/来源'] = $currentDatabaseName
        $mapped['检索日期'] = $RetrievalDate
        $mapped['题名'] = Get-RowValue -Row $row -Aliases $sourceAliases.title
        $mapped['作者'] = Get-RowValue -Row $row -Aliases $sourceAliases.authors
        $mapped['年份'] = Get-RowValue -Row $row -Aliases $sourceAliases.year
        $mapped['来源期刊/会议/出版社'] = Get-RowValue -Row $row -Aliases $sourceAliases.venue
        $mapped['DOI/链接'] = Get-RowValue -Row $row -Aliases $sourceAliases.doi
        $mapped['文献类型'] = Get-RowValue -Row $row -Aliases $sourceAliases.type
        $mapped['研究设计/方法类型'] = Get-RowValue -Row $row -Aliases $sourceAliases.design
        $mapped['子主题标签'] = (Get-RowValue -Row $row -Aliases $sourceAliases.subtheme)
        if (-not $mapped['子主题标签']) {
            $mapped['子主题标签'] = $DefaultSubtheme
        }
        $mapped['去重状态'] = if ($null -eq $duplicateTarget) { '保留' } else { "重复 -> $duplicateTarget" }
        $mapped['是否可获取全文'] = if (Test-Truthy (Get-RowValue -Row $row -Aliases $sourceAliases.oa)) { '是' } else { '' }
        $mapped['备注'] = "schema=$schemaVersion; source_file=$([System.IO.Path]::GetFileName($resolvedInput))"

        $rowsOut.Add([pscustomobject]$mapped)

        if ($key -and $null -eq $duplicateTarget) {
            $seenKeys[$key] = $mapped['文献编号']
        }
        elseif ($null -ne $duplicateTarget) {
            $duplicateCount += 1
        }
    }
}

$resolvedOutput = [System.IO.Path]::GetFullPath($Output)
$null = New-Item -ItemType Directory -Path (Split-Path $resolvedOutput -Parent) -Force
$rowsOut | Export-Csv -LiteralPath $resolvedOutput -NoTypeInformation -Encoding UTF8

Write-Output "[OK] 已写出候选文献表: $resolvedOutput"
Write-Output "[OK] schema=$schemaVersion; imported=$importedCount; duplicates=$duplicateCount; retained=$($importedCount - $duplicateCount)"
