param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ProjectDirectory,
    [ValidateSet('A', 'B', 'C', 'D')]
    [string]$GateProfile = 'A',
    [int]$CurrentYear = (Get-Date).Year,
    [string]$CandidateCsv = '',
    [string]$AbstractScreenCsv = '',
    [string]$FulltextScreenCsv = '',
    [string]$FulltextReviewCsv = '',
    [string]$EvidenceCsv = '',
    [string]$Output = '',
    [switch]$Strict
)

$schema = Import-PowerShellDataFile -Path (Join-Path $PSScriptRoot 'review_project_schema.psd1')
$projectDefaults = $schema.ProjectDefaultPaths
$fixedGates = $schema.FixedGates
$schemaVersion = $schema.SchemaVersion

$yesTokens = @('1', 'true', 'yes', 'y', '是', '纳入', '进入', '进入全文', 'included', 'include', 'keep', '保留')
$duplicateTokens = @('duplicate', 'duplicated', 'dup', '重复', '重复文献', '已重复', '排除重复', 'remove_duplicate')
$coreRoleTokens = @('核心', '主论点', '直接支撑', 'core', 'primary', 'claim')
$fieldAliases = @{
    year = @('年份', 'year', 'pubyear', 'publicationyear')
    subtheme = @('子主题标签', '一级子主题', 'subtheme', 'subtheme_tag')
    dedupe_status = @('去重状态', 'dedupe_status')
    doi = @('DOI/链接', 'doi/链接', 'doi', 'link')
    title = @('题名', 'title')
    pmid = @('pmid', 'PMID')
    abstract_include = @('是否进入全文阶段', '是否进入全文', 'enter_fulltext', 'included')
    fulltext_include = @('是否纳入', 'included', '纳入')
    grade = @('等级(A/B/C/D)', '等级', 'grade')
    review_status = @('评阅状态', 'review_status')
    core_read = @('是否核心精读', 'core_reading', 'is_core')
    quality = @('质量评价/偏倚风险', '质量评价', '偏倚风险', 'risk_of_bias', 'quality_assessment')
    evidence_role = @('综述中的作用', '证据用途', 'role')
    conflict = @('与其他研究的矛盾点', '矛盾点', 'conflict')
    trace = @('可追溯引文页码/位置', '页码/位置', 'trace', 'page_locator')
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

function Test-LooksCoreRole {
    param([string]$Value)
    $normalized = Normalize-Text $Value
    if (-not $normalized) { return $false }
    foreach ($token in $coreRoleTokens) {
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

function Get-YearValue {
    param([pscustomobject]$Row)
    $value = Get-FieldValue -Row $Row -FieldName 'year'
    if (Test-Blank $value) { return $null }
    $digits = -join ($value.ToCharArray() | Where-Object { [char]::IsDigit($_) })
    if ($digits.Length -lt 4) { return $null }
    $year = [int]$digits.Substring(0, 4)
    if ($year -ge 1900 -and $year -le 2100) {
        return $year
    }
    return $null
}

function Import-RowsSafe {
    param([string]$PathValue)
    if (-not (Test-Path -LiteralPath $PathValue)) {
        return @{
            Rows = @()
            Error = "缺少文件: $PathValue"
        }
    }
    return @{
        Rows = @(Import-Csv -LiteralPath $PathValue -Encoding UTF8)
        Error = $null
    }
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

function Get-RecentCounts {
    param(
        [object[]]$Rows,
        [int]$ReferenceYear,
        [int]$WithinYears
    )
    $years = @()
    foreach ($row in $Rows) {
        $yearValue = Get-YearValue -Row $row
        if ($null -ne $yearValue) {
            $years += $yearValue
        }
    }
    if ($years.Count -eq 0) {
        return @{
            Recent = 0
            Total = 0
        }
    }
    $floorYear = $ReferenceYear - $WithinYears + 1
    $recent = ($years | Where-Object { $_ -ge $floorYear }).Count
    return @{
        Recent = $recent
        Total = $years.Count
    }
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

function Format-Ratio {
    param([double]$Numerator, [double]$Denominator)
    if ($Denominator -le 0) { return '无法计算' }
    return ('{0:N1}%' -f (($Numerator / $Denominator) * 100))
}

function Get-StatusLine {
    param(
        [bool]$Passed,
        [string]$Label,
        [string]$Detail
    )
    $marker = if ($Passed) { 'PASS' } else { 'FAIL' }
    return "- [$marker] ${Label}: $Detail"
}

function Get-WarnLine {
    param([string]$Label, [string]$Detail)
    return "- [WARN] ${Label}: $Detail"
}

$resolvedProject = [System.IO.Path]::GetFullPath($ProjectDirectory)
$candidatePath = if ($CandidateCsv) { [System.IO.Path]::GetFullPath($CandidateCsv) } else { Join-Path $resolvedProject $projectDefaults.candidate_csv }
$abstractPath = if ($AbstractScreenCsv) { [System.IO.Path]::GetFullPath($AbstractScreenCsv) } else { Join-Path $resolvedProject $projectDefaults.abstract_screen_csv }
$fulltextScreenPath = if ($FulltextScreenCsv) { [System.IO.Path]::GetFullPath($FulltextScreenCsv) } else { Join-Path $resolvedProject $projectDefaults.fulltext_screen_csv }
$fulltextReviewPath = if ($FulltextReviewCsv) { [System.IO.Path]::GetFullPath($FulltextReviewCsv) } else { Join-Path $resolvedProject $projectDefaults.fulltext_review_csv }
$evidencePath = if ($EvidenceCsv) { [System.IO.Path]::GetFullPath($EvidenceCsv) } else { Join-Path $resolvedProject $projectDefaults.evidence_csv }
$outputPath = if ($Output) { [System.IO.Path]::GetFullPath($Output) } else { Join-Path $resolvedProject $projectDefaults.gate_report_md }

$candidateLoad = Import-RowsSafe -PathValue $candidatePath
$abstractLoad = Import-RowsSafe -PathValue $abstractPath
$fulltextScreenLoad = Import-RowsSafe -PathValue $fulltextScreenPath
$fulltextReviewLoad = Import-RowsSafe -PathValue $fulltextReviewPath
$evidenceLoad = Import-RowsSafe -PathValue $evidencePath

$candidateRows = @($candidateLoad.Rows)
$abstractRows = @($abstractLoad.Rows)
$fulltextScreenRows = @($fulltextScreenLoad.Rows)
$fulltextReviewRows = @($fulltextReviewLoad.Rows)
$evidenceRows = @($evidenceLoad.Rows)

$errors = @()
foreach ($errorValue in @($candidateLoad.Error, $abstractLoad.Error, $fulltextScreenLoad.Error, $fulltextReviewLoad.Error, $evidenceLoad.Error)) {
    if ($errorValue) {
        $errors += $errorValue
    }
}

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
$directCoreEvidence = @($evidenceRowsNonEmpty | Where-Object { Test-LooksCoreRole (Get-FieldValue -Row $_ -FieldName 'evidence_role') })
if ($directCoreEvidence.Count -eq 0) {
    $directCoreEvidence = @($fulltextScreenRows | Where-Object {
        ((Normalize-Text (Get-FieldValue -Row $_ -FieldName 'grade')) -eq 'a') -and
        (Test-Truthy (Get-FieldValue -Row $_ -FieldName 'fulltext_include'))
    })
}

$qualityRows = @()
foreach ($row in @($fulltextReviewRows + $evidenceRowsNonEmpty)) {
    if (-not (Test-Blank (Get-FieldValue -Row $row -FieldName 'quality'))) {
        $qualityRows += $row
    }
}
$conflictRows = @($evidenceRowsNonEmpty | Where-Object { -not (Test-Blank (Get-FieldValue -Row $_ -FieldName 'conflict')) })
$traceRows = @($evidenceRowsNonEmpty | Where-Object { -not (Test-Blank (Get-FieldValue -Row $_ -FieldName 'trace')) })

$retainedRowsForYear = if ($fulltextIncludedRows.Count -gt 0) { $fulltextIncludedRows } else { $abstractIncludedRows }
$coreRowsForYear = if ($evidenceRowsNonEmpty.Count -gt 0) { $evidenceRowsNonEmpty } else { $coreReviewRows }
$recentFive = Get-RecentCounts -Rows $retainedRowsForYear -ReferenceYear $CurrentYear -WithinYears 5
$recentThree = Get-RecentCounts -Rows $coreRowsForYear -ReferenceYear $CurrentYear -WithinYears 3

$subthemeCandidate = Get-SubthemeCounts -Rows $candidateRows
$subthemeRetained = Get-SubthemeCounts -Rows $(if ($fulltextIncludedRows.Count -gt 0) { $fulltextIncludedRows } else { $abstractIncludedRows })
$subthemeReviewed = Get-SubthemeCounts -Rows $reviewedRows
$subthemeCore = Get-SubthemeCounts -Rows $(if ($evidenceRowsNonEmpty.Count -gt 0) { $evidenceRowsNonEmpty } else { $coreReviewRows })
$allSubthemes = @($subthemeCandidate.Keys + $subthemeRetained.Keys + $subthemeReviewed.Keys + $subthemeCore.Keys | Sort-Object -Unique)

$reportLines = New-Object System.Collections.Generic.List[string]
$reportLines.Add('# 闸门检查报告')
$reportLines.Add('')
$reportLines.Add("- 项目目录：$resolvedProject")
$reportLines.Add("- schema：$schemaVersion")
$reportLines.Add("- 闸门档位：$GateProfile")
$reportLines.Add("- 生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
$reportLines.Add('')
$reportLines.Add('## 文件情况')
$reportLines.Add("- 候选文献表：$candidatePath（$($candidateRows.Count) 行）")
$reportLines.Add("- 摘要筛选记录表：$abstractPath（$($abstractRows.Count) 行）")
$reportLines.Add("- 全文筛选记录表：$fulltextScreenPath（$($fulltextScreenRows.Count) 行）")
$reportLines.Add("- 全文评阅登记表：$fulltextReviewPath（$($fulltextReviewRows.Count) 行）")
$reportLines.Add("- 证据提取表：$evidencePath（$($evidenceRows.Count) 行）")
$reportLines.Add('')

if ($errors.Count -gt 0) {
    $reportLines.Add('## 缺失或异常')
    foreach ($errorValue in $errors) {
        $reportLines.Add((Get-WarnLine -Label '文件读取' -Detail $errorValue))
    }
    $reportLines.Add('')
}

$reportLines.Add('## 核心统计')
$reportLines.Add('| 指标 | 数值 |')
$reportLines.Add('|---|---:|')
$reportLines.Add("| 候选文献总量 | $($candidateRows.Count) |")
$reportLines.Add("| 去重后进入初筛 | $dedupedCandidates |")
$reportLines.Add("| 初筛后保留 | $($abstractIncludedRows.Count) |")
$reportLines.Add("| 完成全文评阅 | $($reviewedRows.Count) |")
$reportLines.Add("| 核心精读 | $($coreReviewRows.Count) |")
$reportLines.Add("| 深度证据提取 | $($evidenceRowsNonEmpty.Count) |")
$reportLines.Add("| 可直接支撑主论点的核心证据 | $($directCoreEvidence.Count) |")
$reportLines.Add("| 已填写质量评价/偏倚风险 | $($qualityRows.Count) |")
$reportLines.Add("| 已记录证据矛盾点 | $($conflictRows.Count) |")
$reportLines.Add("| 已记录可追溯页码/位置 | $($traceRows.Count) |")
$reportLines.Add('')

$hardFailures = 0
if ($GateProfile -ne 'C') {
    $reportLines.Add('## 固定闸门检查')
    $metrics = @{
        '候选文献总量' = $candidateRows.Count
        '去重后进入初筛' = $dedupedCandidates
        '初筛后保留' = $abstractIncludedRows.Count
        '完成全文评阅' = $reviewedRows.Count
        '核心精读' = $coreReviewRows.Count
        '深度证据提取' = $evidenceRowsNonEmpty.Count
        '可直接支撑主论点的核心证据' = $directCoreEvidence.Count
    }
    foreach ($label in $fixedGates[$GateProfile].Keys) {
        $threshold = [int]$fixedGates[$GateProfile][$label]
        $actual = [int]$metrics[$label]
        if ($threshold -eq 0) {
            $reportLines.Add((Get-WarnLine -Label $label -Detail "当前档位不强制设定数量线，当前统计值为 $actual"))
            continue
        }
        $passed = $actual -ge $threshold
        if (-not $passed) {
            $hardFailures += 1
        }
        $reportLines.Add((Get-StatusLine -Passed $passed -Label $label -Detail "$actual / $threshold"))
    }
    $reportLines.Add('')
}
else {
    $reportLines.Add('## C 档过程完整性检查')
    $checks = @(
        @{ Passed = ($candidateRows.Count -gt 0); Label = '候选池记录'; Count = $candidateRows.Count },
        @{ Passed = ($abstractRows.Count -gt 0); Label = '摘要筛选记录'; Count = $abstractRows.Count },
        @{ Passed = ($fulltextScreenRows.Count -gt 0); Label = '全文筛选记录'; Count = $fulltextScreenRows.Count },
        @{ Passed = ($fulltextReviewRows.Count -gt 0); Label = '全文评阅记录'; Count = $fulltextReviewRows.Count },
        @{ Passed = ($evidenceRowsNonEmpty.Count -gt 0); Label = '证据提取记录'; Count = $evidenceRowsNonEmpty.Count },
        @{ Passed = ($qualityRows.Count -gt 0); Label = '质量评价/偏倚评价记录'; Count = $qualityRows.Count }
    )
    foreach ($check in $checks) {
        if (-not $check.Passed) {
            $hardFailures += 1
        }
        $reportLines.Add((Get-StatusLine -Passed $check.Passed -Label $check.Label -Detail "$($check.Count) 行"))
    }
    $reportLines.Add('')
}

$reportLines.Add('## 时效性检查')
$reportLines.Add((Get-WarnLine -Label '近五年占比' -Detail "$(Format-Ratio -Numerator $recentFive.Recent -Denominator $recentFive.Total)（基于保留文献，可计算样本 $($recentFive.Total)）"))
$reportLines.Add((Get-WarnLine -Label '近三年占比' -Detail "$(Format-Ratio -Numerator $recentThree.Recent -Denominator $recentThree.Total)（基于核心阅读/证据提取，可计算样本 $($recentThree.Total)）"))
$reportLines.Add('')

if ($allSubthemes.Count -gt 0) {
    $reportLines.Add('## 子主题覆盖')
    $reportLines.Add('| 子主题 | 候选池 | 保留 | 评阅 | 核心/证据 |')
    $reportLines.Add('|---|---:|---:|---:|---:|')
    foreach ($subtheme in $allSubthemes) {
        $candidateCount = if ($subthemeCandidate.ContainsKey($subtheme)) { $subthemeCandidate[$subtheme] } else { 0 }
        $retainedCount = if ($subthemeRetained.ContainsKey($subtheme)) { $subthemeRetained[$subtheme] } else { 0 }
        $reviewedCount = if ($subthemeReviewed.ContainsKey($subtheme)) { $subthemeReviewed[$subtheme] } else { 0 }
        $coreCount = if ($subthemeCore.ContainsKey($subtheme)) { $subthemeCore[$subtheme] } else { 0 }
        $reportLines.Add("| $subtheme | $candidateCount | $retainedCount | $reviewedCount | $coreCount |")
    }
    $reportLines.Add('')
}
else {
    $reportLines.Add('## 子主题覆盖')
    $reportLines.Add((Get-WarnLine -Label '子主题标签' -Detail '当前表格中未发现可统计的子主题标签'))
    $reportLines.Add('')
}

$reportLines.Add('## 记录完整性提示')
$reportLines.Add((Get-WarnLine -Label '质量评价/偏倚风险' -Detail '若当前任务是系统化证据综述或 umbrella review，应确保质量评价记录完整'))
$reportLines.Add((Get-WarnLine -Label '证据矛盾点' -Detail '若矛盾点记录过少，通常意味着综述的比较与批判部分还不够'))
$reportLines.Add((Get-WarnLine -Label '可追溯引文位置' -Detail '若页码/位置为空过多，后续反向核查会变得困难'))
$reportLines.Add('')

$blockerCount = $hardFailures + $errors.Count
$overallOk = $blockerCount -eq 0
$reportLines.Add('## 结论')
if ($overallOk) {
    $reportLines.Add('- 当前统计结果未发现硬性闸门失败项。')
}
else {
    $reportLines.Add("- 当前统计结果存在 $blockerCount 项未达线或关键文件缺失，暂不建议标记为当前档位完成稿。")
}

$null = New-Item -ItemType Directory -Path (Split-Path $outputPath -Parent) -Force
$reportLines -join "`n" | Set-Content -LiteralPath $outputPath -Encoding UTF8
Write-Output "[OK] 已生成闸门检查报告: $outputPath"

if ($Strict -and (-not $overallOk)) {
    exit 1
}
