@echo off
REM ============================================
REM  Limpeza Segura - Controle de Obras
REM  Remove artefatos regeneráveis sem perder
REM  codigo-fonte, banco, anexos ou configs.
REM ============================================
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
echo.
echo === Limpeza do Projeto Controle de Obras ===
echo Pasta: %ROOT%
echo.

REM --- 1. Build artifacts ---
echo [1/7] Removendo build/ ...
if exist "%ROOT%build" (
    rmdir /s /q "%ROOT%build"
    echo       OK - build removido
) else ( echo       Pulando - nao existe )

echo [2/7] Removendo dist/ ...
if exist "%ROOT%dist" (
    rmdir /s /q "%ROOT%dist"
    echo       OK - dist removido
) else ( echo       Pulando - nao existe )

echo [3/7] Removendo installer/ ...
if exist "%ROOT%installer" (
    rmdir /s /q "%ROOT%installer"
    echo       OK - installer removido
) else ( echo       Pulando - nao existe )

REM --- 2. Virtual environment ---
echo [4/7] Removendo .venv/ ...
if exist "%ROOT%.venv" (
    rmdir /s /q "%ROOT%.venv"
    echo       OK - .venv removido (reinstale com: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -e .)
) else ( echo       Pulando - nao existe )

REM --- 3. Caches ---
echo [5/7] Removendo caches (.pytest_cache, .ruff_cache, __pycache__, .mypy_cache) ...
for /d /r "%ROOT%" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)
for /d /r "%ROOT%" %%d in (*.egg-info) do (
    if exist "%%d" rmdir /s /q "%%d"
)
if exist "%ROOT%.pytest_cache" rmdir /s /q "%ROOT%.pytest_cache"
if exist "%ROOT%.ruff_cache" rmdir /s /q "%ROOT%.ruff_cache"
if exist "%ROOT%.mypy_cache" rmdir /s /q "%ROOT%.mypy_cache"
echo       OK - caches removidos

REM --- 4. Artefatos temporarios ---
echo [6/7] Removendo artifacts/ ...
if exist "%ROOT%artifacts" (
    rmdir /s /q "%ROOT%artifacts"
    echo       OK - artifacts removido
) else ( echo       Pulando - nao existe )

REM --- 5. Relatorios gerados (mantem .gitkeep) ---
echo [7/7] Limpando reports/obras/ ...
if exist "%ROOT%reports\obras" (
    del /q "%ROOT%reports\obras\*" 2>nul
    echo       OK - relatorios limpos (gitkeep mantido)
) else ( echo       Pulando - nao existe )

REM --- Resumo ---
echo.
echo === Limpeza concluida ===
echo.
echo PRESERVADOS:
echo   - src/            (codigo fonte)
echo   - data/           (banco + backups)
echo   - storage/anexos/ (documentos do usuario)
echo   - scripts/        (scripts auxiliares)
echo   - tests/          (testes)
echo   - assets/         (recursos estaticos)
echo.
echo Para reinstalar o ambiente:
echo   python -m venv .venv
echo   .venv\Scripts\activate
echo   pip install -e .
echo.
pause
