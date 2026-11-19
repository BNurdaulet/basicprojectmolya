"""
4 түрлі интеллект: IQ, EQ, SQ, PQ — білім беру веб-қосымшасы (FastAPI backend).

Іске қосу:
    1) .env.example файлын .env деп көшіріп, API кілттерін жазыңыз
    2) macOS/Linux: ./run.sh     Windows: run.bat

Қосымша (міндетті емес) айнымалылар:
    GEMINI_MODEL (әдепкі: gemini-2.5-flash)
    GROQ_MODEL   (әдепкі: llama-3.3-70b-versatile)
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import google.generativeai as genai
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("intelligence-app")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

app = FastAPI(title="IQ · EQ · SQ · PQ", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CATEGORIES = ["IQ", "EQ", "SQ", "PQ"]

CATEGORY_NAMES_KK = {
    "IQ": "IQ — интеллектуалдық қабілет (ақыл-ой, логика, талдау)",
    "EQ": "EQ — эмоционалдық интеллект (сезімдерді түсіну және басқару)",
    "SQ": "SQ — рухани интеллект (мән, құндылықтар, ішкі үйлесім)",
    "PQ": "PQ — дене интеллектісі (денсаулық, энергия, өмір салты)",
}

LIKERT_KK = {
    1: "Мүлдем келіспеймін",
    2: "Келіспеймін",
    3: "Келісемін",
    4: "Толықтай келісемін",
}

_RAW_QUESTIONS = [
    # ---------------- IQ ----------------
    ("IQ", "Күрделі мәселені шешкенде оны кішігірім бөліктерге бөліп, жүйелі түрде талдаймын."),
    ("IQ", "Жаңа ақпаратты тез меңгеріп, оны бұрыннан білетін нәрселеріммен байланыстыра аламын."),
    ("IQ", "Сандық деректерді, кестелер мен графиктерді оңай түсініп, қорытынды жасай аламын."),
    ("IQ", "Қандай да бір пікірді қабылдамас бұрын, оның дәлелдері мен логикасын тексеремін."),
    ("IQ", "Логикалық жұмбақтар мен күрделі тапсырмаларды шешу маған ұнайды."),
    ("IQ", "Әртүрлі идеялар мен құбылыстар арасындағы заңдылықтарды тез байқаймын."),
    ("IQ", "Жаңа дағдыларды өз бетімше үйренудің тиімді тәсілдерін таба аламын."),
    ("IQ", "Шешім қабылдар алдында түрлі нұсқаларды салыстырып, олардың салдарын болжаймын."),
    # ---------------- EQ ----------------
    ("EQ", "Өз эмоцияларымды дер кезінде байқап, оларды атап айта аламын."),
    ("EQ", "Ашуланған немесе қобалжыған кезде өзімді тез қолға ала аламын."),
    ("EQ", "Басқа адамның көңіл-күйін байқап, оған жанашырлық таныта аламын."),
    ("EQ", "Келіспеушілік туындағанда әңгімелесушімді құрметтеп, бейбіт шешім іздеймін."),
    ("EQ", "Сынды жеке қорлау деп емес, дамуға берілген мүмкіндік деп қабылдаймын."),
    ("EQ", "Жақындарыма өз сезімімді ашық әрі әдепті түрде жеткізе аламын."),
    ("EQ", "Адамды мұқият тыңдап, оның сөзін бөлмеуге тырысамын."),
    ("EQ", "Сәтсіздіктен кейін көңіл-күйімді қалпына келтіріп, алға қарай жылжи аламын."),
    # ---------------- SQ ----------------
    ("SQ", "Өмірімнің мәні мен мақсаты туралы жиі ойланамын."),
    ("SQ", "Іс-әрекеттерім өзім сенетін құндылықтарыма сәйкес келеді."),
    ("SQ", "Басқаларға көмектесу және қайырымдылық жасау маған терең қанағат сыйлайды."),
    ("SQ", "Табиғатпен немесе өнермен қарым-қатынас жасағанда ішкі тыныштық сезінемін."),
    ("SQ", "Қиын сәттерде сенім, дұға немесе рухани тәжірибе маған күш береді."),
    ("SQ", "Адалдық, әділдік және жауапкершілік — мен үшін өте маңызды қағидалар."),
    ("SQ", "Өзімді өзімнен үлкенірек нәрсенің — қоғамның, адамзаттың, әлемнің бөлігі ретінде сезінемін."),
    ("SQ", "Ішкі үйлесімді сақтау үшін ой елегінен өткізуге, медитацияға немесе жалғыздыққа уақыт бөлемін."),
    # ---------------- PQ ----------------
    ("PQ", "Апта сайын үнемі дене жаттығуымен немесе белсенді қозғалыспен айналысамын."),
    ("PQ", "Күн сайын жеткілікті ұйықтап, толыққанды демалуға тырысамын."),
    ("PQ", "Дұрыс әрі теңгерімді тамақтануға назар аударамын."),
    ("PQ", "Күн ішінде жеткілікті мөлшерде су ішемін."),
    ("PQ", "Денемнің белгілерін тыңдап, шаршаған кезде демалуға уақыт табамын."),
    ("PQ", "Күнделікті істерді атқаруға менің күш-қуатым жеткілікті."),
    ("PQ", "Темекі мен басқа да зиянды әдеттерден аулақ болуға тырысамын."),
    ("PQ", "Денсаулығымды уақытылы тексертіп, қажет болса дәрігерге қаралып тұрамын."),
]

QUESTIONS: List[Dict] = [
    {"id": i + 1, "category": cat, "text": text}
    for i, (cat, text) in enumerate(_RAW_QUESTIONS)
]

QUESTION_CATEGORY_BY_ID = {q["id"]: q["category"] for q in QUESTIONS}

assert len(QUESTIONS) == 32
for _c in CATEGORIES:
    assert sum(1 for q in QUESTIONS if q["category"] == _c) == 8


class AnswerItem(BaseModel):
    id: int = Field(..., ge=1, le=32)
    value: int = Field(..., ge=1, le=4)


class CalculateRequest(BaseModel):
    answers: List[AnswerItem]


def compute_scores(answers: List[AnswerItem]) -> Dict[str, int]:
    ids = [a.id for a in answers]
    if len(ids) != 32 or len(set(ids)) != 32:
        raise HTTPException(
            status_code=422,
            detail="Барлық 32 сұраққа жауап беру қажет (әр сұраққа бір жауаптан).",
        )

    totals = {c: 0 for c in CATEGORIES}
    for a in answers:
        category = QUESTION_CATEGORY_BY_ID.get(a.id)
        if category is None:
            raise HTTPException(status_code=422, detail=f"Белгісіз сұрақ нөмірі: {a.id}")
        totals[category] += a.value

    # Әр санатта 8 сұрақ: ең аз балл = 8, ең көп балл = 32.
    min_score, max_score = 8, 32
    return {
        c: round((totals[c] - min_score) / (max_score - min_score) * 100)
        for c in CATEGORIES
    }


def build_prompt(scores: Dict[str, int]) -> str:
    dominant = max(scores, key=lambda k: scores[k])
    weakest = min(scores, key=lambda k: scores[k])
    score_lines = "\n".join(f"- {CATEGORY_NAMES_KK[c]}: {scores[c]}%" for c in CATEGORIES)

    return f"""Сен — тәжірибелі психолог, коуч және жеке даму бойынша кеңесші. Төменде адамның төрт түрлі интеллект бойынша тест нәтижелері пайыздық көрсеткішпен (0–100%) берілген.

