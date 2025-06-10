import spacy
from spacy.matcher import PhraseMatcher
import re
import json
from datetime import datetime
import spacy.cli
from spacy.util import is_package
import subprocess
from sentence_transformers import SentenceTransformer, util

# Check if the spaCy language model "en_core_web_sm" is installed
# If not, download it using subprocess to run the command-line installer
if not is_package("en_core_web_sm"):
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])

# Alternatively, you could use spaCy's API directly:
# spacy.cli.download("en_core_web_sm")

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Load skill patterns from a JSONL file
# Each line in the file is a JSON object with a "pattern" key
with open('data/skill_patterns.jsonl', 'r', encoding = 'utf8') as f:
    patterns = [json.loads(line)['pattern'] for line in f]

# Initialize PhraseMatcher to match skills based on text patterns
# attr="LOWER" ensures case-insensitive matching
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# Convert skill pattern strings to spaCy Doc objects for matching
patterns = [nlp.make_doc(skill) for skill in patterns]

# Add skill patterns to the matcher under the label "SKILL"
matcher.add("SKILL", patterns)

# Regular expression to match most common email formats
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')

# Regular expression to match international and formatted phone numbers
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')

class ResumeParser:
    def __init__(self, resume_text):
        self.text = resume_text

    def extract_name_from_resume(self):
        """
        Attempts to extract the candidate's name from the top 5 lines of the resume text.

        Returns:
            str or None: The extracted name in title case if found, otherwise None.
        
        Notes:
            - Looks for names written in either ALL CAPS or Title Case.
            - Matches only 2 or 3-word names (e.g., "Hasnain Tariq", "Hasnain Tariq Channa").
        """    

        # Split the resume text into lines and remove leading/trailing whitespace
        lines = self.text.strip().split('\n')

        # Limit the search to the top 5 lines, assuming the name appears near the top
        for line in lines[:5]:  
            line = line.strip() # Clean up whitespace
            if not line:
                continue # Skip empty lines

            # Check if the line is a name written in ALL CAPS (e.g., "HASNAIN" or "HASNAIN TARIQ")
            if re.match(r"^([A-Z]{2,}\s){1,2}[A-Z]{2,}$", line):  # ALL CAPS
                return line.title()  # Convert to title case (e.g., "Hasnain Tariq") for consistency

            # Check if the line is a name in Title Case (e.g., "Hasnain Tariq" or "Hasnain")
            elif re.match(r"^([A-Z][a-z]+\s){1,2}[A-Z][a-z]+$", line):  # Title Case
                return line  # Already in expected format, return as-is
        # If no match is found in the top 5 lines, return None    
        return None


    def extract_emails_from_resume (self):
        """
        Extracts all email addresses from the resume text using a predefined regex pattern.

        Returns:
            list: A list of email addresses found in the resume text.
        """
        # Use the EMAIL_REG regex pattern to find all matches in the resume text
        return re.findall(EMAIL_REG, self.text)



    def extract_phone_number_from_resume(self):
        """
        Extracts a phone number from the resume text using a predefined regex pattern.

        Returns:
            str or None: The first phone number found if valid, otherwise None.
        """
        # Find all phone number matches using the PHONE_REG pattern
        phone = re.findall(PHONE_REG, self.text)

        if phone:
            # Get the first phone number match and remove any formatting characters
            number = ''.join(phone[0])
            # Validate: number is found in text and is a reasonable length
            if self.text.find(number) >= 0 and len(number) <16:
                return number
            
        return None



    def extract_skills_from_resume(self):
        """
        Extracts skills from the resume text using spaCy PhraseMatcher.

        Returns:
            list: A sorted list of unique skills matched in the resume text.
        """
        # Process the resume text using spaCy NLP pipeline
        # Capitalize() is used here, but may not be necessary and could be replaced with lowercasing if needed
        text = nlp(self.text.capitalize())

        # Apply the matcher to the processed text to find skill pattern matches
        matches = matcher(text)

        # Extract matched spans and return unique, sorted skill names
        return sorted({text[start:end].text for _, start, end in matches})




    def extract_degrees_from_resume(self):
        """
        Extracts educational degrees from the resume text using regular expression patterns.

        Returns:
            list: A list of unique degree names found in the text, in the order they appear.
        """
        # Regular expression patterns to capture common degree formats
        degree_patterns = [
            r"(Bachelor\s+of\s+[A-Za-z\s&\s,]+)",    # e.g., Bachelor of Science
            r"(Master\s+of\s+[A-Za-z\s&]+)",         # e.g., Master of Engineering
            r"(Doctor\s+of\s+[A-Za-z\s&]+)",         # e.g., Doctor of Philosophy
            r"(BS\s+in\s+[A-Za-z\s&]+)",             # e.g., BS in Computer Science
            r"(MS\s+in\s+[A-Za-z\s&]+)",             # e.g., MS in Data Analytics
            r"(Ph\.?D\s+in\s+[A-Za-z\s&]+)",         # e.g., PhD in Biology
            r"\b(BS\s+[A-Za-z\s&]+)\b(?!\s+in)",     # BS Computer Science
            r"\b(MS\s+[A-Za-z\s&]+)\b(?!\s+in)",     # MS Software Engineering
            r"\b(Ph\.?D\s+[A-Za-z\s&]+)\b(?!\s+in)", # PhD Mathematics
            r"\b(?:B\.?S\.?|M\.?S\.?|Ph\.?D\.?)\s+[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,3}", # General format
            r"([A-Za-z\s]*Degree\s+in\s+[A-Za-z\s&]+)" # e.g., Associate Degree in Nursing
        ]

        degrees = []

        # Apply each pattern to the resume text
        for pattern in degree_patterns:
            matches = re.findall(pattern, self.text, re.IGNORECASE)
            degrees.extend([match.strip() for match in matches])

        # Remove duplicates while preserving order
        return list(dict.fromkeys(degrees))

    

    def extract_all_experience_entries(self):
        """
        Extracts job experience entries from the resume text by detecting date ranges and associating
        them with nearby lines for job title and company name.

        Returns:
            list of dict: A list where each dict contains 'job_title', 'company', and 'duration' (in years).
        """

        lines = self.text.strip().split('\n')
        experience = []
        current_year = datetime.now().year

        # Pattern to detect date ranges like "Jan 2019 - Dec 2021" or "2018 - Present"
        date_pattern = re.compile(  
            r'((?:[A-Za-z]{3,9}\s+)?\d{4})\s*[-–to]+\s*((?:[A-Za-z]{3,9}\s+)?\d{4}|Present|Current)', 
            re.IGNORECASE
        )

        # Pattern to detect "Job Title at Company" or "Job Title - Company"
        inline_pattern = re.compile(r"(.*?)(?: at |, |- )(.+)", re.IGNORECASE)

        for i in range(len(lines)):
            line = lines[i].strip()
            date_match = date_pattern.search(line)

            if date_match:
                # Calculate duration
                if date_match.group(2).lower() == "current" or date_match.group(2).lower() == "present":
                    duration = f"{int(current_year) - int(date_match.group(1))}"
                else:
                    duration = f"{int(date_match.group(2)) - int(date_match.group(1))}"

                # Look at the previous 1–2 lines for job title and company
                for j in [i - 1, i - 2]:
                    if j >= 0:
                        title_line = lines[j].strip()
                        inline_match = inline_pattern.search(title_line)

                        if inline_match:
                            job_title = inline_match.group(1).strip()
                            company = inline_match.group(2).strip()
                            experience.append({
                                "job_title": job_title,
                                "company": company,
                                "duration": duration
                            })
                            break # Stop after finding a valid entry

                        elif j - 1 >= 0:
                                # Try separate lines: job title above, company below
                                job_title = lines[j - 1].strip()
                                company = lines[j].strip()
                                if job_title and company:
                                    experience.append({
                                        "job_title": job_title,
                                        "company": company,
                                        "duration": duration
                                    })
                                    break
        return experience
    
    def extract_relevant_experience(self,resume_experience,jd_experience):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        relevant_experience = []
        for i in resume_experience:

            job_title= i['job_title']

            if jd_experience[1] is not None:
                score = util.cos_sim(model.encode(job_title), model.encode(jd_experience[1]))

            if score[0][0] > 0.5:
                relevant_experience.append(i)

        return relevant_experience

    def parse(self,jd_experience):
        """
        Orchestrates the extraction of key resume information including:
        name, email, phone number, skills, education, and work experience.

        Returns:
            dict: A structured dictionary containing the extracted resume data.
        """

        # Extract fields using individual extraction methods
        name = self.extract_name_from_resume() or "Not Found"
        skills = self.extract_skills_from_resume ()
        degrees = self.extract_degrees_from_resume()
        email = self.extract_emails_from_resume ()
        phone_number = self.extract_phone_number_from_resume()
        experience = self.extract_all_experience_entries()
        relevant_experience = self.extract_relevant_experience(experience,jd_experience)

        # Return a structured dictionary with all extracted fields
        return {
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "skills": skills,
            "education": [
                {"degree": deg} for deg in degrees
            ],
            "experience": experience,
            "relevant_experience" : relevant_experience,
            "resume_text" : self.text
        }

