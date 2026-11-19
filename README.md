# Төрт интеллект: IQ · EQ · SQ · PQ

Төрт интеллект түрі бойынша білім беру веб-қосымшасы. Интерфейс, 32 сұрақ және AI ұсыныстары толығымен қазақ тілінде.

## Мүмкіндіктер
- 32 сұрақтан тұратын тест (IQ, EQ, SQ, PQ — әрқайсысынан 8 сұрақ, 4 баллдық шкала)
- Chart.js радар диаграммасы және басым интеллект түрін көрсету
- Жеке даму ұсыныстары: негізгі модель Gemini, қате болса автоматты түрде Groq (Llama)

## Технологиялар
- Backend: Python, FastAPI
- Frontend: HTML, Tailwind CSS, vanilla JavaScript (Fetch API), Chart.js
- AI: Gemini API (негізгі), Groq API (резерв)

## Іске қосу

```bash
git clone https://github.com/BNurdaulet/basicprojectmolya.git
cd basicprojectmolya
cp .env.example .env   # ішіне GEMINI_API_KEY және GROQ_API_KEY жазыңыз
./run.sh               # Windows: run.bat
```

`run.sh` виртуалды ортаны жасап, тәуелділіктерді орнатады және серверді қосады.
Браузерде `http://localhost:8000` ашыңыз.

## Render-ге шығару
Render → **New → Blueprint** → осы репозиторийді таңдаңыз (`render.yaml` бар).
`GEMINI_API_KEY` пен `GROQ_API_KEY` мәндерін енгізіңіз.

## Қосымша айнымалылар
| Айнымалы | Әдепкі мәні |
|---|---|
| `GEMINI_MODEL` | `gemini-3.6-flash` |
| `GROQ_MODEL` | `openai/gpt-oss-120b` |

## API
- `GET /api/questions` — 32 сұрақ және жауап шкаласы
- `POST /api/calculate` — жауаптарды қабылдап, пайыздық нәтиже мен AI ұсыныстарын қайтарады

## Ескерту
Тест білім беру мақсатында жасалған және клиникалық диагноз қоймайды.
