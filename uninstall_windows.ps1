# Unicorn Surprise - Windows Uninstaller
# Run with: powershell -ExecutionPolicy Bypass -File uninstall_windows.ps1

Write-Host "============================================" -ForegroundColor Magenta
Write-Host "  Unicorn Surprise - Desinstallation Windows" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host ""

$InstallDir = "$env:USERPROFILE\.unicorn-surprise"
$StartupLnk = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Unicorn Surprise.lnk"

# Stop running python processes that are running the app
Write-Host "Recherche du processus en cours..."
Get-WmiObject Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe' OR Name='wscript.exe'" `
    | Where-Object { $_.CommandLine -like "*unicorn_surprise*" -or $_.CommandLine -like "*\.unicorn-surprise\*" } `
    | ForEach-Object {
        Write-Host "  Arret du PID $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

# Remove startup shortcut
if (Test-Path $StartupLnk) {
    Write-Host "Suppression du raccourci de demarrage: $StartupLnk"
    Remove-Item $StartupLnk -Force
}

# Remove install directory
if (Test-Path $InstallDir) {
    Write-Host "Suppression du dossier: $InstallDir"
    Remove-Item $InstallDir -Recurse -Force
}

Write-Host ""
Write-Host "Desinstallation terminee." -ForegroundColor Green
Write-Host "(psutil est conserve dans pip; supprimez-le avec: pip uninstall psutil)" -ForegroundColor Gray
Write-Host ""

Read-Host "Appuyez sur Entree pour fermer"
