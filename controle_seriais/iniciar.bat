@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   GERENCIADOR DE SERIAIS - CONTROLE DE OBRAS
echo ========================================
echo.

if "%1"=="" goto menu

python "%~dp0controle_seriais.py" %*
pause
goto :eof

:menu
echo COMANDOS DISPONIVEIS:
echo.
echo   1. Listar seriais
echo   2. Buscar serial
echo   3. Registrar novo serial
echo   4. Atualizar status
echo   5. Excluir serial
echo   6. Estatisticas
echo   7. Gerar nova chave
echo   0. Sair
echo.
set /p opcao="Escolha uma opcao: "

if "%opcao%"=="1" (
    python "%~dp0controle_seriais.py" listar
) else if "%opcao%"=="2" (
    set /p chave="Digite a chave: "
    python "%~dp0controle_seriais.py" buscar !chave!
) else if "%opcao%"=="3" (
    set /p chave="Chave: "
    set /p cliente="Cliente: "
    set /p empresa="Empresa: "
    set /p contato="Contato: "
    set /p maquina="Maquina ID: "
    set /p validade="Validade (YYYY-MM-DD): "
    python "%~dp0controle_seriais.py" registrar --chave !chave! --cliente "!cliente!" --empresa "!empresa!" --contato "!contato!" --maquina !maquina! --validade !validade!
) else if "%opcao%"=="4" (
    set /p chave="Chave: "
    set /p status="Novo status (Ativo/Inativo/Expirado): "
    python "%~dp0controle_seriais.py" status !chave! !status!
) else if "%opcao%"=="5" (
    set /p id="ID do serial: "
    python "%~dp0controle_seriais.py" excluir !id!
) else if "%opcao%"=="6" (
    python "%~dp0controle_seriais.py" estatisticas
) else if "%opcao%"=="7" (
    set /p validade="Validade (YYYY-MM-DD): "
    set /p maquina="Maquina ID (deixe vazio para usar esta maquina): "
    python "%~dp0controle_seriais.py" gerar !validade! --maquina !maquina!
) else if "%opcao%"=="0" (
    exit /b 0
) else (
    echo Opcao invalida!
)

echo.
pause
cls
goto menu
