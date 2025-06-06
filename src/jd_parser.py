import re
from src.resume_parser import ResumeParser

job_title = "AWS Data Engineer"

class JobDescriptionParser:
    def __init__(self, jd_text):
        self.jd_text = jd_text

    def extract_experience_from_jd(self):
        """
        Extracts years or months of experience along with associated fields or job titles from a text.

        This function uses multiple regular expression patterns to identify durations of professional 
        experience (e.g., "3 years", "5+ months") and attempts to link them to relevant fields or roles 
        mentioned nearby (e.g., "in software engineering", "as a data analyst").

        Args:
            text (str): The input text to parse.

        Returns:
            List[Tuple[int, str, Optional[str]]]: A list of tuples, each containing:
                - The number of years or months (int)
                - The unit ('years', 'months', etc.)
                - The associated field or role (str), or None if not found
        """

        # Define a list of regex patterns to capture various experience expressions
        patterns = [
            r'(?i)(\d+)\s*[-–to]+\s*(\d+)\s*(years?|months?|yrs?)',
            r'(?i)(?:experience\s*[:\-]?\s*)(\d+)\s*[-–]\s*(\d+)\s*(years?|months?|yrs?)',
            r'(?i)(\d+)\s*(years?|months?|yrs?)\s+experience',
            r'(?i)(?:at least|min(?:imum)? of|minimum)\s+(\d+)\s*(years?|months?|yrs?)\s+of experience',
            r'(?i)(\d+)\+?\s*(years?|months?|yrs?)\s+(?:of\s+)?experience',
            r'(?i)(\d+)\s*\+\s*(years?|months?|yrs?)',
            r'(?i)(\d+)\s*(years?|months?|yrs?)'
        ]

        # List to store matched experience and field results
        matches = []

        # Loop through each pattern to find matches in the input text
        for pattern in patterns:
            for match in re.finditer(pattern, self.jd_text):
                full_match = match.group(0) # The entire matching text
                span = match.span() # The start and end indices of the match

                # Extract matched number and unit (e.g., "3 years")
                groups = match.groups()
                if len(groups) >= 2:
                    number = int(groups[0]) # Extract the numeric value
                    unit = groups[1].lower() # Extract the unit in lowercase (years/months)
                else:
                    continue # Skip if we don’t have both number and unit

                # Try to identify the relevant context (e.g., "in software development")
                context = self.jd_text[span[1]:span[1] + 80]  # look ahead 80 characters

                # Look for phrases like "in [field]" or "as [title]" in the context
                field_match = re.search(
                    r'in ([\w\s\/&\-]+?)([.,;]| with| using| on| and| for|$)', 
                    context, 
                    re.IGNORECASE
                )

                if not field_match:
                    field_match = re.search(
                        r'as ([\w\s\/&\-]+?)([.,;]| with| using| on| and| for|$)', 
                        context, 
                        re.IGNORECASE
                    )

                # Extract the field name if found, else set to None
                field = field_match.group(1).strip() if field_match else None

                # Append the result as a tuple (number, unit, field)
                matches.append((number, unit, field))

        return matches  # Return the list of extracted experience information
    
    def parse_jd_data(self):

        # Extract experience information from the job description using a helper method
        jd_experience = self.extract_experience_from_jd()
        
        return {
            'job_title':job_title,

            # Format the extracted experience into a readable string (e.g., "3 years") and include the context or source
            'experience_required' : [(str(jd_experience[0][0])+" "+str(jd_experience[0][1])), jd_experience[0][2]],

            # Extract relevant skills from the job description text using ResumeParser
            'required_skills' : ResumeParser(self.jd_text).extract_skills_from_resume(),
            'job_description' : self.jd_text
        }

