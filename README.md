# Class Action Notice Reader

A small tool that reads class-action settlement notices with AI and pulls out the key terms an operations team needs: case name, CUSIP, class period, claim and opt-out deadlines, settlement amount and claims administrator.

**AI reads. Code checks. A person decides.**

## Why

Missing a class-action filing deadline leaves client money on the table. Notices are long and inconsistent, so reading them by hand is slow and error-prone.

## How it works

1. **Read** a PDF or text notice (`extractor.py`).
2. **Extract** the fields with an AI model. The model must also return the exact quote it used for every value.
3. **Check** the output (`checks.py`):
   - Missing fields are flagged for manual review.
   - Every quote must really appear in the notice. A value with no matching text is flagged as a possible AI error.
   - Dates must be valid, and the class period start must be before the end.
   - Claim deadlines within 30 days are flagged as urgent.
   - The CUSIP must have a valid format.
4. **Review** the results and flags on a simple screen (`app.py`, Streamlit).

## Results

Tested on 1 real settlement notices: 10 of 10 fields correct (100%). Fields missing from the notice (for example, no CUSIP in a Canadian case) were correctly returned as “not found” and flagged for human review.

## Run it

See `START_HERE.txt`. Works free: manual mode (paste into any AI chat) or the free Gemini API. `test_checks.py` runs the controls without any key, using a fictional sample notice with a planted error.

## What I would add next

- Non-US opt-in class actions and bankruptcy plan notices
- Matching the class period against trade history to find eligible accounts
- A deadline tracker with email alerts

*Personal learning project. The sample notice is fictional. Real notices used for testing are public documents.*
