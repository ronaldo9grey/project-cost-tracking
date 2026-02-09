import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.models.resource import Personnel
from app.schemas.auth import Token, TokenData, UserLogin, ChangePassword
from app.schemas.response import SuccessResponse

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证MD5密码"""
    return hashlib.md5(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """生成MD5密码哈希"""
    return hashlib.md5(password.encode()).hexdigest()


def get_user(db: Session, username: str) -> Optional[Personnel]:
    """根据用户名获取用户，支持employee_id或name"""
    # 首先尝试用employee_id查找
    user = db.query(Personnel).filter(
        Personnel.employee_id == username, 
        Personnel.is_deleted == False
    ).first()
    
    # 如果没找到，尝试用name查找
    if not user:
        user = db.query(Personnel).filter(
            Personnel.name == username, 
            Personnel.is_deleted == False
        ).first()
    
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[Personnel]:
    """验证用户并返回用户对象"""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Personnel:
    """获取当前用户"""
    print(f"收到token: {token[:20]}...")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        print(f"从token中解析出username: {username}")
        if username is None:
            print("token中没有username字段")
            raise UnauthorizedException(message="无法验证凭据")
        token_data = TokenData(username=username)
    except JWTError as e:
        print(f"JWT解析失败: {e}")
        raise UnauthorizedException(message="无法验证凭据")
    
    print(f"尝试查找用户: {token_data.username}")
    user = get_user(db, username=token_data.username)
    if user is None:
        print(f"用户不存在: {token_data.username}")
        raise UnauthorizedException(message="用户不存在")
    
    print(f"成功找到用户: {user.employee_id} ({user.name})")
    return user


@router.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录，获取访问令牌"""
    username = form_data.username
    password = form_data.password
    
    print(f"收到登录请求: username={username}")
    
    # 验证用户和密码
    user = authenticate_user(db, username, password)
    if not user:
        print(f"用户认证失败: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"用户认证成功: {user.employee_id} ({user.name})")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.employee_id}, 
        expires_delta=access_token_expires
    )
    
    token_data = {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    print(f"生成token成功")
    return SuccessResponse(data=token_data, message="登录成功")


@router.post("/refresh")
def refresh_access_token(current_user: Personnel = Depends(get_current_user)):
    """刷新访问令牌"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.employee_id},
        expires_delta=access_token_expires
    )
    
    token_data = {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    return SuccessResponse(data=token_data, message="令牌刷新成功")


@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if not verify_password(password_data.old_password, current_user.password):
        raise BadRequestException(message="旧密码错误")
    
    if password_data.new_password != password_data.confirm_password:
        raise BadRequestException(message="新密码和确认密码不一致")
    
    current_user.password = get_password_hash(password_data.new_password)
    db.commit()
    db.refresh(current_user)
    
    return SuccessResponse(data=None, message="密码修改成功")


@router.get("/users/me")
def get_current_user_info(current_user: Personnel = Depends(get_current_user)):
    """获取当前用户信息"""
    user_info = {
        "id": current_user.id,
        "username": current_user.employee_id,
        "employee_id": current_user.employee_id,
        "name": current_user.name,
        "department": current_user.department,
        "position": current_user.position,
        "phone": current_user.phone,
        "email": current_user.email,
        "role_id": current_user.role_id
    }
    return SuccessResponse(data=user_info, message="获取用户信息成功")
