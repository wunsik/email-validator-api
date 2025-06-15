from fastapi import FastAPI
from app.schemas import EmailCheckRequest, EmailCheckResponse, PlanEnum
from app.validator import is_disposable, check_mx, get_domain_score
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/validate", response_model=EmailCheckResponse)
def validate_email(request: EmailCheckRequest):
    email = request.email
    domain = email.split("@")[1]
    plan = request.plan

    response = {
        "valid": True,
        "domain": domain,
        "is_disposable": is_disposable(domain),
        "plan": plan
    }

    if plan in [PlanEnum.pro, PlanEnum.ultra]:
        response["mx_found"] = check_mx(domain)
        response["domain_score"] = get_domain_score(domain)
    else:  # basic
        response["mx_found"] = None
        response["domain_score"] = None

    return response
