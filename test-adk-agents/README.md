# ADK Agents

Step 1 - Create a python environment

``` bash
python3 -m venv .venv
venv\Scripts\activate 
pip install -r requirements.txt
```

Step 2 - Add your key to .env file

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

Step 3 - Run ADK 

```bash
adk web
```