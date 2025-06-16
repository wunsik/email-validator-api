from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
from app.schemas import EmailCheckRequest, EmailCheckResponse, PlanEnum
from app.validator import is_disposable, check_mx, get_domain_score

app = FastAPI(
    title="Email Validator API",
    description="This API allows you to validate emails by checking if they are disposable, if they have valid MX records, and assigning a trust score to the domain.",
    version="1.0.0",
    contact={
        "name": "Aiden Woo",
        "url": "https://nowebsiteyet.com",
        "email": "wunsik@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ RapidAPI Key → Plan 매핑
VALID_API_KEYS = {
    "e6b852e101mshf896879a95b2f68p19637djsnbabea23c25c8": PlanEnum.basic,
    # 여기에 다른 유저 Key 추가 시 확장 가능
    # 예: "pro_key_abc": PlanEnum.pro,
    # 예: "ultra_key_xyz": PlanEnum.ultra,
}

# ✅ 미들웨어로 API Key 인증 + plan 저장
@app.middleware("http")
async def authenticate_api_key(request: Request, call_next):
    api_key = request.headers.get("X-RapidAPI-Key")
    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")

    # plan 정보를 상태에 저장
    request.state.plan = VALID_API_KEYS[api_key]
    return await call_next(request)

# ✅ plan은 사용자 요청이 아닌, Key 기반으로 서버에서 결정
@app.post("/validate", response_model=EmailCheckResponse)
def validate_email(request_body: EmailCheckRequest, request: Request):
    email = request_body.email
    domain = email.split("@")[1]
    plan = request.state.plan

    response = {
        "valid": True,
        "domain": domain,
        "is_disposable": is_disposable(domain),
        "plan": plan,
        "mx_found": None,
        "domain_score": None,
    }

    if plan in [PlanEnum.pro, PlanEnum.ultra]:
        response["mx_found"] = check_mx(domain)
    if plan == PlanEnum.ultra:
        response["domain_score"] = get_domain_score(domain)

    return response
