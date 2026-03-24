import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pymupdf
from internal_db.skills import soft_skills, it_skills, business_skills
from jd import extract_skills_from_jd_text


def extract_text_from_resume(file_path: str):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return "File not found."
        if not file_path.lower().endswith('.pdf'):
            print(f"Unsupported file format: {file_path}")
            return "Unsupported file format. Please upload a PDF."
        doc = pymupdf.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from resume: {e}")
        return ""
    
def extract_soft_skills_from_text(text: str):
    found_soft_skills = set()
    for soft_skill in soft_skills:
        if soft_skill.lower() in text.lower():
            found_soft_skills.add(soft_skill)
    missing_soft_skills = set(soft_skills) - found_soft_skills
    return found_soft_skills, missing_soft_skills
    
    
def extract_skills_from_text_without_jd(text: str, field: str):
    found_skills = set()
    found_soft_skills, missing_soft_skills = extract_soft_skills_from_text(text)
    if field == 'it':
        skills_to_check = it_skills
    elif field == 'business':
        skills_to_check = business_skills
    else:
        print(f"Unknown field: {field}")
        return {"skills": [], "missing_skills": [], "matching_score": 0}
    
    for skill in skills_to_check:
        if skill.lower() in text.lower():
            found_skills.add(skill)
    missing_skills = set(skills_to_check) - found_skills
    
    for soft_skill in soft_skills:
        if soft_skill.lower() in text.lower():
            found_soft_skills.add(soft_skill)
            
    matching_score = len(found_skills) / len(skills_to_check) * 100 if skills_to_check else 0
    return {
        "skills": list(found_skills),
        "missing_skills": list(missing_skills),
        "soft_skills": list(found_soft_skills),
        "missing_soft_skills": list(missing_soft_skills),
        "matching_score": matching_score
    }
    

def extract_skills_from_text_with_jd(text: str, jd_text: str):
    jd_skills = extract_skills_from_jd_text(jd_text)
    found_skills = set()
    found_soft_skills, missing_soft_skills = extract_soft_skills_from_text(text)
    for skill in jd_skills:
        if skill.lower() in text.lower():
            found_skills.add(skill)
    missing_skills = set(jd_skills) - found_skills
    matching_score = len(found_skills) / len(jd_skills) * 100 if jd_skills else 0
    return {
        "skills": list(found_skills),
        "missing_skills": list(missing_skills),
        "matching_score": matching_score,
        "soft_skills": list(found_soft_skills),
        "missing_soft_skills": list(missing_soft_skills)
    }

############################ Advanced features using AI #########################################
# Apply AI for smarter keyword extraction from PDF, semantic similarity, resume feedback.
import re
import asyncio
from ollama import AsyncClient

# Use AI to extract skills more accurately from the resume text
async def extract_skills_with_ai(text: str):
    # Use llm to analyze the resume text and extract skills
    messages=[
        {
            'role': 'system',
            'content': 'You are a helpful assistant that extracts skills from resumes. Extract both hard and soft skills mentioned in the resume text.'
        },
        {
            'role': 'user',
            'content': f"""Extract skills from the following resume text:\n\n{text} with the following format:\n
            Hard Skills: [list of hard skills]\n\n
            Soft Skills: [list of soft skills]
            
            
            Please note that do not include any other information or paraphrase any words, just the skills in the specified format.
            """
        }
    ]
    response = await AsyncClient(host='http://localhost:11434').chat(model='qwen2.5:7b', messages=messages)
    
    if __name__ == "__main__":
        print("\n\n\n\n\n")
        print("AI Response:\n", response.message.content)
        print("\n\n\n\n\n")
    
    # Extract the content from the response
    hard_skills = []
    soft_skills = []
    
    # Parse the response to separate hard and soft skills
    if response and response.message and response.message.content:
        content = response.message.content
        hard_skills_match = re.search(r'Hard Skills:\s*(.*)', content)
        soft_skills_match = re.search(r'Soft Skills:\s*(.*)', content)
        if hard_skills_match:
            hard_skills = [skill.strip() for skill in hard_skills_match.group(1).split(',')]
        if soft_skills_match:
            soft_skills = [skill.strip() for skill in soft_skills_match.group(1).split(',')]
            

    
    return {
        "skills": hard_skills,
        "soft_skills": soft_skills
    }
    

def extract_contact_info(text: str):
    # Use regex to find potential email addresses and phone numbers
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return {
        "emails": emails,
        "phone_numbers": phones
    }
    
    

############################ TESTING #########################################
if __name__ == "__main__":
    pdf_path = r"D:\IT\My Projects\job_recommender_system\api_server\external_resources\Tuong Nguyen Pham Resume.pdf"
    resume_text = extract_text_from_resume(pdf_path)
    
    skills = extract_skills_from_text_without_jd(resume_text, 'it')
    print("Extracted Skills without JD:", skills)
    
    skills_ai = asyncio.run(extract_skills_with_ai(resume_text))
    print("Extracted Skills with AI:", skills_ai)
    