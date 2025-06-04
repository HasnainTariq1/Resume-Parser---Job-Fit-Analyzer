from src.resume_parser import ResumeParser
# Extract the text from resumes in PDF form
import fitz, pprint

def extract_text_from_pdf(path):
  doc = fitz.open(path)
  text = ""
  for page in doc:
    text += page.get_text()

  return text

resume_text = extract_text_from_pdf("data/2.pdf")

pprint.pprint(ResumeParser(resume_text).parse())