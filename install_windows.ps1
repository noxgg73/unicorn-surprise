# Unicorn Surprise - Windows Installer
# Run with: powershell -ExecutionPolicy Bypass -File install_windows.ps1

Write-Host "============================================" -ForegroundColor Magenta
Write-Host "   Unicorn Surprise - Installation Windows" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host ""

$InstallDir = "$env:USERPROFILE\.unicorn-surprise"
$StartupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"

# Create install directory
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Check Python
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3") {
            $pythonCmd = $cmd
            break
        }
    } catch {}
}

if (!$pythonCmd) {
    Write-Host "Python 3 est requis !" -ForegroundColor Red
    Write-Host "Telechargez-le sur: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Cochez 'Add Python to PATH' pendant l'installation." -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

Write-Host "Python trouve: $pythonCmd" -ForegroundColor Green

# Install psutil
Write-Host "Installation des dependances..."
& $pythonCmd -m pip install psutil --quiet 2>$null

# Copy the app
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceFile = Join-Path $ScriptDir "app\unicorn_surprise.py"

if (Test-Path $SourceFile) {
    Copy-Item $SourceFile "$InstallDir\unicorn_surprise.py" -Force
} else {
    Write-Host "Erreur: unicorn_surprise.py introuvable." -ForegroundColor Red
    Write-Host "Placez ce script dans le dossier unicorn-surprise." -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

# Create startup shortcut using VBScript (hidden window)
$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "$pythonCmd ""$InstallDir\unicorn_surprise.py""", 0, False
"@

$vbsPath = "$InstallDir\launch.vbs"
Set-Content -Path $vbsPath -Value $vbsContent -Encoding ASCII

# Create shortcut in Startup folder
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("$StartupDir\Unicorn Surprise.lnk")
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$vbsPath`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Unicorn Surprise"
$Shortcut.Save()

Write-Host ""
Write-Host "Installation terminee !" -ForegroundColor Green
Write-Host "Unicorn Surprise se lancera a chaque demarrage." -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour desinstaller:" -ForegroundColor Yellow
Write-Host "  1. Supprimez: $StartupDir\Unicorn Surprise.lnk"
Write-Host "  2. Supprimez: $InstallDir"
Write-Host ""

$response = Read-Host "Lancer maintenant ? (o/n)"
if ($response -eq "o" -or $response -eq "O") {
    Start-Process $pythonCmd -ArgumentList "$InstallDir\unicorn_surprise.py" -WindowStyle Hidden
    Write-Host "Lance !" -ForegroundColor Green
}

Read-Host "Appuyez sur Entree pour fermer"