НӘТИЖЕЛЕР:
{score_lines}

Басым интеллект түрі: {dominant} ({scores[dominant]}%)
Ең төмен дамыған түрі: {weakest} ({scores[weakest]}%)

ТАПСЫРМА:
Осы нәтижелерге сүйеніп, адамға арналған жеке даму ұсыныстарын ТЕК ҚАЗАҚ ТІЛІНДЕ жаз. Жауап достық, құрметті әрі нақты болсын. Ағылшын немесе орыс сөздерін қолданба (IQ, EQ, SQ, PQ аббревиатураларынан басқа). Диагноз қойма, медициналық кеңес берме.

ЖАУАПТЫҢ ҚҰРЫЛЫМЫ (дәл осы тақырыптарды қолдан, әр тақырып "## " белгісімен басталсын):

## Жалпы шолу
2–3 сөйлеммен нәтижелердің жалпы көрінісін сипатта.

## Күшті жақтарыңыз
Ең жоғары екі интеллект түрі бойынша қысқаша талдау және оларды қалай пайдалануға болатыны.

## Дамытуға болатын салалар
Ең төмен көрсеткіштері бар интеллект түрлері бойынша жұмсақ әрі мотивациялайтын талдау.

## IQ дамыту жолдары
## EQ дамыту жолдары
## SQ дамыту жолдары
## PQ дамыту жолдары
Әр бөлімде 3 нақты, орындалатын кеңесті "- " белгісімен тізім түрінде бер.

