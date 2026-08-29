param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ProjectDirectory,
    [string]$CandidateCsv = '',
    [string]$AbstractScreenCsv = '',
    [string]$FulltextScreenCsv = '',
    [string]$FulltextReviewCsv = '',
    [string]$EvidenceCsv = '',
    [string]$Output = ''
)

$schema = Import-PowerShellDataFile -Path (Join-Path $PSScriptRoot 'review_project_schema.psd1')
$projectDefaults = $schema.ProjectDefaultPaths
$schemaVersion = $schema.SchemaVersion

$yesTokens = @('1', 'true', 'yes', 'y', '是', '纳入', '进入', '进入全文', 'included', 'include', 'keep', '保留')
$duplicateTokens = @('duplicate', 'duplicated', 'dup', '重复', '重复文献', '已重复', '排除重复', 'remove_duplicate')
$fieldAliases = @{
    subtheme = @('子主题标签', '一级子主题', 'subtheme', 'subtheme_tag')
    dedupe_status = @('去重状态', 'dedupe_status')
    doi = @('DOI/链接', 'doi/链接', 'doi', 'link')
    title = @('题名', 'title')
    pmid = @('pmid', 'PMID')
    abstract_include = @('是否进入全文阶段', '是否进入全文', 'enter_fulltext', 'included')
    fulltext_include = @('是否纳入', 'included', '纳入')
    grade = @('等级(A/B/C/D)', '等级', 'grade')
    core_read = @('是否核心精读', 'core_reading', 'is_core')
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

function Test-Blank {
    param([string]$Value)
    return [string]::IsNullOrWhiteSpace($Value)
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

function Test-LooksDuplicate {
    param([string]$Value)
    $normalized = Normalize-Text $Value
    if (-not $normalized) { return $false }
    foreach ($token in $duplicateTokens) {
        if ($normalized.Contains((Normalize-Text $token))) {
            return $true
        }
    }
    return $false
}

function Get-FieldValue {
    param(
        [pscustomobject]$Row,
        [string]$FieldName
    )
    $aliasSet = @{}
    foreach ($alias in $fieldAliases[$FieldName]) {
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

function Get-CanonicalCandidateKey {
    param([pscustomobject]$Row)
    foreach ($fieldName in @('doi', 'pmid', 'title')) {
        $value = Get-FieldValue -Row $Row -FieldName $fieldName
        if (-not (Test-Blank $value)) {
            return Normalize-Text $value
        }
    }
    return ''
}

function Import-RowsSafe {
    param([string]$PathValue)
    if (-not (Test-Path -LiteralPath $PathValue)) {
        return @()
    }
    return @(Import-Csv -LiteralPath $PathValue -Encoding UTF8)
}

function Test-NonEmptyRow {
    param([pscustomobject]$Row)
    foreach ($property in $Row.PSObject.Properties) {
        if (-not (Test-Blank ([string]$property.Value))) {
            return $true
        }
    }
    return $false
}

function Get-SubthemeCounts {
    param([object[]]$Rows)
    $counts = @{}
    foreach ($row in $Rows) {
        $subtheme = Get-FieldValue -Row $row -FieldName 'subtheme'
        if (-not (Test-Blank $subtheme)) {
            if (-not $counts.ContainsKey($subtheme)) {
                $counts[$subtheme] = 0
            }
            $counts[$subtheme] += 1
        }
    }
    return $counts
}

function Escape-MermaidLabel {
    param([string]$Value)
    if ($null -eq $Value) { return '' }
    return ($Value.Replace('"', "'"))
}

$resolvedProject = [System.IO.Path]::GetFullPath($ProjectDirectory)
$candidatePath = if ($CandidateCsv) { [System.IO.Path]::GetFullPath($CandidateCsv) } else { Join-Path $resolvedProject $projectDefaults.candidate_csv }
$abstractPath = if ($AbstractScreenCsv) { [System.IO.Path]::GetFullPath($AbstractScreenCsv) } else { Join-Path $resolvedProject $projectDefaults.abstract_screen_csv }
$fulltextScreenPath = if ($FulltextScreenCsv) { [System.IO.Path]::GetFullPath($FulltextScreenCsv) } else { Join-Path $resolvedProject $projectDefaults.fulltext_screen_csv }
$fulltextReviewPath = if ($FulltextReviewCsv) { [System.IO.Path]::GetFullPath($FulltextReviewCsv) } else { Join-Path $resolvedProject $projectDefaults.fulltext_review_csv }
$evidencePath = if ($EvidenceCsv) { [System.IO.Path]::GetFullPath($EvidenceCsv) } else { Join-Path $resolvedProject $projectDefaults.evidence_csv }
$outputPath = if ($Output) { [System.IO.Path]::GetFullPath($Output) } else { Join-Path $resolvedProject $projectDefaults.visual_summary_md }

$candidateRows = Import-RowsSafe -PathValue $candidatePath
$abstractRows = Import-RowsSafe -PathValue $abstractPath
$fulltextScreenRows = Import-RowsSafe -PathValue $fulltextScreenPath
$fulltextReviewRows = Import-RowsSafe -PathValue $fulltextReviewPath
$evidenceRows = Import-RowsSafe -PathValue $evidencePath

$dedupedCandidates = 0
if ($candidateRows.Count -gt 0) {
    $hasDedupeField = $false
    foreach ($row in $candidateRows) {
        if (-not (Test-Blank (Get-FieldValue -Row $row -FieldName 'dedupe_status'))) {
            $hasDedupeField = $true
            break
        }
    }
    if ($hasDedupeField) {
        $dedupedCandidates = (@($candidateRows | Where-Object { -not (Test-LooksDuplicate (Get-FieldValue -Row $_ -FieldName 'dedupe_status')) })).Count
    }
    else {
        $unique = @{}
        foreach ($row in $candidateRows) {
            $key = Get-CanonicalCandidateKey -Row $row
            if ($key) {
                $unique[$key] = $true
            }
        }
        $dedupedCandidates = if ($unique.Count -gt 0) { $unique.Count } else { $candidateRows.Count }
    }
}

$abstractIncludedRows = @($abstractRows | Where-Object { Test-Truthy (Get-FieldValue -Row $_ -FieldName 'abstract_include') })
$fulltextIncludedRows = @($fulltextScreenRows | Where-Object { Test-Truthy (Get-FieldValue -Row $_ -FieldName 'fulltext_include') })
$reviewedRows = @($fulltextReviewRows | Where-Object { Test-NonEmptyRow $_ })
$coreReviewRows = @($fulltextReviewRows | Where-Object { Test-Truthy (Get-FieldValue -Row $_ -FieldName 'core_read') })
$evidenceRowsNonEmpty = @($evidenceRows | Where-Object { Test-NonEmptyRow $_ })

$gradeCounts = [ordered]@{ A = 0; B = 0; C = 0; D = 0 }
foreach ($row in $fulltextScreenRows) {
    if (-not (Test-Truthy (Get-FieldValue -Row $row -FieldName 'fulltext_include'))) {
        continue
    }
    $grade = (Normalize-Text (Get-FieldValue -Row $row -FieldName 'grade')).ToUpperInvariant()
    if ($gradeCounts.Contains($grade)) {
        $gradeCounts[$grade] += 1
    }
}

$subthemeCounts = Get-SubthemeCounts -Rows $evidenceRowsNonEmpty
if ($subthemeCounts.Count -eq 0) {
    $subthemeCounts = Get-SubthemeCounts -Rows $fulltextIncludedRows
}
if ($subthemeCounts.Count -eq 0) {
    $subthemeCounts = Get-SubthemeCounts -Rows $abstractIncludedRows
}
$subthemeKeys = @($subthemeCounts.Keys | Sort-Object)

$flowLines = @(
    '```mermaid',
    'flowchart TD',
    ('    A["候选文献\n{0}"] --> B["去重后\n{1}"]' -f $candidateRows.Count, $dedupedCandidates),
    ('    B --> C["摘要筛选保留\n{0}"]' -f $abstractIncludedRows.Count),
    ('    C --> D["全文筛选纳入\n{0}"]' -f $fulltextIncludedRows.Count),
    ('    D --> E["完成全文评阅\n{0}"]' -f $reviewedRows.Count),
    ('    E --> F["核心精读\n{0}"]' -f $coreReviewRows.Count),
    ('    F --> G["证据提取\n{0}"]' -f $evidenceRowsNonEmpty.Count),
    '```'
)

$gradeChartLines = @()
if (($gradeCounts.Values | Measure-Object -Sum).Sum -gt 0) {
    $gradeChartLines += '```mermaid'
    $gradeChartLines += 'pie showData'
    $gradeChartLines += '    title 全文筛选等级分布'
    foreach ($grade in @('A', 'B', 'C', 'D')) {
        if ($gradeCounts[$grade] -gt 0) {
            $gradeChartLines += ('    "{0}" : {1}' -f $grade, $gradeCounts[$grade])
        }
    }
    $gradeChartLines += '```'
}

$subthemeChartLines = @()
if ($subthemeKeys.Count -gt 0) {
    $subthemeChartLines += '```mermaid'
    $subthemeChartLines += 'pie showData'
    $subthemeChartLines += '    title 子主题覆盖分布'
    foreach ($key in $subthemeKeys) {
        $subthemeChartLines += ('    "{0}" : {1}' -f (Escape-MermaidLabel $key), $subthemeCounts[$key])
    }
    $subthemeChartLines += '```'
}

$reportLines = New-Object System.Collections.Generic.List[string]
$reportLines.Add('# 统计图表草案')
$reportLines.Add('')
$reportLines.Add("- 项目目录：$resolvedProject")
$reportLines.Add("- schema：$schemaVersion")
$reportLines.Add("- 生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
$reportLines.Add('')
$reportLines.Add('## 概览')
$reportLines.Add("| 指标 | 数值 |")
$reportLines.Add("|---|---:|")
$reportLines.Add("| 候选文献总量 | $($candidateRows.Count) |")
$reportLines.Add("| 去重后进入初筛 | $dedupedCandidates |")
$reportLines.Add("| 摘要筛选保留 | $($abstractIncludedRows.Count) |")
$reportLines.Add("| 全文筛选纳入 | $($fulltextIncludedRows.Count) |")
$reportLines.Add("| 完成全文评阅 | $($reviewedRows.Count) |")
$reportLines.Add("| 核心精读 | $($coreReviewRows.Count) |")
$reportLines.Add("| 证据提取 | $($evidenceRowsNonEmpty.Count) |")
$reportLines.Add('')
$reportLines.Add('## 图1 草案：筛选流程图')
foreach ($line in $flowLines) { $reportLines.Add($line) }
$reportLines.Add('')

$reportLines.Add('## 图2 草案：全文筛选等级分布')
if ($gradeChartLines.Count -gt 0) {
    foreach ($line in $gradeChartLines) { $reportLines.Add($line) }
}
else {
    $reportLines.Add('- 当前未发现可绘制的等级分布数据。')
}
$reportLines.Add('')

$reportLines.Add('## 图3 草案：子主题覆盖分布')
if ($subthemeChartLines.Count -gt 0) {
    foreach ($line in $subthemeChartLines) { $reportLines.Add($line) }
}
else {
    $reportLines.Add('- 当前未发现可绘制的子主题覆盖数据。')
}
$reportLines.Add('')

$reportLines.Add('## 可直接写入图表规划模板的建议')
$reportLines.Add('| 图表编号 | 类型 | 目的 | 主要内容 | 证据/数据来源 | 对应章节 | 状态 |')
$reportLines.Add('|---|---|---|---|---|---|---|')
$reportLines.Add('| 图1 | Mermaid流程图 | 展示筛选链路与保留数量 | 候选文献 -> 去重 -> 摘要筛选 -> 全文筛选 -> 评阅 -> 核心精读 -> 证据提取 | 候选池/筛选/评阅/证据表 | 引言或方法部分 | 草案 |')
$reportLines.Add('| 图2 | Mermaid饼图 | 展示全文筛选等级结构 | A/B/C/D 等级分布 | 全文筛选记录表 | 代表性证据比较 | 草案 |')
$reportLines.Add('| 图3 | Mermaid饼图 | 展示子主题覆盖均衡性 | 子主题对应的保留/证据数量 | 全文筛选记录表或证据提取表 | 主要研究方向或主题模块 | 草案 |')
$reportLines.Add('')

if ($subthemeKeys.Count -gt 0) {
    $reportLines.Add('## 子主题覆盖表')
    $reportLines.Add('| 子主题 | 数量 |')
    $reportLines.Add('|---|---:|')
    foreach ($key in $subthemeKeys) {
        $reportLines.Add("| $key | $($subthemeCounts[$key]) |")
    }
    $reportLines.Add('')
}

$null = New-Item -ItemType Directory -Path (Split-Path $outputPath -Parent) -Force
$reportLines -join "`n" | Set-Content -LiteralPath $outputPath -Encoding UTF8
Write-Output "[OK] 已生成统计图表草案: $outputPath"
