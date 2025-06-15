import dns.resolver
import json
from disposable_email_domains import blocklist
from pathlib import Path

# 경로 설정
domain_scores_path = Path("app/domain_scores.json")
unknown_domains_log = Path("data/unknown_domains.txt")
unknown_domains_log.parent.mkdir(parents=True, exist_ok=True)  # data/ 없으면 생성

# 점수 데이터 로딩
domain_scores = json.loads(domain_scores_path.read_text())


# ✅ 새 도메인 로그 기록 함수
def log_unknown_domain(domain: str):
    if not unknown_domains_log.exists():
        unknown_domains_log.write_text("")
    existing = set(unknown_domains_log.read_text().splitlines())
    if domain not in existing:
        with unknown_domains_log.open("a") as f:
            f.write(domain + "\n")


# ✅ 디스포저블 체크
def is_disposable(domain: str) -> bool:
    return domain in blocklist


# ✅ MX 레코드 확인
def check_mx(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return len(answers) > 0
    except Exception:
        return False


# ✅ 도메인 점수 조회 + 로그
def get_domain_score(domain: str) -> int:
    if domain in domain_scores:
        return domain_scores[domain]
    else:
        log_unknown_domain(domain)
        return 50  # 중립 기본값
