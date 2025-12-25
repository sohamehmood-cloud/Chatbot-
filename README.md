# MindBuddy — AI-Powered Mental Wellbeing Chatbot

A responsive, safety-first chatbot that answers basic questions about mental health and emotional wellbeing. Built with Flask and includes crisis detection with direct resources.

## ⚠️ Important Disclaimer

**MindBuddy is not a substitute for professional mental health care.** It provides supportive information and self-care tips only. If you are in crisis or experiencing suicidal thoughts, please contact your local emergency services or a crisis hotline immediately:

- **US**: Call or text **988** (Suicide & Crisis Lifeline)
- **International**: [OpenCounseling — Crisis Hotlines](https://www.opencounseling.com/suicide-hotlines)
- **Always seek professional help** for diagnosis, treatment, or emergencies

## Features

✅ **Crisis Detection** — Automatically identifies mental health crisis keywords and provides immediate emergency resources  
✅ **OpenAI Integration** — Uses GPT-3.5-turbo when API key is configured; falls back to safe, rule-based responses otherwise  
✅ **Responsive UI** — Modern, mobile-friendly chat interface with typing indicators and message history  
✅ **Safety-First** — Prominent disclaimer and links to crisis hotlines and professional resources  
✅ **Accessibility** — ARIA labels, semantic HTML, and keyboard navigation (Enter to send)  

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Navigate to the project directory:**
   ```powershell
   cd "e:\Soha_CS_1st_Sem\this"
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   (On macOS/Linux: `source venv/bin/activate`)

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **(Optional) Add OpenAI API key for AI responses:**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key: `OPENAI_API_KEY=sk-...`
   - Without an API key, the chatbot uses safe fallback responses

### Running the Chatbot

```powershell
python app.py
```

Then open your browser to **http://127.0.0.1:5000**

## Project Structure

```
├── app.py                 # Flask backend with crisis detection & /chat endpoint
├── index.html             # Chat UI with disclaimer and resource links
├── style.css              # Responsive, modern styling
├── script.js              # Frontend chat logic with typing indicators
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment file
└── README.md              # This file
```

## How It Works

1. **User sends message** → Frontend sends POST request to `/chat` endpoint
2. **Backend processes**:
   - Checks for crisis keywords (suicide, self-harm, etc.)
   - If crisis detected → returns emergency resources immediately
   - Otherwise → calls OpenAI (if configured) OR returns safe fallback
3. **Frontend displays** response with typing indicator, auto-scroll, and proper formatting

## Safety Features

- **Crisis Keyword Detection** — Monitors 8 common crisis phrases and immediately provides emergency resources
- **No Medical Diagnosis** — All responses avoid diagnosing conditions or recommending medical treatment
- **Professional Referrals** — Encourages seeking help from qualified mental health professionals
- **Prominent UI Disclaimer** — Clear warning that this is not a replacement for professional care
- **Fallback System** — Works without OpenAI API; provides helpful, safe default responses

## API Endpoint

### POST `/chat`

**Request:**
```json
{
  "message": "How can I manage anxiety?"
}
```

**Response:**
```json
{
  "answer": "Here are some grounding techniques...",
  "crisis": false
}
```

If `"crisis": true`, the response contains immediate crisis resources.

## Testing

Run the app and the chatbot automatically responds to messages with or without OpenAI:

**Example:** Testing with Python
```python
import requests
response = requests.post(
    'http://127.0.0.1:5000/chat',
    json={'message': 'What can help with stress?'}
)
print(response.json())
```

**Crisis Detection Test:**
```python
response = requests.post(
    'http://127.0.0.1:5000/chat',
    json={'message': 'I want to harm myself'}
)
# Returns immediate crisis resources
```

## Environment Variables

Create a `.env` file (from `.env.example`) with:

```
OPENAI_API_KEY=your_openai_key_here  # Optional (for AI responses)
FLASK_ENV=development
FLASK_DEBUG=1
```

## Ethical Principles

✔ Supports mental well-being in a safe, responsible way  
✔ Does NOT provide medical diagnoses or treatment  
✔ Uses only open-source and permissioned libraries  
✔ All responses are empathetic and non-judgmental  
✔ Directs users to professionals when appropriate  

## Technologies

- **Backend:** Flask, Python
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **AI Model:** OpenAI GPT-3.5-turbo (optional)
- **Server:** CORS-enabled Flask development server

## Resources

- [MentalHealth.gov — Get Help](https://www.mentalhealth.gov/get-help)
- [International Crisis Hotlines](https://www.opencounseling.com/suicide-hotlines)
- [NAMI (US) — Mental Health Support](https://www.nami.org/)

---

**Built with care for mental wellbeing.** Always reach out to a mental health professional if you need real support.
