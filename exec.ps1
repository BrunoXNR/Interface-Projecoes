# Script para empacotar e distribuir o projeto em um arquivo executável (.exe) usando PyInstaller

# Verifica se a biblioteca PyInstaller está instalada
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller não encontrado. Instalando..."
    pip install pyinstaller
}

# Executa o comando PyInstaller no PowerShell
Write-Host "Empacotando o arquivo"
pyinstaller --noconfirm --onefile --windowed --icon=utils/logofh.ico --add-data "utils;utils" --hidden-import=reportlab --hidden-import=matplotlib.backends.backend_agg interface.py

# Verifica se o comando foi executado com sucesso
if ($?) {
    Write-Host "Empacotamento concluído com sucesso! O arquivo .exe está na pasta 'dist/'."
} else {
    Write-Host "Erro durante o empacotamento. Verifique os logs para mais detalhes."
}
