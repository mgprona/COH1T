Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$game = "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch\RelicCOH.exe"
$outDir = "C:\Users\MennzKTR\Desktop\COH1T\work\shots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$p = Start-Process -FilePath $game -ArgumentList "-dev" -WorkingDirectory "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch" -PassThru
Start-Sleep -Seconds 12

$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
for ($i = 1; $i -le 6; $i++) {
    $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $path = Join-Path $outDir ("shot{0}.png" -f $i)
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Output "saved $path"
    Start-Sleep -Seconds 3
}

Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
Write-Output "game closed"
