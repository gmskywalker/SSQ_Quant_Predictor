@echo off
:: 设置控制台为 UTF-8 编码，完美显示中文和 Emoji
chcp 65001 >nul

:: ==========================================
:: ⚙️ 用户配置区 (User Config)
:: 如果您的虚拟环境不叫 lottery，请修改下面这行等号后面的名字：
set ENV_NAME=lottery
:: ==========================================

echo =======================================================
echo       👑 V3.0 双色球量化预测矩阵 自动化流水线 👑
echo =======================================================
echo.

echo [1/4] 🟢 正在寻找并唤醒虚拟环境 (%ENV_NAME%)...

:: 【第一次尝试】：尝试直接唤醒
call activate %ENV_NAME% >nul 2>&1
if not errorlevel 1 goto :run_scripts

:: 【第二次尝试】：雷达网搜索常见安装路径
set "found_conda=0"
for %%p in (
    "%USERPROFILE%\anaconda3\Scripts\activate.bat"
    "%USERPROFILE%\miniconda3\Scripts\activate.bat"
    "%USERPROFILE%\AppData\Local\anaconda3\Scripts\activate.bat"
    "%USERPROFILE%\AppData\Local\miniconda3\Scripts\activate.bat"
    "C:\ProgramData\anaconda3\Scripts\activate.bat"
    "C:\ProgramData\miniconda3\Scripts\activate.bat"
    "C:\anaconda3\Scripts\activate.bat"
    "C:\miniconda3\Scripts\activate.bat"
    "D:\anaconda3\Scripts\activate.bat"
    "D:\miniconda3\Scripts\activate.bat"
) do (
    if exist %%p (
        call %%p %ENV_NAME%
        set "found_conda=1"
        goto :run_scripts
    )
)

:: 【第三次尝试】：绝望的报错与自救指南
if "%found_conda%"=="0" (
    echo.
    echo ❌ 致命错误：找不到您的 Anaconda/Miniconda 安装路径！
    echo -------------------------------------------------------
    echo 💡 解决办法 1：
    echo 请右键编辑本 bat 文件，手动填入您的 activate.bat 绝对路径（不会操作查询AI）。
    echo.
    echo 💡 解决办法 2（推荐小白使用）：
    echo 请从电脑的开始菜单手动打开【Anaconda Prompt】黑窗口
    echo 然后输入 cd 进入本项目的文件夹，依次手动敲入以下命令：
    echo 1. conda activate %ENV_NAME%
    echo 2. python 01_get_data.py
    echo 3. python 02_ml_model.py
    echo 4. python 03_generator.py
    echo -------------------------------------------------------
    pause
    exit
)

:run_scripts
echo    ✅ 唤醒成功！(%ENV_NAME% 纯净环境已就绪)

echo.
echo [2/4] 🕷️ 正在全网拉取最新开奖数据 (01_get_data.py)...
python 01_get_data.py

echo.
echo [3/4] 🤖 正在启动多维特征引擎与 AI 概率网 (02_ml_model.py)...
python 02_ml_model.py

echo.
echo [4/4] 🛡️ 正在组装 V3.0 终极神仙防守阵型 (03_generator.py)...
python 03_generator.py

echo.
echo =======================================================
echo 🎉 报告老板，全流程流水线执行完毕！请签收您的王牌底仓！
echo =======================================================
pause