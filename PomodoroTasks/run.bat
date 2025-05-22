@echo off
echo.
echo ============================================================
echo               LUMI - ASSISTENTE DE PRODUTIVIDADE
echo ============================================================
echo.

rem Verifica se o Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Python nao foi encontrado!
    echo.
    echo Para usar este programa, voce precisa:
    echo 1. Instalar o Python 3.7 ou superior de www.python.org/downloads
    echo 2. Marcar a opcao "Add Python to PATH" durante a instalacao
    echo.
    echo Apos instalar o Python, execute este arquivo novamente.
    echo.
    pause
    exit /b 1
)

rem Verifica se as dependências estão instaladas
echo Verificando instalacao...
python -c "import requests" >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Instalando o modulo 'requests'...
    python -m pip install requests
    if %errorlevel% neq 0 (
        echo.
        echo ERRO: Falha ao instalar o modulo 'requests'.
        echo Execute manualmente: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Inicializando PomodoroTasks Assistant...
echo.
python main.py %*
if errorlevel 1 (
    echo.
    echo Erro ao executar o PomodoroTasks.
    echo.
    echo Para diagnosticar o problema, execute:
    echo python check_setup.py
    echo.
)
pause
