#!/bin/bash
# 修复API路径的脚本

echo "=== 批量修复API路径前缀 ==="

# 修复 project.ts
echo "修复 project.ts..."
sed -i 's|/v1/|/api/v1/|g' f:/myPro/projectA1127/projectA/web_project/frontend/src/api/project.ts

# 修复 Auth.ts  
echo "修复 Auth.ts..."
sed -i 's|/v1/|/api/v1/|g' f:/myPro/projectA1127/projectA/web_project/frontend/src/api/Auth.ts

# 修复 supplierAnalysis.ts
echo "修复 supplierAnalysis.ts..."
sed -i 's|/v1/|/api/v1/|g' f:/myPro/projectA1127/projectA/web_project/frontend/src/api/supplierAnalysis.ts

# 修复 dailyReport.ts
echo "修复 dailyReport.ts..."
sed -i 's|/v1/|/api/v1/|g' f:/myPro/projectA1127/projectA/web_project/frontend/src/api/dailyReport.ts

# 修复 resource.ts
echo "修复 resource.ts..."
sed -i 's|/v1/|/api/v1/|g' f:/myPro/projectA1127/projectA/web_project/frontend/src/api/resource.ts

echo "✅ 所有API路径修复完成！"