@REM -*- ENCODING:UTF-8 -*- 
@ECHO OFF

ECHO "========================================="
ECHO "Mistake-Hunter V1.0.0"
ECHO " "
ECHO "If it is the first time to execute, please use the parameter "-r" to install environment dependencies"
ECHO "We recommend using .venv Virtual enviremnet to prevent version conflict"
ECHO "========================================"

REM 检查是否安装 Python
ECHO "[*]Run Envirment check..."
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO "[E]Python is not detected. Please install Python first and ensure it has been added to the PATH."
    PAUSE
    EXIT /B
)
ECHO "[*]Python has installed"

@REM 如果传入 -r 参数，先安装依赖
IF "%1"=="-r" (
    ECHO "[*]The -r parameter has been detected, starting to install dependencies"
    pip install -r requirements.txt
    IF %ERRORLEVEL% NEQ 0 (
        ECHO "[E]Dependency installation failed. Please check the requirements.txt file"
        PAUSE
        EXIT /B
    )
    
)

@REM 启动服务器
ECHO "[*]Starting Django Server"
CD ".\src"

@REM 运行数据库迁移
IF "%1"=="-r" (
    python manage.py migrate
)

@REM 启动服务器
python "manage.py" "runserver"
PAUSE