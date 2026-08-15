# COH1T Thai Mod Uninstaller

$ErrorActionPreference = "Continue"

function Find-GameDir {
    $steam = (Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Valve\Steam" -Name "InstallPath" -ErrorAction SilentlyContinue).InstallPath
    if ($steam) {
        $p = Join-Path $steam "steamapps\common\Company of Heroes Relaunch"
        if (Test-Path (Join-Path $p "RelicCOH.exe")) { return $p }
    }
    $p2 = "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch"
    if (Test-Path (Join-Path $p2 "RelicCOH.exe")) { return $p2 }
    return $null
}

if (Get-Process RelicCOH -ErrorAction SilentlyContinue) {
    Write-Host "[!] ปิดเกมก่อนถอนม็อด" -ForegroundColor Red
    exit 1
}

$Game = Find-GameDir
if (-not $Game) { Write-Host "หาโฟลเดอร์เกมไม่เจอ"; exit 1 }

$Sga = Join-Path $Game "Engine\Archives\Engine.sga"
$Ucs = Join-Path $Game "CoH\Engine\Locale\English\RelicCOH.English.ucs"

$ok = $true
foreach ($f in @($Sga, $Ucs)) {
    if (Test-Path "$f.bak") {
        Copy-Item "$f.bak" $f -Force
        Write-Host "[OK] คืน $f"
    } else {
        Write-Host "[!] ไม่มี backup: $f (ปล่อยไว้แบบเดิม)" -ForegroundColor Yellow
        $ok = $false
    }
}

if ($ok) {
    Write-Host "=== ถอนม็อดแล้ว เกมกลับเป็นอังกฤษต้นฉบับ ===" -ForegroundColor Green
} else {
    Write-Host "ถอนไม่สมบูรณ์ — ใช้ Steam Verify integrity แล้วลงใหม่ถ้าต้องการ" -ForegroundColor Yellow
}
