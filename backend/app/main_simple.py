from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import hashlib
from datetime import datetime, timedelta
from jose import jwt

# 简化的配置
SECRET_KEY = "project-management-system-secret-key-2024-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# 用户数据（临时使用硬编码）
USERS = {
    "EMP001": {
        "id": 5,
        "username": "EMP001", 
        "name": "陆宏东",
        "password": "e10adc3949ba59abbe56e057f20f883e"  # MD5: 123456
    }
}

app = FastAPI(title="简化的项目管理系统API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证MD5密码"""
    return hashlib.md5(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
def read_root():
    return {"message": "简化版项目管理系统API", "version": "1.0.0"}

@app.post("/api/v1/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录，获取访问令牌"""
    username = form_data.username
    password = form_data.password
    
    print(f"收到登录请求: username={username}")
    
    # 查找用户
    user = USERS.get(username)
    if not user:
        print(f"用户不存在: {username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not verify_password(password, user["password"]):
        print(f"密码错误: {username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    print(f"用户认证成功: {user['username']}")
    
    # 生成token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    token_data = {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    print(f"生成token成功: {access_token[:20]}...")
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": token_data
    }

@app.get("/api/v1/auth/users/me")
def get_current_user_info(username: str = "EMP001"):
    """获取当前用户信息"""
    user = USERS.get(username)
    if user:
        user_info = {
            "id": user["id"],
            "username": user["username"],
            "role_id": 1
        }
        return {
            "code": 200,
            "message": "获取用户信息成功",
            "data": user_info
        }
    else:
        raise HTTPException(status_code=404, detail="用户不存在")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)