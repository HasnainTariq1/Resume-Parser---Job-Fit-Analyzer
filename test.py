from src.resume_parser import ResumeParser
from src.jd_parser import JobDescriptionParser
from src.similarity_match import SimilarityMatch
from src.llm_matcher import score_resume_with_llm
# Extract the text from resumes in PDF form
import fitz, pprint

def extract_text_from_pdf(path):
  doc = fitz.open(path)
  text = ""
  for page in doc:
    text += page.get_text()

  return text

resume_text = extract_text_from_pdf("data/4.pdf")




description = """
Job Summary:
We are seeking a skilled AWS Data Engineer to join our data team. In this role, you will design, build, and maintain scalable and reliable data pipelines on AWS. You'll work closely with data analysts, data scientists, and stakeholders to deliver data-driven insights and solutions using cloud-native technologies.

Key Responsibilities:
Design, develop, and deploy robust ETL/ELT pipelines using AWS services (e.g., Glue, Lambda, EMR, Step Functions, S3, Redshift).

Implement data lake and data warehouse solutions to support analytics and business intelligence needs.

Collaborate with cross-functional teams to understand data requirements and deliver reliable datasets.

Monitor and optimize pipeline performance and data reliability.

Implement data governance practices including data quality, lineage, and cataloging.

Automate data validation and alerting processes.

Maintain and improve CI/CD processes for data pipeline deployments.

Required Qualifications:
Bachelor’s degree in Computer Science, Engineering, Information Systems, or related field.

3+ years of experience in data engineering or software engineering.

Strong hands-on experience with AWS services including Glue, S3, Redshift, Lambda, Athena, and IAM.

Proficiency in Python, SQL, and Spark (PySpark preferred).

Experience with orchestration tools like Airflow or AWS Step Functions.

Familiarity with data modeling, warehousing concepts, and performance tuning.

Knowledge of DevOps principles and tools such as Git, Terraform, or CloudFormation.

Preferred Qualifications:
AWS Certified Data Analytics – Specialty or AWS Certified Solutions Architect.

Experience with real-time data processing (e.g., Kinesis, Kafka).

Knowledge of data security and compliance best practices.

Familiarity with machine learning pipelines or big data tools (EMR, Hadoop).

"""
# job_description_details = JobDescriptionParser(description).parse_jd_data()
# resume_details = ResumeParser(resume_text).parse(job_description_details['experience_required'])
# resume_similarity_score = SimilarityMatch(resume_details,job_description_details).similarity_check_in_resume_and_job_desc()

llm_score = score_resume_with_llm(description, resume_text)

print(llm_score)

# pprint.pprint(job_description_details)
# pprint.pprint(resume_details)
# print(resume_similarity_score)