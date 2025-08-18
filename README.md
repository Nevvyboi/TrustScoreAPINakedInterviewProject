
---

# 📝 Project README — User Trust Score API

A tiny FastAPI service that calculates a **trust score (0–100)** from five inputs: **years in network**, **verified referrals**, **discipline incidents**, **training level**, and **community contributions**. Inputs are **normalized**, **weighted**, and combined; incidents act as a **penalty** (fewer incidents → higher score). The API also returns a **human explanation** with **improvement suggestions**.

---

## 👤 Applicant Name

**Nevin Tom**

## 🧠 Chosen Task

**Bunker Occupant Trust Score**

---

## 🛠️ How to Run

**Requirements**

* Python **3.10+**
* `pip`

**Install**

```bash
pip install fastapi uvicorn pydantic "jinja2" "python-multipart"
# or
pip install -r requirements.txt
```

**Run the API**

```bash
uvicorn main:bunkerOccuptantTrustScore --reload
# OpenAPI docs: http://127.0.0.1:8000/docs
# Optional UI page (if template present): GET /bunkerOccupantTrustScore
```

> **Windows/PowerShell tip:** In PowerShell, use `curl.exe` (not the `curl` alias) or `Invoke-RestMethod`. Examples below.

---

## 🔌 Endpoint

### `POST /calculateOccupantTrustScore`

* **All inputs are integers from `0` to `5`** (validated at the API boundary).

**Request (JSON)**

```json
{
  "yearsInNetwork": 2,
  "referrals": 3,
  "disciplineIncidents": 1,
  "trainingLevel": 4,
  "communityContributions": 2
}
```

**Response (JSON) — rich shape**

```json
{
  "score": 56,
  "band": "Good – standard checks",
  "explanation": "Score 56 • Good – standard checks. Strongest signals: Training, Referrals. Focus on the suggestions below to raise your score.",
  "pointsBreakdown": {
    "yearsInNetwork": 7.5,
    "referrals": 10.7,
    "cleanRecord": 20.3,
    "training": 16.0,
    "communityContributions": 6.0
  },
  "suggestions": [
    "Maintain a clean record (no new incidents) to regain ~5 pts over time.",
    "Secure ~2 additional verified referral(s) to strengthen social proof.",
    "Add ~3 more community contribution(s) (peer reviews, docs, support)."
  ]
}
```

**cURL (PowerShell, using real curl)**

```powershell
curl.exe -X POST "http://127.0.0.1:8000/calculateOccupantTrustScore" `
  -H "Content-Type: application/json" `
  -d "{""yearsInNetwork"":2,""referrals"":3,""disciplineIncidents"":1,""trainingLevel"":4,""communityContributions"":2}"
```

**PowerShell-native**

```powershell
$body = @{
  yearsInNetwork = 2
  referrals = 3
  disciplineIncidents = 1
  trainingLevel = 4
  communityContributions = 2
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://127.0.0.1:8000/calculateOccupantTrustScore' `
  -Method POST -ContentType 'application/json' -Body $body
```

---

## 🧮 Scoring Logic (summary)

**Normalize & cap → 0–1**

* `years = min(Y,10)/10`
* `refs = min(R,7)/7`
* `inc = min(D,5)/5`
* `train = min(T,5)/5`
* `contrib = min(C,10)/10`

**Weights (→ 100 pts total)**

* Years **15** | Referrals **25** | Clean record **25** | Training **20** | Contributions **15**

**Score**

```
score = 15*years
      + 25*refs
      + 25*(1 - inc^1.5)   # fewer incidents → higher points (non-linear penalty)
      + 20*train
      + 15*contrib
score ∈ [0, 100]
```

---

## 📈 Why These Factors & Weights (Business Rationale) —> *Summary*

We prioritize **signals that cut cost & risk** while growing a dependable community. The highest weights go to **referrals** (social proof) and **clean record** (risk control), then **training** (execution quality), and finally **tenure** and **contributions** (stability & positive externalities). This setup speeds up onboarding for trustworthy users, lowers moderation/support costs, and protects brand reputation.

* 🤝 **Referrals —> 25 pts**
  *Why:* strongest real world predictor of reliability (trusted social proof).
  *Value:* lower churn & incident rates → fewer manual reviews and faster approvals.

* 🛡️ **Clean Record (Incidents) —> 25 pts**
  *Why:* direct proxy for operational/compliance risk; full credit when incidents = 0, deduct as incidents rise.
  *Value:* fewer investigations and reputation hits → reduced risk costs and higher brand trust.

* 🎓 **Training —> 20 pts**
  *Why:* verified skills/certifications prevent avoidable errors.
  *Value:* better execution, fewer mistakes → lower support load and safer operations.

* ⏳ **Years in Network —> 15 pts**
  *Why:* loyalty and predictability correlate with retention.
  *Value:* improves lifetime value and planning without letting tenure mask active risk.

* 🌱 **Community Contributions —> 15 pts**
  *Why:* helpful behavior strengthens the ecosystem and peer support.
  *Value:* offsets staff effort, improves Net Promoter Score, and builds a healthier community.

**Design safeguards**

* 🧰 **Caps & normalization** prevent gaming and enforce diminishing returns.
* 🧮 **Transparent additive model** is auditable, explainable, and easy to tune.
* 🚦 **Operational bands** (example): **80–100** ✅ fast-track, **50–79** 🔎 standard checks, **<50** ⛔ manual review.

---

## 🖼️ GUI Screenshots

<img width="551" height="484" alt="{5B7429DE-5095-40E7-99E3-AC247CE0FB08}" src="https://github.com/user-attachments/assets/ec0417f7-5eda-4d4f-a74f-fab5d4022095" />

<img width="546" height="845" alt="{7DDB4D19-CD23-4B82-82C0-B153CDFB2160}" src="https://github.com/user-attachments/assets/ce104cbc-ec2b-4047-aa68-022ecf3b9f90" />

---

## 🧠 Assumptions & Notes

* Inputs are **0–5** integers (server-validated).
* Incidents use a **non-linear penalty** (`inc^1.5`) so repeat issues hurt more.
* Weights are business-tunable; adjust caps/weights without changing the API.

## 🧪 Quick Test Cases

| Input (Y,R,D,T,C) | Expected                            |
| ----------------- | ----------------------------------- |
| (5,5,0,5,5)       | Near **100**                        |
| (1,0,5,0,0)       | Very low (high risk, few positives) |
| (3,3,1,3,3)       | Mid-range                           |

---
