# WORKAI

WORKAI is an advanced AI-powered research and browser automation tool using Playwright and Groq LLMs.

## Features
- Deep multi-layered research using Groq LLMs
- Automated browser search and content extraction (Playwright)
- Fact verification and contradiction analysis
- Modern, modular Python codebase

## Setup Instructions
1. **Clone the repository**
2. **Create and activate a Python virtual environment**
	- Windows PowerShell: `python -m venv .venv; .\.venv\Scripts\Activate`
	- macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
3. **Install dependencies**
	- `pip install -r requirements.txt`
4. **Install Playwright browsers**
	- `python -m playwright install`
5. **Configure environment variables**
	- Copy `.env.example` to `.env` and add your GROQ_API_KEY
	- Example:
	  ```env
	  GROQ_API_KEY=your_groq_api_key_here
	  SEARCH_TIMEOUT=30000
	  MAX_SEARCH_STEPS=10
	  DEBUG=True
	  ```

## Usage
Run the main app:
```bash
python main.py
```
You can also pass a query as an argument:
```bash
python main.py "What is the future of AI in medicine?"
```

## File Overview
- `main.py`: Main application entry point
- `browser_controller.py`: Browser automation logic
- `research_agent.py`: AI research logic
- `.env`: Environment variables for API keys
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation

## Troubleshooting
- Ensure your virtual environment is activated before installing or running.
- If Playwright browsers are not installed, run `python -m playwright install`.
- For API errors, check your GROQ_API_KEY in `.env`.

## License
MIT
