from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import pathlib
from pydantic import BaseModel
from app.utils.auth import verify_web_password
from app.utils.logging import log
import app.config.settings as settings

# 创建认证路由器
auth_router = APIRouter(prefix="/api/auth", tags=["认证"])

# 设置模板目录
BASE_DIR = pathlib.Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def get_real_client_ip(request: Request) -> str:
    """
    获取客户端的真实IP地址
    优先级：X-Forwarded-For > X-Real-IP > CF-Connecting-IP > Remote-Addr > client.host
    """
    # 尝试从 X-Forwarded-For 头获取（可能包含多个IP，取第一个）
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For 可能包含多个IP，格式：client, proxy1, proxy2
        ip = forwarded_for.split(",")[0].strip()
        if ip and ip != "unknown":
            return ip
    
    # 尝试从 X-Real-IP 头获取（Nginx等代理常用）
    real_ip = request.headers.get("X-Real-IP")
    if real_ip and real_ip != "unknown":
        return real_ip.strip()
    
    # 尝试从 CF-Connecting-IP 头获取（Cloudflare专用）
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip and cf_ip != "unknown":
        return cf_ip.strip()
    
    # 尝试从 Remote-Addr 头获取
    remote_addr = request.headers.get("Remote-Addr")
    if remote_addr and remote_addr != "unknown":
        return remote_addr.strip()
    
    # 如果都没有，返回直接连接的IP（可能是内网IP）
    return request.client.host if request.client else "unknown"

# 登录请求模型
class LoginRequest(BaseModel):
    password: str

# 登录响应模型
class LoginResponse(BaseModel):
    success: bool
    message: str

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request):
    """
    用户登录验证接口
    """
    try:
        # 获取客户端真实IP
        client_ip = get_real_client_ip(req)
        
        # 验证密码
        if not request.password:
            log("warning", f"登录失败：密码为空 - IP: {client_ip}")
            raise HTTPException(status_code=400, detail="密码不能为空")
        
        # 使用PASSWORD进行验证
        if request.password == settings.PASSWORD:
            log("info", f"用户登录成功 - IP: {client_ip}")
            # 直接返回成功状态，让前端处理跳转
            return JSONResponse(content={"success": True, "message": "登录成功", "authenticated": True})
        else:
            log("warning", f"登录失败：密码错误 - IP: {client_ip}")
            raise HTTPException(status_code=401, detail="密码错误")
            
    except HTTPException:
        raise
    except Exception as e:
        log("error", f"登录验证异常 - IP: {client_ip}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@auth_router.post("/logout")
async def logout(req: Request):
    """
    用户登出接口
    """
    try:
        client_ip = get_real_client_ip(req)
        log("info", f"用户登出 - IP: {client_ip}")
        return JSONResponse(content={"success": True, "message": "登出成功"})
    except Exception as e:
        log("error", f"登出异常 - IP: {client_ip}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@auth_router.get("/status")
async def get_auth_status():
    """
    获取认证配置状态
    """
    return JSONResponse(content={
        "password_required": bool(settings.PASSWORD),
        "web_password_set": bool(settings.WEB_PASSWORD and settings.WEB_PASSWORD != settings.PASSWORD)
    })
