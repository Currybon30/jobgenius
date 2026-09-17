from pathlib import Path

import pymupdf

from app.ai_agents.premium_multiagents import jobfinder_agent
from app.db.mcp import init_mcp_client
from app.helpers.llm_call import agent7_jobfinder_format_result


async def test_agent_jobfinder():
    print("Testing agent jobfinder")
    await init_mcp_client()
    print("MCP client initialized")
    pdf_bytes = Path(
        r"D:\IT\My Projects\jobgenius\api_server\external\Tuong_Nguyen_Pham_Resume.pdf"
    ).read_bytes()
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()  # type: ignore
    doc.close()
    analyzed_results_dict = {
        "intent": {
            "target_role": "Software Engineer",
            "seniority_level": "Junior",
            "industry": "tech",
            "priority_goals": [
                "Enhance project management and team leadership experience",
                "Highlight technical skills in programming languages and frameworks",
                "Provide metrics or results for projects and experiences",
            ],
            "focus_areas": [
                "projects",
                "skills",
            ],
            "top_keywords": [
                "AI",
                "Python",
                "React.js",
                "TensorFlow",
                "AWS",
                "Machine Learning",
                "Full-stack development",
                "Team leadership",
            ],
            "optimization_strategy": {
                "must_have": [
                    "Demonstrable experience with AI and machine learning frameworks (e.g., TensorFlow)",
                    "Technical skills in Python, Java, C#, JavaScript, React.js",
                    "Experience with AWS services",
                ],
                "nice_to_have": [
                    "Projects showcasing real-world applications of technical skills",
                    "Leadership roles or team management experience",
                ],
                "avoid": [
                    "Generic statements without specific examples",
                    "Lack of quantifiable achievements or metrics in projects and experiences",
                ],
            },
        },
        "analyzer": {
            "sections": {
                "education": (
                    "EDUCATION \nUniversity of Windsor \nWindsor, ON \nBachelor of Computer Science \n "
                    "05/2025 – 12/2026 \n• \nCumulative GPA: 3.5 / 4.0 \n• \nAdmitted with advanced standing "
                    "into the degree completion program. \nCentennial College \n Toronto, ON \nAdvanced Diploma "
                    "in Software Engineering Technology – AI \n 01/2023 – 04/2025 \n• \nCumulative GPA: "
                    "4.311 / 4.5 \n• \nGraduated with High Honours - Recognized for outstanding academic "
                    "achievement and consistent excellence."
                ),
                "experience": (
                    "EXPERIENCE \nPeer Tutor \n Toronto, ON \nCentennial College \n 02/2025 – 04/2025 \n• \n"
                    "Tutored students in programming and machine learning. \n• \nClarified concepts and "
                    "reviewed assignments to improve understanding and academic performance. \n• \nFostered "
                    "a supportive and collaborative learning environment during one-on-one sessions."
                ),
                "skills": (
                    "SKILLS \nTechnical: Python, Java, C#, JavaScript, React.js, TensorFlow, SQL, Git, AWS \n"
                    "Soft: Communication, teamwork, problem solving, adaptability, leadership \n"
                    "Language: Vietnamese – Fluent, English - Proficient"
                ),
                "volunteer": (
                    "Volunteer \n 04/2023 – 01/2025 \n• \nProvided direction and ushering students into the "
                    "event. \n• \nApproached students to answer questions. \n• \nManaged event registration, "
                    "distributed swag, and welcomed attendees."
                ),
                "projects": (
                    "PROJECTS \nImmigration Consultation Chatbot \n Toronto, ON \nTeam Lead \n "
                    "02/2025 – 04/2025 \n• \nLed a team of 6 in the end-to-end development of IRIS, a "
                    "full-stack AI-powered chatbot supporting international \nstudents with real-time "
                    "Canadian immigration guidance. \n• \nIntegrated Large Language Models (LLMs) and "
                    "Retrieval-Augmented Generation (RAG) for accurate, \nconversational, and "
                    "policy-grounded responses. \n• \nImplemented a multi-agent system using LangGraph, "
                    "applying agentic AI principles to orchestrate tasks such \nas document retrieval, "
                    "question answering, and dialogue management autonomously — significantly \nminimizing "
                    "the need for human intervention. \nStudent Attendance Tracking System \n Toronto, ON \n"
                    "Team Member \n 03/2025 – 04/2025 \n• \nDeveloped a cloud-based automated attendance "
                    "tracking system using AWS Rekognition and AWS \nComprehend to detect student ID cards, "
                    "extract textual data via OCR, and record attendance accurately. \n• \nImplemented "
                    "backend services using Python, AWS Chalice, and Boto3, with serverless architecture to "
                    "process \nattendance data, store records in AWS S3, and provide real-time voice "
                    "feedback using AWS Polly. \n• \nDesigned and built a user-friendly web interface with "
                    "HTML, CSS, and JavaScript, enabling professors and \nadministrators to manage "
                    "attendance records, add student data, and generate reports securely. \nToronto "
                    "Collision Prediction System \n Toronto, ON \nTeam Member \n 02/2024 – 04/2025 \n• \n"
                    "Analyzed real KSI (Killed or Seriously Injured) data from the Toronto Police Service, "
                    "uncovering key factors \ncontributing to collisions and enhancing the classification "
                    "model. \n• \nDeveloped an intuitive interface using HTML and CSS, allowing users to "
                    "input data and receive personalized \npredictions on local collision risks. \n• \n"
                    "Integrated a Flask backend to process user inputs and generate real-time collision "
                    "risk predictions based on \ntrained models and neighborhood-specific data."
                ),
            },
            "years_exp": 0,
            "has_summary": False,
            "has_skills": True,
            "has_experience": True,
            "has_projects": True,
            "has_education": True,
            "emails": [
                "pham39@uwindsor.ca",
            ],
            "phone_numbers": [
                "437)-428-6446",
            ],
            "has_metrics": False,
            "hard_skills": [
                "java",
                "sql",
                "aws",
                "git",
                "javascript",
                "html",
                "css",
                "react",
                "python",
            ],
            "soft_skills": [
                "teamwork",
                "adaptability",
                "collaboration",
                "communication",
                "problem solving",
                "leadership",
            ],
            "certifications": [],
            "languages": [],
            "professional_links": {
                "linkedin": "https://linkedin.com/in/tuongnguyenpham",
                "github": "https://github.com/Currybon30",
                "gitlab": None,
                "portfolio": None,
                "other": [],
            },
            "has_volunteer": False,
        },
    }
    messages, raw_jobs = await jobfinder_agent(
        resume_text=text, analyzed_results_dict=analyzed_results_dict
    )
    jobfinder_result = agent7_jobfinder_format_result(messages, raw_jobs)
    explanation_message = jobfinder_result["message"]
    jobs = jobfinder_result.get("jobs") or []
    print(explanation_message)
    print(jobs)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_agent_jobfinder())
