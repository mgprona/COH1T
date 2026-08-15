# COH1T Thai Mod Installer
# ใช้คู่กับ: patch.json + RelicCOH.English.ucs + uninstall.bat

$ErrorActionPreference = "Stop"

$PatchFile = Join-Path $PSScriptRoot "patch.json"
$UcsFile = Join-Path $PSScriptRoot "RelicCOH.English.ucs"

function Find-GameDir {
    $steam = (Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Valve\Steam" -Name "InstallPath" -ErrorAction SilentlyContinue).InstallPath
    if ($steam) {
        $p = Join-Path $steam "steamapps\common\Company of Heroes Relaunch"
        if (Test-Path (Join-Path $p "RelicCOH.exe")) { return $p }
    }
    $p2 = "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch"
    if (Test-Path (Join-Path $p2 "RelicCOH.exe")) { return $p2 }
    throw "หาโฟลเดอร์เกมไม่เจอ — ติดตั้งเกมผ่าน Steam ก่อน หรือแก้สคริปต์ระบุ path เอง"
}

function Get-Sha256($path) {
    (Get-FileHash -Path $path -Algorithm SHA256).Hash.ToLower()
}

$Game = Find-GameDir
$Sga = Join-Path $Game "Engine\Archives\Engine.sga"
$Ucs = Join-Path $Game "CoH\Engine\Locale\English\RelicCOH.English.ucs"

if (Get-Process RelicCOH -ErrorAction SilentlyContinue) {
    Write-Host "[!] ปิดเกมก่อนติดตั้ง" -ForegroundColor Red
    exit 1
}

$patch = Get-Content $PatchFile -Raw | ConvertFrom-Json
$current = Get-Sha256 $Sga

if ($current -eq $patch.patched_sha256) {
    Write-Host "[OK] ติดตั้งไว้แล้ว (Engine.sga ตรงกับเวอร์ชันม็อด)" -ForegroundColor Green
    exit 0
}
if ($current -ne $patch.vanilla_sha256) {
    Write-Host "[!] Engine.sga ไม่ตรงกับเวอร์ชันเกมต้นฉบับ — ให้เปิด Steam คลิกขวาเกม > Properties > Installed Files > Verify integrity แล้วลองใหม่" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] สำรองไฟล์ต้นฉบับ..."
Copy-Item $Sga "$Sga.bak" -Force
Copy-Item $Ucs "$Ucs.bak" -Force

Write-Host "[2/4] ใส่ฟอนต์ไทย (patch $($patch.blocks.Count) blocks)..."
$bytes = [System.IO.File]::ReadAllBytes($Sga)
foreach ($blk in $patch.blocks) {
    $off = [int]$blk[0]
    $data = [Convert]::FromBase64String($blk[1])
    [Array]::Copy($data, 0, $bytes, $off, $data.Length)
}
[System.IO.File]::WriteAllBytes($Sga, $bytes)

Write-Host "[3/4] ใส่ข้อความแปลไทย..."
Copy-Item $UcsFile $Ucs -Force

Write-Host "[4/4] ตรวจสอบ..."
$final = Get-Sha256 $Sga
if ($final -ne $patch.patched_sha256) {
    Write-Host "[!] แพตช์ไม่สมบูรณ์ — กำลังคืนไฟล์เดิม..." -ForegroundColor Red
    Copy-Item "$Sga.bak" $Sga -Force
    Copy-Item "$Ucs.bak" $Ucs -Force
    exit 1
}

Write-Host ""
Write-Host "=== ติดตั้งสำเร็จ! เปิดเกมได้เลย (Settings ยังเป็น English — ข้อความเป็นไทยอัตโนมัติ) ===" -ForegroundColor Green
Write-Host "ถอนม็อด: รัน uninstall.bat"
