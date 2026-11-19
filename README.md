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
git clone <репозиторий-сілтемесі>
cd <папка-аты>
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows:     .venv\Scripts\activate
pip install -r requirements.txt
```

API кілттерін орнатыңыз.

Linux/macOS:
```bash
export GEMINI_API_KEY="..."
export GROQ_API_KEY="..."
```

Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="..."
$env:GROQ_API_KEY="..."
```

Серверді іске қосыңыз:
```bash
python -m uvicorn main:app --reload
```
Содан кейін браузерде `http://localhost:8000` ашыңыз.

## Қосымша айнымалылар
| Айнымалы | Әдепкі мәні |
|---|---|
| `GEMINI_MODEL` | `gemini-2.5-flash` |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |

## API
- `GET /api/questions` — 32 сұрақ және жауап шкаласы
- `POST /api/calculate` — жауаптарды қабылдап, пайыздық нәтиже мен AI ұсыныстарын қайтарады

## Ескерту
Тест білім беру мақсатында жасалған және клиникалық диагноз қоймайды.
