Add-Type -AssemblyName System.Drawing

$src = (Resolve-Path "work\shots\shot6.png").Path
$bmp = New-Object System.Drawing.Bitmap($src)
$w = [int]$bmp.Width
$h = [int]$bmp.Height

$x0 = [int]($w * 0.55)
$x1 = [int]($w * 0.92)
$y0 = [int]($h * 0.18)
$y1 = [int]($h * 0.95)
$cw = [int]($x1 - $x0)
$ch = [int]($y1 - $y0)

$scale = 3
$out = New-Object System.Drawing.Bitmap ([int]($cw * $scale)), ([int]($ch * $scale))
$g = [System.Drawing.Graphics]::FromImage($out)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$rect = New-Object System.Drawing.Rectangle 0, 0, $out.Width, $out.Height
$srcRect = New-Object System.Drawing.Rectangle $x0, $y0, $cw, $ch
$g.DrawImage($bmp, $rect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
$g.Dispose()
$out.Save("$PWD\work\shots\crop_b.png", [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$out.Dispose()
"cropped: ${cw}x${ch} -> $($cw * $scale)x$($ch * $scale)"
