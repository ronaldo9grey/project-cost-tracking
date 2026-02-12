# sync_to_tencent.ps1 - Windows PowerShell 脚本：同步代码到腾讯云并部署

param(
    [string]$ServerIP = "175.178.40.53",
    [string]$Username = "ubuntu",
    [switch]$AutoDeploy = $false
)

# 项目配置
$ProjectPath = "/var/www/web_project"
$BackupPath = "/var/www/web_project_backups"

Write-Host "🚀 开始同步到腾讯云并部署..." -ForegroundColor Green
Write-Host ""
Write-Host "服务器: $Username@$ServerIP" -ForegroundColor Cyan
Write-Host "项目路径: $ProjectPath" -ForegroundColor Cyan
Write-Host ""

# ========== 第一步：本地代码提交到GitHub ==========
Write-Host "========== 第一步：本地代码提交到GitHub ==========" -ForegroundColor Green
Write-Host ""

# 检查Git状态
Write-Host "检查Git状态..." -ForegroundColor Yellow
git status
Write-Host ""

# 检查是否有未提交的更改
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "发现未提交的更改，正在提交..." -ForegroundColor Yellow
    git add .
    $commitMessage = Read-Host "请输入提交信息 (默认为自动生成的日期时间): "
    if ([string]::IsNullOrWhiteSpace($commitMessage)) {
        $commitMessage = "chore: 同步最新代码到腾讯云 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }
    git commit -m $commitMessage
    Write-Host "✅ 本地已提交" -ForegroundColor Green
} else {
    Write-Host "没有未提交的更改" -ForegroundColor Green
}

# 推送到GitHub
Write-Host ""
Write-Host "推送到GitHub..." -ForegroundColor Yellow
git push origin main
Write-Host "✅ 已推送到GitHub" -ForegroundColor Green

# ========== 第二步：腾讯云服务器备份 ==========
Write-Host ""
Write-Host "========== 第二步：腾讯云服务器备份 ==========" -ForegroundColor Green
Write-Host ""

# 检查SSH连接
Write-Host "检查SSH连接..." -ForegroundColor Yellow
$sshTest = ssh -o ConnectTimeout=10 -o BatchMode=yes $Username@$ServerIP "echo 'SSH连接成功'" 2>&1
if ($sshTest -like "*SSH连接成功*") {
    Write-Host "✅ SSH连接正常" -ForegroundColor Green
} else {
    Write-Host "❌ SSH连接失败，请检查:" -ForegroundColor Red
    Write-Host "   - 服务器IP是否正确: $ServerIP" -ForegroundColor Yellow
    Write-Host "   - 用户名是否正确: $Username" -ForegroundColor Yellow
    Write-Host "   - SSH密钥是否配置" -ForegroundColor Yellow
    Write-Host "   - 安全组是否开放22端口" -ForegroundColor Yellow
    exit 1
}

# 执行备份
Write-Host ""
Write-Host "正在创建备份..." -ForegroundColor Yellow
$backupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFolder = "$BackupPath/backup_$backupTimestamp"

$backupCommands = @"
# 创建备份目录
mkdir -p $BackupPath

# 备份整个项目目录
cp -r $ProjectPath $backupFolder

# 记录备份信息
echo "Backup created at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" > $backupFolder/backup_info.txt
echo "Git commit: $(git -C $ProjectPath log --oneline -1)" >> $backupFolder/backup_info.txt

# 显示备份结果
echo "✅ 备份创建成功!"
echo "备份位置: $backupFolder"
ls -la $backupFolder | head -20
"@

$backupResult = ssh $Username@$ServerIP $backupCommands 2>&1
Write-Host $backupResult -ForegroundColor White

# 询问是否继续
Write-Host ""
$continueDeploy = Read-Host "备份完成，是否继续部署? (y/N): "
if ($continueDeploy -ne "y" -and $continueDeploy -ne "Y") {
    Write-Host "已取消部署" -ForegroundColor Yellow
    exit 0
}

# ========== 第三步：服务器拉取最新代码 ==========
Write-Host ""
Write-Host "========== 第三步：服务器拉取最新代码 ==========" -ForegroundColor Green
Write-Host ""

Write-Host "正在拉取最新代码..." -ForegroundColor Yellow
$pullResult = ssh $Username@$ServerIP "cd $ProjectPath && git pull origin main" 2>&1
Write-Host $pullResult -ForegroundColor White

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 代码更新成功" -ForegroundColor Green
} else {
    Write-Host "⚠️ 代码更新可能有问题，请检查输出" -ForegroundColor Yellow
}

# ========== 第四步：重启服务 ==========
Write-Host ""
Write-Host "========== 第四步：重启服务 ==========" -ForegroundColor Green
Write-Host ""

Write-Host "重启Docker服务..." -ForegroundColor Yellow
$restartResult = ssh $Username@$ServerIP "cd $ProjectPath && docker-compose restart" 2>&1
Write-Host $restartResult -ForegroundColor White

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 服务重启成功" -ForegroundColor Green
} else {
    Write-Host "⚠️ 服务重启可能有问题" -ForegroundColor Yellow
}

# ========== 第五步：验证部署结果 ==========
Write-Host ""
Write-Host "========== 第五步：验证部署结果 ==========" -ForegroundColor Green
Write-Host ""

Write-Host "检查服务状态..." -ForegroundColor Yellow
$serviceStatus = ssh $Username@$ServerIP "cd $ProjectPath && docker-compose ps" 2>&1
Write-Host $serviceStatus -ForegroundColor White

Write-Host ""
Write-Host "检查Git版本..." -ForegroundColor Yellow
$gitVersion = ssh $Username@$ServerIP "cd $ProjectPath && git log --oneline -3" 2>&1
Write-Host $gitVersion -ForegroundColor White

# ========== 完成 ==========
Write-Host ""
Write-Host "🎉 腾讯云同步和部署完成!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 部署摘要:" -ForegroundColor Yellow
Write-Host "   ✅ 代码已推送到GitHub" -ForegroundColor Green
Write-Host "   ✅ 服务器已创建备份: $backupFolder" -ForegroundColor Green
Write-Host "   ✅ 最新代码已拉取到服务器" -ForegroundColor Green
Write-Host "   ✅ Docker服务已重启" -ForegroundColor Green
Write-Host ""
Write-Host "� 访问地址:" -ForegroundColor Yellow
Write-Host "   前端: http://$ServerIP" -ForegroundColor White
Write-Host "   API:  http://$ServerIP:8000" -ForegroundColor White
Write-Host "   文档: http://$ServerIP:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔧 备份位置: $backupFolder" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️ 如需恢复备份，执行:" -ForegroundColor Yellow
Write-Host "   ssh $Username@$ServerIP" -ForegroundColor White
Write-Host "   cd $ProjectPath" -ForegroundColor White
Write-Host "   rm -rf *" -ForegroundColor White
Write-Host "   cp -r $backupFolder/* . " -ForegroundColor White
Write-Host "   docker-compose restart" -ForegroundColor White
