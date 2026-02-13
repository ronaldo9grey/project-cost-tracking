@echo off
echo ================================
echo 项目成本跟踪系统 - GitHub推送脚本
echo ================================
echo.

echo 正在检查Git配置...
git status

echo.
echo 如果您在GitHub上创建了仓库，请运行以下命令推送代码：
echo.
echo git push -u origin main
echo.
echo 如果需要GitHub认证，建议使用：
echo 1. Personal Access Token（推荐）
echo 2. 或者使用GitHub CLI
echo.
echo 创建GitHub仓库的链接：
echo https://github.com/new
echo.
echo 仓库信息：
echo 名称: project-cost-tracking
echo 描述: 项目成本跟踪系统 - 支持项目管理、成本分析、资源管理和供应商管理
echo 类型: Private（私有）
echo.
pause