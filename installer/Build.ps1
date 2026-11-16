param([string]$Output = (Join-Path $PSScriptRoot '..\dist\Peeky3-Setup.exe'))

$ErrorActionPreference = 'Stop'
$source = Split-Path -Parent $PSScriptRoot
$outputPath = [IO.Path]::GetFullPath($Output)
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$build = Join-Path ([IO.Path]::GetTempPath()) ('Peeky3Build-' + [guid]::NewGuid().ToString('N'))
if (-not (Test-Path -LiteralPath $compiler)) { throw 'The Windows .NET Framework C# compiler is required.' }

try {
    $app = Join-Path $build 'App'
    $ui = Join-Path $app 'ui'
    New-Item -ItemType Directory -Path $ui -Force | Out-Null
    foreach ($file in 'peeky.py','spatial.py','qwen_vision.py','paths.py','i18n.py','requirements.txt','LICENSE') {
        Copy-Item -LiteralPath (Join-Path $source $file) -Destination $app
    }
    foreach ($file in '__init__.py','layout.py','overlay_draw.py','scene_view.py') {
        Copy-Item -LiteralPath (Join-Path $source "ui\$file") -Destination $ui
    }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'prepare_speech.py') -Destination $app
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Install.ps1') -Destination $build
    Push-Location $source
    try {
        & python (Join-Path $PSScriptRoot 'make_icon.py')
        if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed.' }
    } finally { Pop-Location }
    $icon = Join-Path $source 'peeky.ico'
    Copy-Item -LiteralPath $icon -Destination $app

    $payload = Join-Path $build 'payload.zip'
    $uninstall = @('Uninstall.py','Uninstall-Peeky.cmd' | ForEach-Object {
        Join-Path (Join-Path $source 'portable') $_
    })
    Compress-Archive -Path (@($app,(Join-Path $build 'Install.ps1')) + $uninstall) -DestinationPath $payload
    New-Item -ItemType Directory -Path (Split-Path -Parent $outputPath) -Force | Out-Null
    & $compiler /nologo /target:winexe /optimize+ /platform:x64 "/out:$outputPath" "/win32icon:$icon" "/resource:$payload,Payload" /r:System.IO.Compression.dll /r:System.IO.Compression.FileSystem.dll (Join-Path $PSScriptRoot 'Setup.cs')
    if ($LASTEXITCODE -ne 0) { throw 'Compilation of the installer failed.' }
    Get-Item -LiteralPath $outputPath

    $fallbackPath = Join-Path $build 'Script setup'
    New-Item -ItemType Directory -Path $fallbackPath | Out-Null
    Copy-Item -LiteralPath (@($app,(Join-Path $build 'Install.ps1')) + $uninstall) -Destination $fallbackPath -Recurse
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Install-Peeky3.cmd') -Destination $fallbackPath
    $releaseZip = Join-Path (Split-Path -Parent $outputPath) 'Peeky3-Windows.zip'
    Compress-Archive -LiteralPath @($outputPath,$fallbackPath,(Join-Path $source 'README.md')) -DestinationPath $releaseZip -Force
    Get-Item -LiteralPath $releaseZip
} finally {
    $tempPath = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if ($build.StartsWith($tempPath + 'Peeky3Build-', [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $build)) {
        Remove-Item -LiteralPath $build -Recurse -Force
    }
}
