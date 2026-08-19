@echo off
REM =============================================
REM Build do Controle de Obras (PyInstaller)
REM Saida: dist\ControleDeObras\ControleDeObras.exe
REM
REM Build em pasta temporaria para evitar travamento
REM de arquivos pelo OneDrive, depois copia para dist\.
REM =============================================
cd /d "%~dp0"

set "BUILD_DIR=%TEMP%\controle_obras_build"
set "DIST_DIR=%TEMP%\controle_obras_dist"

echo [1/3] Verificando dependencias de build...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
)

echo [2/3] Empacotando aplicacao...
python -m PyInstaller --noconfirm --clean --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%" ControleDeObras.spec
if errorlevel 1 (
    echo [ERRO] Falha no empacotamento.
    exit /b 1
)

echo [3/3] Copiando para dist\ControleDeObras...
if exist "dist\ControleDeObras" rmdir /s /q "dist\ControleDeObras"
if not exist "dist\ControleDeObras" mkdir "dist\ControleDeObras"
xcopy /s /e /y /q "%DIST_DIR%\ControleDeObras\*" "dist\ControleDeObras\" >nul

echo.
echo Build concluido!
echo Executavel gerado: dist\ControleDeObras\ControleDeObras.exe
echo.
echo Para criar atalho:
echo   - Botao direito no .exe ^> Enviar para ^> Desktop
echo   - Ou copie a pasta dist\ControleDeObras inteira
exit /b 0