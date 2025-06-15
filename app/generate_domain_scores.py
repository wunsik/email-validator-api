import json
from pathlib import Path
import dns.resolver

# 파일 경로
input_domains = Path("email_providers.txt")
tranco_csv = Path("top-1m.csv")
output_path = Path("domain_scores.json")

# Load Tranco rank → domain: rank dict
rank_map = {}
if tranco_csv.exists():
    with tranco_csv.open() as f:
        for line in f:
            rank, domain = line.strip().split(",", 1)
            rank_map[domain.lower()] = int(rank)

# DNS 기반 체크
def get_dns_score(domain):
    score = 0
    try:
        # MX record
        answers = dns.resolver.resolve(domain, "MX")
        mx_hosts = [r.exchange.to_text().lower() for r in answers]
        if any("google.com" in h or "outlook.com" in h for h in mx_hosts):
            score += 20
        else:
            score += 10
    except:
        pass

    try:
        # SPF
        txts = dns.resolver.resolve(domain, "TXT")
        if any("v=spf1" in r.to_text() for r in txts):
            score += 15
        # DKIM (간접 체크)
        if any("dkim" in r.to_text().lower() for r in txts):
            score += 10
    except:
        pass

    return score

# 도메인 리스트 불러오기
domains = [line.strip() for line in input_domains.open() if line.strip()]
domain_scores = {}

for domain in domains:
    base_score = 0

    # Tranco 순위 점수
    rank = rank_map.get(domain.lower())
    if rank:
        base_score = max(100 - rank // 10000, 10)  # Top 10K → 100점, 이후 10점씩 감소
    else:
        base_score = 50  # 기본값 (순위 외)

    # DNS 점수 추가
    dns_score = get_dns_score(domain)

    # 최종 점수
    total_score = min(base_score + dns_score, 100)
    domain_scores[domain] = total_score

# 저장
output_path.write_text(json.dumps(domain_scores, indent=2))
print(f"✅ domain_scores.json regenerated: {len(domain_scores)} domains")
