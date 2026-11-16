$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$root = Join-Path $env:LOCALAPPDATA 'Peeky3'
$app = Join-Path $root 'App'
$data = Join-Path $root 'Data'
$pythonVersion = '3.13.17'
$model = 'qwen3-vl:4b-instruct'
$python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'
$ollamaPath = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'

function Invoke-Checked([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Failed ($LASTEXITCODE): $Exe" }
}

function Install-Dependency([string]$Url, [string]$Name, [string[]]$Arguments) {
    $target = Join-Path $PSScriptRoot $Name
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $target
    $signature = Get-AuthenticodeSignature -LiteralPath $target
    if ($signature.Status -ne 'Valid') { throw "Could not verify the signature of $Name." }
    $process = Start-Process -FilePath $target -ArgumentList $Arguments -WindowStyle Hidden -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "$Name exited with code $($process.ExitCode)." }
}

function Find-Ollama {
    if (Test-Path -LiteralPath $ollamaPath) { return $ollamaPath }
    $command = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
}

function Connect-Ollama {
    try {
        return Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2
    } catch { return $null }
}

function New-PeekyShortcuts([string]$AppDirectory, [string[]]$Folders) {
    $shell = New-Object -ComObject WScript.Shell
    $icon = Join-Path $AppDirectory 'peeky.ico'
    $launcher = Join-Path $AppDirectory '.venv\Scripts\pythonw.exe'
    foreach ($folder in $Folders) {
        if (-not $folder) { throw 'Could not locate the Windows shortcut folder.' }
        New-Item -ItemType Directory -Force -Path $folder | Out-Null
        $shortcut = $shell.CreateShortcut((Join-Path $folder 'Peeky 3.lnk'))
        $shortcut.TargetPath = $launcher
        $shortcut.Arguments = '"' + (Join-Path $AppDirectory 'peeky.py') + '"'
        $shortcut.WorkingDirectory = $AppDirectory
        $shortcut.IconLocation = "$icon,0"
        $shortcut.Description = 'Peeky 3 desktop assistant'
        $shortcut.Save()
    }
}

try {
    if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {
        throw 'This release requires x64 Windows.'
    }
    New-Item -ItemType Directory -Force -Path $app,$data | Out-Null
    Write-Host '[1/4] Preparing Python and application files'
    if (-not (Test-Path -LiteralPath $python)) {
        Install-Dependency "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe" 'PythonSetup.exe' @(
            '/quiet', 'InstallAllUsers=0', 'Include_launcher=0', 'Include_test=0',
            'Include_doc=0', 'Include_tcltk=1', 'PrependPath=0',
            ('TargetDir="{0}"' -f (Split-Path -Parent $python))
        )
    }
    Copy-Item -Path (Join-Path $PSScriptRoot 'App\*') -Destination $app -Recurse -Force
    $venv = Join-Path $app '.venv'
    $appPython = Join-Path $venv 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $appPython)) {
        Invoke-Checked $python @('-m','venv',$venv)
    }
    Invoke-Checked $appPython @('-m','pip','--disable-pip-version-check','install','--only-binary=:all:','-r',(Join-Path $app 'requirements.txt'))
    Invoke-Checked $appPython @('-m','pip','--disable-pip-version-check','install','--only-binary=:all:',
        'torch==2.7.1','torchvision==0.22.1','--index-url','https://download.pytorch.org/whl/cpu')

    Write-Host '[2/4] Preparing local speech for English and Polish'
    $env:PEEKY_DATA_DIR = $data
    Invoke-Checked $appPython @((Join-Path $app 'prepare_speech.py'))

    Write-Host '[3/4] Preparing Ollama and the default vision model'
    $tags = Connect-Ollama
    if (-not $tags -or $model -notin @($tags.models | ForEach-Object { $_.name })) {
        $ollama = Find-Ollama
        if (-not $ollama) {
            Install-Dependency 'https://ollama.com/download/OllamaSetup.exe' 'OllamaSetup.exe' @(
                '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'
            )
            $ollama = Find-Ollama
        }
        if (-not $ollama) { throw 'Could not locate Ollama after installation.' }
        if (-not $tags) {
            $env:OLLAMA_HOST = '127.0.0.1:11434'
            Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
            $deadline = (Get-Date).AddSeconds(25)
            do {
                Start-Sleep -Milliseconds 500
                $tags = Connect-Ollama
            } until ($tags -or (Get-Date) -gt $deadline)
            if (-not $tags) { throw 'Ollama did not start on 127.0.0.1:11434.' }
        }
        if ($model -notin @($tags.models | ForEach-Object { $_.name })) {
            $env:OLLAMA_HOST = '127.0.0.1:11434'
            Invoke-Checked $ollama @('pull',$model)
        }
    }

    Write-Host '[4/4] Creating shortcuts'
    foreach ($file in 'Uninstall.py','Uninstall-Peeky.cmd') {
        $uninstallPath = Join-Path $PSScriptRoot $file
        if (Test-Path -LiteralPath $uninstallPath) {
            Copy-Item -LiteralPath $uninstallPath -Destination $root -Force
        }
    }
    New-PeekyShortcuts $app @([Environment]::GetFolderPath('DesktopDirectory'),[Environment]::GetFolderPath('Programs'))
    exit 0
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    Add-Type -AssemblyName System.Windows.Forms
    [Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Peeky 3 Setup', 'OK', 'Error') | Out-Null
    exit 1
}
