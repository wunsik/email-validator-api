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
    # 📌 모든 헤더 출력 (RapidAPI가 보내는지 확인)
    print("📥 Incoming headers:")
    for key, value in request.headers.items():
        print(f"  {key}: {value}")

    # 대소문자 둘 다 시도
    api_key = headers.get("x-rapidapi-key")

    if not api_key:
        print("❌ No API key found in headers.")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Missing API key")
    elif api_key not in VALID_API_KEYS:
        print(f"❌ Invalid API key received: {api_key}")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    else:
        print(f"✅ API key accepted: {api_key}")

    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")

    request.state.plan = VALID_API_KEYS[api_key]
    print(f"✅ Authenticated plan: {request.state.plan}")
    return await call_next(request)

# ✅ plan은 사용자 요청이 아닌, Key 기반으로 서버에서 결정
@app.post("/validate", response_model=EmailCheckResponse)
def validate_email(request_body: EmailCheckRequest, request: Request):
    email = request_body.email
    domain = email.split("@")[1]
    plan = request.state.plan


    print(f"📥 Email request received: {email}")
    print(f"🔐 Plan based on API key: {plan}")

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
