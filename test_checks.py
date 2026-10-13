"""Tests the controls WITHOUT calling the AI (no API key needed).
Run:  python test_checks.py
The fake AI result below has one planted error (a wrong class-period end date)
so you can see the evidence check catch it."""
from datetime import date

from checks import check

text = open("notices/SAMPLE_mock_notice.txt", encoding="utf-8").read()

fake_ai_result = {
    "fields": {
        "case_name": "In re Northwind Energy Corp. Securities Litigation",
        "court": "United States District Court, Southern District of New York",
        "security_name": "Northwind Energy Corp. common stock",
        "cusip": "66977W109",
        "class_period_start": "2022-03-01",
        "class_period_end": "2023-09-15",          # PLANTED ERROR: notice says August 15
        "claim_filing_deadline": "2026-11-20",
        "opt_out_deadline": "2026-10-30",
        "settlement_amount_usd": 38500000,
        "claims_administrator": "Example Claims Services LLC",
    },
    "evidence": {
        "case_name": "In re Northwind Energy Corp. Securities Litigation",
        "court": "SOUTHERN DISTRICT OF NEW YORK",
        "security_name": "common stock of Northwind Energy Corp.",
        "cusip": "CUSIP 66977W109",
        "class_period_start": "between March 1, 2022",
        "class_period_end": "September 15, 2023",   # this quote is NOT in the notice
        "claim_filing_deadline": "no later than November 20, 2026",
        "opt_out_deadline": "received no later than October 30, 2026",
        "settlement_amount_usd": "cash payment of $38,500,000",
        "claims_administrator": "Example Claims Services LLC",
    },
}

issues = check(fake_ai_result, text, today=date(2026, 10, 13))
print("Issues for human review:")
for field, issue, detail in issues:
    print(f"  {field:24} {issue:12} {detail}")
assert any(i[0] == "class_period_end" and i[1] == "NO_EVIDENCE" for i in issues), "planted error not caught"
print("\nTest passed: the planted error was caught.")
