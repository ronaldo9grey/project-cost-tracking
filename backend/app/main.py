from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, projects, cost, supplier, resource, daily_report, ai_chat, daily_report_analysis, project_tracking, daily_report_evaluation, ai_daily_report, notification
from app.core.config import settings
from app.core.exceptions import CustomException

app = FastAPI(
    title="项目管理系统API",
    description="项目成本跟踪系统的后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None}
    )

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(auth, prefix="/api/v1/auth", tags=["认证"])
app.include_router(projects, prefix="/api/v1/projects", tags=["项目管理"])
app.include_router(cost, prefix="/api/v1/cost", tags=["成本分析"])
app.include_router(supplier, prefix="/api/v1/suppliers", tags=["供应商管理"])
app.include_router(resource, prefix="/api/v1/resource", tags=["资源管理"])
app.include_router(daily_report, prefix="/api/v1/daily-report", tags=["日报管理"])
app.include_router(project_tracking, prefix="/api/v1", tags=["项目跟踪"])

app.include_router(daily_report_analysis, prefix="/api/v1/daily-report", tags=["日报数据分析"])

app.include_router(daily_report_evaluation, prefix="/api/v1/daily-report-evaluation", tags=["日报评价"])

app.include_router(ai_chat, prefix="/api/v1/ai", tags=["AI对话"])
app.include_router(ai_daily_report, prefix="/api/v1", tags=["AI日报助手"])
app.include_router(notification, prefix="/api/v1", tags=["通知服务"])

# 根路径
@app.get("/")
def read_root():
    return {"message": "项目管理系统API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
