# Smart Resume Parser & Job Matcher

An intelligent NLP-powered tool to automate resume screening and job matching for HR professionals and recruiters. Built using Python, spaCy, sentence-transformers, React.js, and Flask, this system parses resumes, extracts key details, compares them with job descriptions, and calculates semantic similarity scores — with optional LLM integration for enhanced accuracy. The system supports both traditional ML matching and GPT-based LLM matching via OpenAI API.

---

## Workflows

1. Setup skill patterns JSONL file
2. Build resume parser using spaCy, Regex, and PhraseMatcher
3. Extract structured resume data: name, email, phone, skills, degrees, experience
4. Parse job descriptions for required skills, experience, education
5. Compute semantic similarity using Sentence Transformers
6. Add optional GPT-3.5 turbo-based scoring for enhanced results
7. Setup Flask backend and React frontend
8. Deploy backend (Google Cloud) and frontend (Netlify)

---

# How to run?

### STEPS:

### Clone the repository

```bash
git clone https://github.com/HasnainTariq1/Resume-Parser---Job-Fit-Analyzer.git
```

### STEP 01 — Create and activate conda environment
```bash
conda create -n resumeparser python=3.10 
```

```bash
conda activate resumeparser
```


### STEP 02- Install dependencies
```bash
pip install -r requirements.txt
```


### STEP 03 — Run Flask backend
```bash
python main.py
```

STEP 04 — Run React frontend (in separate terminal)
```bash
cd frontend
npm install
npm start
```

Now,
```bash
Open your browser at localhost:3000 to view the app
```



```bash
Author: Hasnain Tariq
Machine Learning Engineer | NLP | AI
Email: hasnaintariq172@gmail.com
GitHub: https://github.com/HasnainTariq1
```
