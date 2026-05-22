# AI Process Efficiency Assistant

AI Process Efficiency Assistant is a Streamlit MVP for supporting product and project team workflows with AI and evaluating the impact of AI on process efficiency.

The application uses the real OpenAI API through the Responses API with structured JSON output when a valid API key is configured. Mock mode does not generate fake analysis; it only shows a clear warning that a valid key and billing are required.

## Thesis Context

This platform was developed as an experimental MVP for a bachelor thesis on the impact of artificial intelligence technologies on the efficiency of product and project management processes in IT companies.

The MVP demonstrates how AI can support:

- task quality analysis;
- product and project artifact generation;
- feedback analysis;
- KPI-based evaluation of process efficiency before and after AI support.

## Tech Stack

- Python 3.11+
- Streamlit
- Pandas
- Plotly
- python-dotenv
- OpenAI Python SDK
- CSV storage

## Project Structure

```text
ai_process_efficiency_assistant/
├── app.py
├── llm_client.py
├── prompts.py
├── kpi_calculator.py
├── data_storage.py
├── requirements.txt
├── README.md
├── .env.example
└── data/
    ├── sample_feedback.csv
    └── kpi_results.csv
```

## Setup

```bash
cd ai_process_efficiency_assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Environment Variables

Create a `.env` file in the same folder as `app.py`:

```text
ai_process_efficiency_assistant/.env
```

Full local path in this workspace:

```text
/Users/arturmusaelan/Documents/AI Process Efficiency Assistant/ai_process_efficiency_assistant/.env
```

You can create it from the example file:

```bash
cp .env.example .env
```

To enable real AI responses, add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
APP_MODE=auto
```

Never hardcode the API key in Python files.

## Runtime Modes

`APP_MODE=auto`

Uses the real OpenAI API when `OPENAI_API_KEY` is available. If the key is missing or still a placeholder value, AI modules show a mock-mode warning instead of generating fake analysis.

`APP_MODE=real`

Requires a valid OpenAI API key. If the key is missing or the API call fails, the app shows an error instead of silently using mock output.

`APP_MODE=mock`

Forces mock mode. AI modules do not call OpenAI and do not generate fake realistic output.

The top of the Streamlit app always shows the current mode:

- Real OpenAI API mode is active.
- Mock mode is active. Add valid OPENAI_API_KEY to .env for real AI responses.
- APP_MODE=real but OPENAI_API_KEY is missing.

## Modules

### Task Quality Analyzer

Analyzes a product/project task description and returns:

- task quality score;
- detected elements;
- missing or weak elements;
- recommendations;
- improved task description split into practical sections.

### Artifact Generator

Generates selected product/project artifacts:

- Product Brief / PRD;
- User stories;
- Acceptance criteria;
- QA checklist;
- Risk register.

### Feedback Analyzer

Analyzes multiple feedback items and returns:

- main feedback themes;
- repeated user problems;
- sentiment summary;
- product hypotheses;
- recommended metrics;
- priority table.

### KPI Impact Calculator

Calculates deterministic before/after process metrics:

- Time Saving %;
- Quality Change;
- Clarification Reduction %;
- Defect/Risk Change %;
- Cost Saving;
- Efficiency Index.

KPI results are appended to:

```text
data/kpi_results.csv
```

## Test Scenarios

### Test 1: Verification Task

Input:

```text
Потрібно додати новий екран верифікації користувача, де буде показано статус документів і пояснення, що потрібно зробити далі.
```

Expected:

- mentions verification;
- mentions document statuses;
- mentions user guidance;
- includes edge cases for rejected, pending, and missing documents;
- includes analytics for the verification flow;
- does not mention PDF export, weekly status meetings, or unrelated project reports.

### Test 2: PDF Export Task

Input:

```text
As a user, I want to export my project report to PDF so that I can share it with stakeholders before the weekly status meeting.
```

Expected:

- mentions PDF export;
- mentions project report;
- mentions stakeholders;
- includes export success and failure;
- includes empty report and large report cases;
- does not mention verification, payment, documents, or login.

### Test 3: Verification Feedback

Input:

```text
1. Не розумію, чому мої документи відхилили.
2. Дуже довго проходить перевірка.
3. Хотілося б бачити статус кожного документа.
4. Незрозуміло, які саме фото треба завантажити.
5. Після відхилення не пояснюється причина.
```

Expected:

- mentions unclear rejection reasons;
- mentions long verification time;
- mentions document status visibility;
- mentions photo upload instructions;
- mentions verification completion metrics;
- does not mention PDF export, project reports, shopping cart, or unrelated topics.

### Test 4: Feedback Analysis Artifact

Input:

```text
Створити AI-модуль для аналізу користувацького фідбеку та формування продуктових гіпотез.
```

Expected:

- mentions feedback ingestion;
- mentions topic clustering;
- mentions sentiment analysis;
- mentions product hypotheses;
- mentions recommended metrics;
- mentions Product Manager or Product Analyst users;
- does not mention verification, PDF export, or payment unless the input mentions them.

## Notes

The OpenAI integration is implemented in `llm_client.py`.

The prompts and JSON schemas are implemented in `prompts.py`.

The KPI calculator does not use OpenAI. It is deterministic and uses safe calculation functions so invalid baseline values do not crash the app.
