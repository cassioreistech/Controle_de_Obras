@echo off
REM =============================================
REM Build do Controle de Obras (PyInstaller)
REM Saida: dist\ControleDeObras\ControleDeObras.exe
REM =============================================
cd /d "%~dp0"

echo [1/3] Verificando dependencias de build...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
)

echo [2/3] Empacotando aplicacao...
python -m PyInstaller --noconfirm --clean ControleDeObras.spec
if errorlevel 1 (
    echo [ERRO] Falha no empacotamento.
    exit /b 1
)

echo [3/3] Build concluido!
echo.
echo Executavel gerado: dist\ControleDeObras\ControleDeObras.exe
echo.
echo Para criar atalho:
echo   - Botao direito no .exe ^> Enviar para ^> Desktop
echo   - Ou copie a pasta dist\ControleDeObras inteira
exit /b 0