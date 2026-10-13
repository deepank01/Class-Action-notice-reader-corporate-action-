"""Controls on the AI output. Anything returned here needs a person to review it."""
import re
from datetime import date

from fields import FIELDS


def check(result, text, today=None):
    today = today or date.today()
    f, ev = result["fields"], result.get("evidence", {})
    issues = []
    norm = lambda s: re.sub(r"\s+", " ", str(s or "")).lower()
    t = norm(text)

    # 1. Missing fields, and quotes that do not appear in the notice (possible AI error)
    for k in FIELDS:
        if f.get(k) is None:
            issues.append((k, "MISSING", "Not found in notice - check by hand"))
            continue
        q = ev.get(k)
        if not q or norm(q) not in t:
            issues.append((k, "NO_EVIDENCE", "AI quote not found in notice - possible error"))

    # 2. Date checks
    def d(k):
        try:
            return date.fromisoformat(f[k]) if f.get(k) else None
        except ValueError:
            issues.append((k, "BAD_DATE", f[k]))
            return None

    s, e, c = d("class_period_start"), d("class_period_end"), d("claim_filing_deadline")
    if s and e and s > e:
        issues.append(("class_period", "BAD_RANGE", "Start date is after end date"))
    if c:
        days = (c - today).days
        if days < 0:
            issues.append(("claim_filing_deadline", "PASSED", "Deadline has passed"))
        elif days <= 30:
            issues.append(("claim_filing_deadline", "URGENT", f"{days} days left"))

    # 3. Format check
    if f.get("cusip") and not re.fullmatch(r"[0-9A-Z]{9}", str(f["cusip"])):
        issues.append(("cusip", "BAD_FORMAT", f["cusip"]))
    return issues
