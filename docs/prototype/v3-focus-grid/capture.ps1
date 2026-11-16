# Captures every wireframe screen to PNG with headless Microsoft Edge.
# Usage (from anywhere):  powershell -ExecutionPolicy Bypass -File capture.ps1
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$dir  = $PSScriptRoot
$page = 'file:///' + (($dir -replace '\\', '/') -replace ' ', '%20') + '/wireframe.html'
$tmp  = Join-Path $env:TEMP 'study-station-wireframe-edge'

# name, query, width, minimum height, device scale
$shots = @(
  @('01-dang-nhap-desktop',          'screen=dang-nhap',               1440, 900, 1),
  @('02-dang-ky-desktop',            'screen=dang-ky',                 1440, 900, 1),
  @('03-tong-quan-desktop',          'screen=tong-quan',               1440, 900, 1),
  @('04-phien-hoc-desktop',          'screen=phien-hoc',               1440, 900, 1),
  @('05-lich-su-desktop',            'screen=lich-su',                 1440, 900, 1),
  @('06-cai-dat-pomodoro-desktop',   'screen=cai-dat&tab=pomodoro',    1440, 900, 1),
  @('07-cai-dat-canh-bao-desktop',   'screen=cai-dat&tab=canh-bao',    1440, 900, 1),
  @('08-cai-dat-thiet-bi-desktop',   'screen=cai-dat&tab=thiet-bi',    1440, 900, 1),
  @('09-cai-dat-tai-khoan-desktop',  'screen=cai-dat&tab=tai-khoan',   1440, 900, 1),
  @('10-tong-quan-tablet',           'screen=tong-quan',               1024, 768, 1),
  @('11-dang-nhap-mobile',           'screen=dang-nhap',                390, 844, 2),
  @('12-tong-quan-mobile',           'screen=tong-quan',                390, 844, 2),
  @('13-phien-hoc-mobile',           'screen=phien-hoc',                390, 844, 2),
  @('14-lich-su-mobile',             'screen=lich-su',                  390, 844, 2),
  @('15-cai-dat-mobile',             'screen=cai-dat&tab=canh-bao',     390, 844, 2),
  @('16-danh-gia-desktop',           'screen=tong-quan&state=danh-gia', 1440, 900, 1),
  @('17-danh-gia-mobile',            'screen=tong-quan&state=danh-gia',  390, 844, 2)
)

function Invoke-Edge([string[]]$extra) {
  $base = @('--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
            "--user-data-dir=$tmp", '--virtual-time-budget=6000')
  $out = Join-Path $env:TEMP 'study-station-wireframe-out.txt'
  $p = Start-Process -FilePath $edge -ArgumentList ($base + $extra) -Wait -PassThru `
        -RedirectStandardOutput $out -RedirectStandardError (Join-Path $env:TEMP 'study-station-wireframe-err.txt')
  Get-Content $out -Raw -Encoding UTF8
}

foreach ($s in $shots) {
  $name, $query, $w, $minH, $scale = $s
  $crop = $w -lt 500          # Edge clamps narrower windows, see wireframe.html
  $win = $w
  if ($crop) { $query = "$query&w=$w&minh=$minH"; $win = 500 }
  $url = "$page`?$query"
  # Pass 1: read the page height the wireframe writes to <html data-h="...">.
  $dom = Invoke-Edge @("--window-size=$win,400", '--dump-dom', "`"$url`"")
  $h = $minH
  if ($dom -match 'data-h="(\d+)"') { $h = [Math]::Max($minH, [int]$Matches[1]) }
  # Pass 2: full-page screenshot.
  $png = Join-Path $dir "$name.png"
  Invoke-Edge @("--window-size=$win,$h", "--force-device-scale-factor=$scale", "--screenshot=`"$png`"", "`"$url`"") | Out-Null
  if ($crop) {
    $src = [System.Drawing.Bitmap]::FromFile($png)
    $rect = New-Object System.Drawing.Rectangle 0, 0, ($w * $scale), $src.Height
    $dst = $src.Clone($rect, $src.PixelFormat)
    $src.Dispose()
    $dst.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
    $dst.Dispose()
  }
  Write-Output "$name  ${w}x$h @${scale}x"
}
