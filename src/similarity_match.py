from sentence_transformers import SentenceTransformer, util

class SimilarityMatch:
        
    def __init__(self, resume_details, job_desc_details):
        self.resume_details = resume_details
        self.job_desc_details = job_desc_details
    
    def similarity_check_in_resume_and_job_desc(self):
        model = SentenceTransformer('all-MiniLM-L6-v2')
      
        # Combine relevant experience entries into one string
        relevant_experience_entries = self.resume_details.get("relevant_experience", [])
        # print(relevant_experience_entries)

        # Extract job titles and maybe companies
        experience_text = " ".join([
            f"{entry.get('job_title', '')} at {entry.get('company', '')} for {entry.get('duration', '')} months"
            for entry in relevant_experience_entries
        ])

        scores = {
            "skills": util.pytorch_cos_sim(
                model.encode(" ".join(self.resume_details.get("skills", [])), convert_to_tensor=True),
                model.encode(" ".join(self.job_desc_details.get("required_skills", [])), convert_to_tensor=True)
            ).item(),

            "experience": util.pytorch_cos_sim(
                model.encode(experience_text, convert_to_tensor=True),
                model.encode(" ".join(self.job_desc_details.get("experience_required", [])), convert_to_tensor=True)
            ).item(),

            "overall": util.pytorch_cos_sim(
                model.encode(self.resume_details.get("resume_text"), convert_to_tensor=True),
                model.encode(self.job_desc_details.get("job_description"), convert_to_tensor=True)
            ).item()
        }
        # print(scores)

        final_score = 0.5 * scores["skills"] + 0.3 * scores["experience"]  + 0.2 * scores["overall"]


        return final_score

