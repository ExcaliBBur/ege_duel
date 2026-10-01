# Снимает окно Roblox Studio (только его, не весь экран) раз в секунду, пока Studio работает.
# Нужен, чтобы посмотреть на экраны игры после автопроверки. Снимки складываются в build\shots.
# Запуск:  powershell -ExecutionPolicy Bypass -File tests\studio\capture_window.ps1 -Seconds 90

param([int]$Seconds = 90)

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$shots = Join-Path $root "build\shots"
New-Item -ItemType Directory -Force $shots | Out-Null
Get-ChildItem $shots -Filter *.png | Remove-Item -Force

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class EgeWindow {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
}
"@

$deadline = (Get-Date).AddSeconds($Seconds)
$index = 0
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 1000
    $studio = Get-Process RobloxStudioBeta -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if (-not $studio) { continue }
    $rect = New-Object EgeWindow+RECT
    [void][EgeWindow]::GetWindowRect($studio.MainWindowHandle, [ref]$rect)
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 100 -or $height -le 100) { continue }
    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $hdc = $graphics.GetHdc()
    [void][EgeWindow]::PrintWindow($studio.MainWindowHandle, $hdc, 2)
    $graphics.ReleaseHdc($hdc)
    $index += 1
    $bitmap.Save((Join-Path $shots ("shot-{0:d3}.png" -f $index)), [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
}
Write-Output "shots: $index"
