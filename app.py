from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from src.resume_parser import ResumeParser
from src.jd_parser import JobDescriptionParser
from src.similarity_match import SimilarityMatch
from zipfile import ZipFile
import json
from io import BytesIO
from src.llm_matcher import score_resume_with_llm
import fitz, pprint
import os


app = Flask(__name__)
CORS(app, origins=["https://fitmyresume.netlify.app"], supports_credentials=True) # Allow requests from React

def extract_text_from_pdf(file_stream):
  # Open the PDF file from a binary stream using PyMuPDF (fitz)
  doc = fitz.open(stream=file_stream.read(), filetype="pdf")
  text = ""

  # Iterate through each page in the PDF document
  for page in doc:
    # Extract text from the current page and append it to the text variable
    text += page.get_text()
  return text


@app.route('/api/match', methods=['POST'])
def match():

  """
    API endpoint to match uploaded resumes against a given job description.
    
    Expects:
        - Multiple PDF files via 'resumes' form field.
        - A job description string via 'job' form field.
    
    Returns:
        - A JSON response containing a list of matched resumes with:
            - filename
            - candidate name
            - similarity score (rounded)
        - Only resumes with a similarity score >= 0.5 are included.
  """
  # Get the uploaded resume files from the request (multiple files allowed)
  resume_files = request.files.getlist("resumes")

  # Get the job description text from the form data
  job_text = request.form.get("job", "")

  # If either resumes or job description is missing, return an error response
  if not resume_files or not job_text:
      return jsonify({'error': 'Missing file or job description'}), 400


  # Parse the job description using JobDescriptionParser
  job_text = JobDescriptionParser(job_text).parse_jd_data()

  results = []
  # Iterate over each uploaded file
  for file in resume_files:
    # Skip files that are not PDFs    
    if not file.filename.endswith('.pdf'):
      continue 

    try:
      # Extract raw text from the PDF resume
      resume_text = extract_text_from_pdf(file)

      # Parse the extracted resume text using ResumeParser
      resume_parsed = ResumeParser(resume_text).parse(job_text['experience_required'])

      # Calculate similarity score between parsed resume and job description
      score = SimilarityMatch(resume_parsed, job_text).similarity_check_in_resume_and_job_desc()

      # If the similarity score is above threshold (e.g., 0.5), add it to the results
      if score>=0.5:
        results.append({
          "filename": file.filename,
          "candidateName": resume_parsed['name'],
          "score": round(score, 2)
        })

    except Exception as e:
      print(f"Error processing {file.filename}: {e}")

  # Sort results in descending order based on similarity score    
  results = sorted(results, key=lambda x: x['score'], reverse=True)
  
  # Return the results as a JSON response
  return jsonify({"results": results})
  



@app.route('/api/match_llm', methods=['POST'])
def match_using_llm():
  """
    API endpoint to match resumes against a job description using an LLM (Large Language Model).

    Expects:
        - 'resumes': one or more PDF resume files via multipart form-data.
        - 'job': job description text via form-data.
        - 'api_key': API key for accessing the LLM service.

    Returns:
        - JSON response containing a list of resumes with:
            - filename
            - candidate name (extracted by LLM)
            - similarity score (>= 0.5 only)
        - Results are sorted by score in descending order.
  """

  # Get uploaded resume files and job description from the request
  resume_files = request.files.getlist("resumes")
  job_text = request.form.get("job", "")
  api_key = request.form.get("api_key")
 
  # Get uploaded resume files and job description from the request
  if not resume_files or not job_text:
    return jsonify({'error': 'Missing file or job description'}), 400


  results = []

  # Process each uploaded resume file
  for file in resume_files:
    # Skip files that are not PDFs    
    if not file.filename.endswith('.pdf'):
      continue  

    try:
      # Extract text from the resume PDF
      resume_text = extract_text_from_pdf(file)
      
      # Call LLM-based scoring function with resume, job description, and API key
      score_response = score_resume_with_llm(resume_text, job_text , api_key)
      
      # Parse the LLM response from JSON string to dictionary
      responseScore = json.loads(score_response)
      # print(responseScore)

      # Convert score to float
      score = float(responseScore["score"])
      
      # Include in results if score meets threshold
      if score >= 0.5:
        results.append({
          "filename": file.filename,
          "candidateName": responseScore['Candidate Name'],
          "score": round(score,2)
        })

    except Exception as e:
      print(f"Error processing {file.filename}: {e}")

  # Sort the results by score in descending order
  results = sorted(results, key=lambda x: x['score'], reverse=True)

  # Return the results as a JSON response
  return jsonify({"results": results})





@app.route('/api/download-top', methods=['POST'])
def download_top_resumes():
  """
    API endpoint to download selected Top resumes as a ZIP file.

    Expects:
        - 'resumes': one or more resume files (PDFs) via multipart form-data.

    Returns:
        - A downloadable ZIP archive ('top_candidates.zip') containing all Top uploaded resumes.
  """
  # Get uploaded resume files from the request
  resumes = request.files.getlist('resumes')

  # Return error if no resumes are uploaded
  if not resumes:
    return {'error': 'No resumes provided'}, 400

  # Create an in-memory file object to hold the ZIP archive
  memory_file = BytesIO()

  # Create and write files to the ZIP archive
  with ZipFile(memory_file, 'w') as zf:
    for resume in resumes:
      filename = resume.filename # Get the original filename
      file_bytes = resume.read() # Read the file content
      zf.writestr(filename, file_bytes) # Write to the ZIP file with original name

  # Reset file pointer to the beginning  
  memory_file.seek(0)

  # Return the in-memory ZIP file as a downloadable attachmen
  return send_file(memory_file, download_name='top_candidates.zip', as_attachment=True)



if __name__ == '__main__':
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 4000))  # Use PORT env var or default to 5000
    app.run(host="0.0.0.0", port=port)
