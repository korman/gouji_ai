@echo off
echo 正在清理 models 和 logs 目录...

rem 检查 models 目录是否存在
if exist "models\" (
    echo 清理 models 目录中的文件...
    del /f /q /s "models\*.pt"
    echo models 目录清理完成！
) else (
    echo models 目录不存在，跳过清理。
)

rem 检查 logs 目录是否存在
if exist "logs\" (
    echo 清理 logs 目录中的文件...
    del /f /q /s "logs\*.log"
	del /f /q /s "logs\*.db"
    echo logs 目录清理完成！
) else (
    echo logs 目录不存在，跳过清理。
)

echo 清理完成！
pause