## 4 апталық жеке даму жоспары
Әр апта үшін "- " белгісімен тізім: 1-апта, 2-апта, 3-апта, 4-апта (әрқайсысына нақты бір мақсат).

## Қорытынды
Шабыттандыратын 2–3 сөйлем.

Маңызды: markdown-ның тек "## " тақырыптарын, "- " тізімдерін және **жуан мәтінді** қолдан. Кесте, код блоктарын және эмодзи қолданба."""


SYSTEM_INSTRUCTION_KK = (
    "Сен қазақ тілінде ғана жауап беретін, қолдау көрсететін жеке даму кеңесшісісің."
)


def _call_gemini_sync(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY орнатылмаған")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=SYSTEM_INSTRUCTION_KK,
    )
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.7, "max_output_tokens": 4096},
        request_options={"timeout": 60},
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini бос жауап қайтарды")
    return text


def _call_groq_sync(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY орнатылмаған")
    client = Groq(api_key=GROQ_API_KEY, timeout=60.0)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION_KK},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )
    text = (completion.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("Groq бос жауап қайтарды")
    return text


async def generate_recommendation(prompt: str) -> Dict[str, str]:
    """Алдымен Gemini, қате болса (rate limit және т.б.) бірден Groq."""
    try:
        text = await asyncio.to_thread(_call_gemini_sync, prompt)
        return {"text": text, "provider": "gemini"}
    except Exception as gemini_error:  # noqa: BLE001
        logger.warning("Gemini қатесі, Groq-қа ауысу: %s", gemini_error)

    try:
        text = await asyncio.to_thread(_call_groq_sync, prompt)
        return {"text": text, "provider": "groq"}
    except Exception as groq_error:  # noqa: BLE001
        logger.error("Groq да қате берді: %s", groq_error)
        return {"text": "", "provider": "none"}


@app.get("/api/questions")
async def get_questions():
    return {
        "scale": [{"value": v, "label": label} for v, label in LIKERT_KK.items()],
        "questions": QUESTIONS,
    }


@app.post("/api/calculate")
async def calculate(payload: CalculateRequest):
    scores = compute_scores(payload.answers)
    dominant = max(scores, key=lambda k: scores[k])
    prompt = build_prompt(scores)
    result = await generate_recommendation(prompt)

    if result["provider"] == "none":
        recommendation = (
            "## Ескерту\n"
            "Қазіргі уақытта жасанды интеллект ұсыныстарын жасау мүмкін болмады. "
            "Нәтижелеріңіз диаграммада көрсетілген. Бірнеше минуттан кейін тестті қайта тапсырып көріңіз."
        )
    else:
        recommendation = result["text"]

    return {
        "scores": scores,
        "dominant": dominant,
        "recommendation": recommendation,
        "provider": result["provider"],
    }


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
