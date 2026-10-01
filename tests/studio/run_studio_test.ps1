# Автопроверка в настоящей Roblox Studio.
# Собирает тестовое место, ставит временный плагин, запускает Studio, ждёт отчёт в журнале Studio,
# печатает его, закрывает Studio и удаляет плагин.
# Запуск из папки проекта:  powershell -ExecutionPolicy Bypass -File tests\studio\run_studio_test.ps1

param([switch]$Shots)  # -Shots: сценарий задерживается на каждом экране, а окно Studio снимается в build\shots

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$rojo = Join-Path $root "tools\bin\rojo.exe"
$plugins = Join-Path $env:LOCALAPPDATA "Roblox\Plugins"
$pluginFile = Join-Path $plugins "EgeDuelAutotestPlugin.rbxm"
$place = Join-Path $root "build\ege-duel-autotest.rbxlx"
$logs = Join-Path $env:LOCALAPPDATA "Roblox\logs"

$studio = Get-ChildItem (Join-Path $env:LOCALAPPDATA "Roblox\Versions") -Recurse -Filter RobloxStudioBeta.exe |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $studio) { throw "Roblox Studio не найдена" }
if (Get-Process RobloxStudioBeta -ErrorAction SilentlyContinue) { throw "Сначала закройте Roblox Studio" }

New-Item -ItemType Directory -Force $plugins, (Split-Path $place) | Out-Null
& $rojo build (Join-Path $PSScriptRoot "plugin.project.json") -o $pluginFile | Out-Null
$project = if ($Shots) { "shots.project.json" } else { "test.project.json" }
& $rojo build (Join-Path $PSScriptRoot $project) -o $place | Out-Null
if ($Shots) {
    Start-Process powershell -WindowStyle Hidden -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "`"$(Join-Path $PSScriptRoot 'capture_window.ps1')`"", "-Seconds", "150" | Out-Null
}

$started = Get-Date
$process = Start-Process -FilePath $studio.FullName -ArgumentList "-task", "EditFile", "-localPlaceFile", "`"$place`"" -PassThru
$finished = $false
$lines = @()
try {
    $deadline = (Get-Date).AddSeconds(300)
    while ((Get-Date) -lt $deadline -and -not $finished) {
        Start-Sleep -Seconds 3
        $log = Get-ChildItem $logs -Filter "*Studio*" | Where-Object { $_.LastWriteTime -gt $started -and $_.Name -notlike "*Installer*" } |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($log) {
            $lines = @(Select-String -Path $log.FullName -Pattern "EGETEST|\[Bank\]" | ForEach-Object { ($_.Line -replace "^.*\[FLog::Creator\w+\] ", "") })
            $finished = [bool]($lines | Where-Object { $_ -match "EGETEST PLUGIN END" })
        }
    }
}
finally {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force }
    Remove-Item $pluginFile -Force -ErrorAction SilentlyContinue
}

$lines | Where-Object { $_ -notmatch "PLUGIN RESULT" } | ForEach-Object { Write-Output $_ }
$failed = @($lines | Where-Object { $_ -match "EGETEST (FAIL|CLIENT ERROR|SERVER ERROR|TIMEOUT)" })
if (-not $finished) { Write-Output "ИТОГ: Studio не прислала отчёт за 5 минут"; exit 2 }
if ($failed.Count -gt 0) { Write-Output "ИТОГ: есть провалы ($($failed.Count))"; exit 1 }
Write-Output "ИТОГ: все проверки в Studio пройдены"
