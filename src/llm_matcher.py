from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity




def score_resume_with_llm(resume_text, job_text, apiKey):
    client = OpenAI(api_key=apiKey)
    prompt = f"""
You are an expert hiring assistant.

Given the following resume and job description, analyze the candidate's suitability for the job on a scale from 0 to 1.

### Job Description:
{job_text}

### Resume:
{resume_text}

Return only a JSON response like:
{{"score": float (0 to 1)
   "Candidate Name":  }}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    # print("in llm", response)
    return response.choices[0].message.content
