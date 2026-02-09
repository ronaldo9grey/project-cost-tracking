#!/bin/bash
# 批量修复API路径前缀

echo "=== 批量修复API路径前缀 ==="

# 修复 supplierAnalysis.ts
echo "修复 supplierAnalysis.ts..."
sed -i "s|'/v1/|'/api/v1/|g" f:/myPro/projectA1127/projectA/web_project/frontend/src/api/supplierAnalysis.ts

# 修复 dailyReport.ts (如果存在)
if [ -f "f:/myPro/projectA1127/projectA/web_project/frontend/src/api/dailyReport.ts" ]; then
    echo "修复 dailyReport.ts..."
    sed -i "s|'/v1/|'/api/v1/|g" f:/myPro/projectA1127/projectA/web_project/frontend/src/api/dailyReport.ts
fi

# 修复 resource.ts (如果存在其他路径)
echo "修复 resource.ts..."
sed -i "s|'/v1/|'/api/v1/|g" f:/myPro/projectA1127/projectA/web_project/frontend/src/api/resource.ts

echo "✅ API路径修复完成！"