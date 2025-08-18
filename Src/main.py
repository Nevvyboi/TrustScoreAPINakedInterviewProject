from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from math import ceil

#Data which can be altered based of business modification
maxYearsInNetwork : int = 10
maxReferrals : int = 7
maxDisciplineIncidents : int = 5
maxTrainingLevel : int = 5
maxCommunityContributions : int = 10
#Weights of each factor which can be altered based of business modification
maxYearsInNetworkWeight: float = 15
maxReferralsWeight: float = 25
maxDisciplineIncidentsWeight: float = 25
maxTrainingLevelWeight: float = 20
maxCommunityContributionsWeight: float = 15

bunkerOccuptantTrustScore = FastAPI()
bunkerOccuptantTrustScore.mount("/static", StaticFiles(directory = "static"), name = "static")
templates = Jinja2Templates(directory = "templates")

@bunkerOccuptantTrustScore.get("/bunkerOccupantTrustScore", response_class = HTMLResponse)
async def home(request : Request):
    return templates.TemplateResponse("home.html", {"request": {}})

class TrustScoreRequest(BaseModel):
    yearsInNetwork: int = Field(..., ge = 0, description = "Years active in the network")
    referrals: int = Field(..., ge = 0, description = "Number of trusted referrals")
    disciplineIncidents: int = Field(..., ge = 0, description = "Number of disciplinary incidents")
    trainingLevel: int = Field(..., ge = 0, le = 5, description = "Training proficiency (0-5)")
    communityContributions: int = Field(..., ge = 0, description = "Positive community contributions") 

@bunkerOccuptantTrustScore.post("/calculateOccupantTrustScore")
async def calculateTrustScore(data: TrustScoreRequest):
    yearsInNetwork   = min(data.yearsInNetwork, maxYearsInNetwork) / maxYearsInNetwork
    referrals    = min(data.referrals, maxReferrals) / maxReferrals
    disciplineIncidents     = min(data.disciplineIncidents, maxDisciplineIncidents) / maxDisciplineIncidents
    trainingLevel   = min(data.trainingLevel, maxTrainingLevel) / maxTrainingLevel
    communityContributions = min(data.communityContributions, maxCommunityContributions) / maxCommunityContributions

    result = buildTrustScoreFeedback(yearsInNetwork, referrals, disciplineIncidents, trainingLevel, communityContributions)
    return result

def calculateTrustScore(yearsInNetwork : float, referrals : float, disciplineIncidents : float, trainingLevel : float, communityContributions : int) -> int:
    score = (
        (yearsInNetwork * maxYearsInNetworkWeight) +
        (referrals * maxReferralsWeight) +
        ((1.0 - disciplineIncidents**1.5) * maxDisciplineIncidentsWeight) +
        (trainingLevel * maxTrainingLevelWeight) +
        (communityContributions * maxCommunityContributionsWeight)
    )

    return int(max(0, min(100, round(score))))

def buildTrustScoreFeedback(
    years: float,          
    refs: float,          
    inc: float,            
    train: float,          
    contrib: float       
) -> dict:

    yearPoints   = years   * maxYearsInNetworkWeight
    referralsPoints    = refs    * maxReferralsWeight
    cleanPoints   = (1.0 - (inc ** 1.5)) * maxDisciplineIncidentsWeight
    trainPoints   = train   * maxTrainingLevelWeight
    contribPoints = contrib * maxCommunityContributionsWeight

    total = yearPoints + referralsPoints + cleanPoints + trainPoints + contribPoints
    score = int(max(0, min(100, round(total))))

    if score >= 80:
        band = "Excellent -> fast-track eligible"
    elif score >= 50:
        band = "Good -> standard checks"
    else:
        band = "Needs review –> manual checks"

    parts = [
        ("Tenure", yearPoints),
        ("Referrals", referralsPoints),
        ("Clean record", cleanPoints),
        ("Training", trainPoints),
        ("Contributions", contribPoints),
    ]
    partsSorted = sorted(parts, key=lambda x: x[1], reverse=True)
    strengths = ", ".join([name for name, _ in partsSorted[:2]])

    suggestions = []

    if inc > 0:
        recoverable = int(round(max(0, maxDisciplineIncidentsWeight - cleanPoints)))
        suggestions.append(
            f"Maintain a clean record (no new incidents) to regain -> {recoverable} points over time."
        )

    target_r = 0.8
    needReferrals = ceil(max(0, target_r * maxReferrals - refs * maxReferrals))
    if needReferrals > 0:
        suggestions.append(
            f"Secure -> {needReferrals} additional verified referral(s) to strengthen social proof."
        )

    if train < 0.8:
        gain = int(round((0.8 - train) * maxTrainingLevelWeight))
        suggestions.append(
            f"Complete training to reach level 4–5 (unlocks ~{gain} pts)."
        )

    target_c = 0.7
    needContributions = ceil(max(0, target_c * maxCommunityContributions - contrib * maxCommunityContributions))
    if needContributions > 0:
        suggestions.append(
            f"Add -> {needContributions} more community contribution(s)."
        )

    target_y = 0.6
    needYears = ceil(max(0, target_y * maxYearsInNetwork - years * maxYearsInNetwork))
    if needYears > 0:
        suggestions.append(
            f"Sustain participation for -> {needYears} more year(s) to improve stability."
        )

    explanation = (
        f"Score {score} • {band}. Strongest signals: {strengths}. "
        "Focus on the suggestions below to raise your score."
    )

    return {
        "score": score,
        "band": band,
        "explanation": explanation,
        "pointsBreakdown": {
            "yearsInNetwork": round(yearPoints, 1),
            "referrals": round(referralsPoints, 1),
            "cleanRecord": round(cleanPoints, 1),
            "training": round(trainPoints, 1),
            "communityContributions": round(contribPoints, 1),
        },
        "suggestions": suggestions or ["Keep doing what you’re doing — you’re on track!"],
    }
