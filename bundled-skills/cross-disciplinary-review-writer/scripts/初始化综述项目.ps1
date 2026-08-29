param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$OutputDirectory,
    [switch]$Force,
    [switch]$SkipExisting
)

if ($Force -and $SkipExisting) {
    throw '不能同时使用 -Force 和 -SkipExisting。'
}

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputDirectory)
$null = New-Item -ItemType Directory -Path $resolvedOutput -Force

$stageDirs = @(
    '00_选题说明',
    '01_检索策略',
    '02_候选池与筛选',
    '03_全文获取与评阅',
    '04_证据提取与阅读笔记',
    '05_写作框架与图表规划',
    '06_论点映射与提纲',
    '07_正文草稿',
    '08_修改与终检'
)

foreach ($dirName in $stageDirs) {
    $null = New-Item -ItemType Directory -Path (Join-Path $resolvedOutput $dirName) -Force
}

$assetsDir = Join-Path (Split-Path $PSScriptRoot -Parent) 'assets\模板资源'
$mapping = [ordered]@{
    '选题说明模板.md'       = '00_选题说明\选题说明.md'
    '检索策略模板.md'       = '01_检索策略\检索策略.md'
    '候选文献表模板.csv'     = '02_候选池与筛选\候选文献表.csv'
    '摘要筛选记录表模板.csv' = '02_候选池与筛选\摘要筛选记录表.csv'
    '全文获取登记表模板.csv' = '03_全文获取与评阅\全文获取登记表.csv'
    '全文筛选记录表模板.csv' = '03_全文获取与评阅\全文筛选记录表.csv'
    '全文评阅登记表模板.csv' = '03_全文获取与评阅\全文评阅登记表.csv'
    '证据提取表模板.csv'     = '04_证据提取与阅读笔记\证据提取表.csv'
    '阅读笔记模板.md'       = '04_证据提取与阅读笔记\阅读笔记模板.md'
    '写作框架模板.md'       = '05_写作框架与图表规划\写作框架说明.md'
    '图表规划模板.md'       = '05_写作框架与图表规划\图表规划.md'
    '统计图表草案模板.md'    = '05_写作框架与图表规划\统计图表草案.md'
    '论点映射模板.md'       = '06_论点映射与提纲\论点映射.md'
    '综述提纲模板.md'       = '06_论点映射与提纲\综述提纲.md'
    '初稿模板.md'          = '07_正文草稿\初稿_v1.md'
    '二轮修改清单模板.md'    = '08_修改与终检\二轮修改清单.md'
    '最终核查模板.md'       = '08_修改与终检\最终核查清单.md'
}

foreach ($entry in $mapping.GetEnumerator()) {
    $sourcePath = Join-Path $assetsDir $entry.Key
    $destinationPath = Join-Path $resolvedOutput $entry.Value
    $destinationDir = Split-Path $destinationPath -Parent
    $null = New-Item -ItemType Directory -Path $destinationDir -Force

    if (Test-Path -LiteralPath $destinationPath) {
        if ($SkipExisting) {
            continue
        }
        if (-not $Force) {
            throw "目标文件已存在: $destinationPath。使用 -Force 覆盖，或使用 -SkipExisting 跳过已有文件。"
        }
    }

    Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Force
}

Write-Output "[OK] 已初始化综述项目目录: $resolvedOutput"
