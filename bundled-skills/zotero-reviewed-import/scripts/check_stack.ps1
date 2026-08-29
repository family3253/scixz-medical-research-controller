$ErrorActionPreference = "Stop"

$profile = Join-Path $env:APPDATA "Zotero\Zotero\Profiles\jgzdgd0j.default"
$prefs = Join-Path $profile "prefs.js"
$zoteroExe = "C:\Program Files\Zotero\zotero.exe"
$wordExe = "C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
$wpsExe = "C:\Program Files\WPS Office\office6\wps.exe"
$localApiUrl = "http://127.0.0.1:23119/api/"

if (Test-Path $zoteroExe) {
    Start-Process -FilePath $zoteroExe | Out-Null
    Start-Sleep -Seconds 4
}

$localApiOk = $false
try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $localApiUrl -TimeoutSec 5
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
        $localApiOk = $true
    }
} catch {
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode.value__ -eq 403) {
        $localApiOk = $true
    } else {
        $localApiOk = $false
    }
}

$prefsText = if (Test-Path $prefs) { Get-Content $prefs -Raw } else { "" }
$bbtInstalled = $prefsText -match "better-bibtex@iris-advies.com"
$wordIntegration = $prefsText -match "extensions.zoteroWinWordIntegration.version"
$localApiEnabled = $prefsText -match 'extensions\.zotero\.httpServer\.localAPI\.enabled", true'
$codexConfig = Join-Path $env:USERPROFILE ".codex\config.toml"

[pscustomobject]@{
    zotero_installed = Test-Path $zoteroExe
    zotero_local_api_enabled = $localApiEnabled
    zotero_local_api_reachable = $localApiOk
    better_bibtex_installed = $bbtInstalled
    word_installed = Test-Path $wordExe
    word_integration_present = $wordIntegration
    wps_installed = Test-Path $wpsExe
    codex_zotero_mcp_configured = (Select-String -Path $codexConfig -Pattern '\[mcp_servers\.zotero\]' -Quiet)
} | Format-List
