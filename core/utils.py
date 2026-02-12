import os
import requests
from pypdf import PdfReader
from django.conf import settings

def translate_text(text, target_language='hi'):
    """
    Translates text to target language using googletrans library.
    Default target is Hindi ('hi'), but supports many languages.
    Common codes: 'hi' (Hindi), 'es' (Spanish), 'fr' (French), 'de' (German), etc.
    """
    try:
        from googletrans import Translator
        translator = Translator()
        
        # Skip translation if text is too short or target is English
        if not text or len(text.strip()) < 10 or target_language == 'en':
            return text
        
        # Translate in chunks if text is very long (API limit ~5000 chars)
        max_chunk_size = 4500
        if len(text) > max_chunk_size:
            # Split by sentences/paragraphs
            chunks = []
            current_chunk = ""
            for sentence in text.split('. '):
                if len(current_chunk) + len(sentence) < max_chunk_size:
                    current_chunk += sentence + '. '
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + '. '
            if current_chunk:
                chunks.append(current_chunk)
            
            # Translate each chunk
            translated_chunks = []
            for chunk in chunks:
                result = translator.translate(chunk, dest=target_language)
                translated_chunks.append(result.text)
            
            return ' '.join(translated_chunks)
        else:
            result = translator.translate(text, dest=target_language)
            return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        # Return original text if translation fails
        return text


def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_skills(text):
    """
    Extracts skills from text based on a predefined list.
    This is a basic implementation. In a real app, use NLP.
    """
    # Common tech skills list
    COMMON_SKILLS = {
        "python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "swift", "kotlin",
        "html", "css", "sql", "mysql", "postgresql", "mongodb", "aws", "azure", "docker",
        "kubernetes", "git", "react", "angular", "vue", "django", "flask", "spring", "node.js",
        "machine learning", "data science", "artificial intelligence", "deep learning",
        "communication", "leadership", "problem solving", "agile", "scrum", "project management"
    }
    
    found_skills = set()
    text_lower = text.lower()
    
    for skill in COMMON_SKILLS:
        # Simple word matching, can be improved
        if skill in text_lower:
            found_skills.add(skill)
            
    return list(found_skills)

def get_adzuna_jobs(skills, location="in"): 
    """
    Fetches job recommendations from Adzuna API based on skills.
    """
    if not skills:
        return []
    
    app_id = settings.ADZUNA_APP_ID
    app_key = settings.ADZUNA_APP_KEY
    
    # Adzuna API endpoint
    country = "in" # Default to India as requested
    
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    
    # Construct query from skills (top 3 skills to avoid over-constraint)
    what = " ".join(skills[:3]) 
    
    params = {
        'app_id': app_id,
        'app_key': app_key,
        'what': what,
        'content-type': 'application/json',
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except requests.RequestException as e:
        print(f"Adzuna API Error: {e}")
        return []

def get_jsearch_jobs(skills, location="India"):
    """
    Fetches job recommendations from JSearch API (via RapidAPI) based on skills.
    """
    if not skills:
        return []
    
    # Get API key from settings
    api_key = getattr(settings, 'RAPIDAPI_KEY', None)
    
    if not api_key:
        print("RapidAPI key not configured")
        return []
    
    url = "https://jsearch.p.rapidapi.com/search"
    
    # Construct query from skills
    query = " ".join(skills[:3]) + f" jobs in {location}"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Normalize JSearch data to common format
        jobs = []
        for job in data.get('data', [])[:10]:  # Limit to 10 jobs
            jobs.append({
                'id': job.get('job_id', ''),
                'title': job.get('job_title', ''),
                'company': {'display_name': job.get('employer_name', 'Unknown')},
                'location': {'display_name': job.get('job_city', '') + ', ' + job.get('job_country', '')},
                'description': job.get('job_description', ''),
                'created': job.get('job_posted_at_datetime_utc', ''),
                'salary_min': job.get('job_min_salary'),
                'salary_max': job.get('job_max_salary'),
                'redirect_url': job.get('job_apply_link', '')
            })
        
        return jobs
    except requests.RequestException as e:
        print(f"JSearch API Error: {e}")
        return []

def get_remoteok_jobs(skills):
    """
    Fetches remote job recommendations from RemoteOK API based on skills.
    """
    if not skills:
        return []
    
    url = "https://remoteok.com/api"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # RemoteOK returns array where first element is metadata
        if isinstance(data, list) and len(data) > 1:
            data = data[1:]  # Skip first element
        
        # Filter jobs based on skills
        skills_lower = [s.lower() for s in skills]
        jobs = []
        
        for job in data[:20]:  # Check first 20 jobs
            if not isinstance(job, dict):
                continue
                
            # Check if any skill matches job tags or description
            job_tags = [tag.lower() for tag in job.get('tags', [])]
            job_desc = job.get('description', '').lower()
            
            # Simple matching logic
            if any(skill in job_tags or skill in job_desc for skill in skills_lower):
                jobs.append({
                    'id': job.get('id', ''),
                    'title': job.get('position', ''),
                    'company': {'display_name': job.get('company', 'Unknown')},
                    'location': {'display_name': 'Remote'},
                    'description': job.get('description', '')[:500],  # Truncate long descriptions
                    'created': job.get('date', ''),
                    'salary_min': job.get('salary_min'),
                    'salary_max': job.get('salary_max'),
                    'redirect_url': job.get('url', '')
                })
                
                if len(jobs) >= 10:  # Limit to 10 jobs
                    break
        
        return jobs
    except requests.RequestException as e:
        print(f"RemoteOK API Error: {e}")
        return []

def aggregate_jobs(skills, location="India"):
    """
    Aggregates job results from multiple APIs.
    """
    all_jobs = []
    
    # Fetch from Adzuna
    try:
        adzuna_jobs = get_adzuna_jobs(skills, location)
        all_jobs.extend(adzuna_jobs)
        print(f"Fetched {len(adzuna_jobs)} jobs from Adzuna")
    except Exception as e:
        print(f"Error fetching from Adzuna: {e}")
    
    # Fetch from JSearch
    try:
        jsearch_jobs = get_jsearch_jobs(skills, location)
        all_jobs.extend(jsearch_jobs)
        print(f"Fetched {len(jsearch_jobs)} jobs from JSearch")
    except Exception as e:
        print(f"Error fetching from JSearch: {e}")
    
    # Fetch from RemoteOK
    try:
        remoteok_jobs = get_remoteok_jobs(skills)
        all_jobs.extend(remoteok_jobs)
        print(f"Fetched {len(remoteok_jobs)} jobs from RemoteOK")
    except Exception as e:
        print(f"Error fetching from RemoteOK: {e}")
    
    # Remove duplicates based on title and company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job.get('title', '').lower(), job.get('company', {}).get('display_name', '').lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"Total unique jobs: {len(unique_jobs)}")
    return unique_jobs

def calculate_ats_score(text, skills):
    """
    Calculates a heuristic ATS score based on resume content.
    Also generates missing keywords and professional summary.
    """
    score = 0
    breakdown = {
        "strengths": [],
        "weaknesses": [],
        "missing_keywords": []
    }
    
    text_lower = text.lower()
    
    # 1. Content Length (10 points)
    word_count = len(text.split())
    if 200 <= word_count <= 2000:
        score += 10
        breakdown["strengths"].append("Optimal resume length")
    else:
        breakdown["weaknesses"].append("Resume length is outside optimal range (200-2000 words)")

    # 2. Contact Info Check (20 points)
    has_email = "@" in text
    # Simple digit check for phone, can be improved with regex
    has_phone = sum(c.isdigit() for c in text) > 9 
    
    if has_email:
        score += 10
        breakdown["strengths"].append("Email address detected")
    else:
        breakdown["weaknesses"].append("Missing email address")
        
    if has_phone:
        score += 10
        breakdown["strengths"].append("Phone number detected")
    else:
        breakdown["weaknesses"].append("Missing phone number")

    # 3. Key Sections Check (30 points)
    sections = ["experience", "education", "skills", "summary", "projects"]
    found_sections = [s for s in sections if s in text_lower]
    
    score += (len(found_sections) / len(sections)) * 30
    
    if len(found_sections) == len(sections):
        breakdown["strengths"].append("All key sections detected")
    else:
        missing = [s.title() for s in sections if s not in text_lower]
        breakdown["weaknesses"].append(f"Missing sections: {', '.join(missing)}")

    # 4. Skills/Keywords (40 points)
    # Based on number of skills found relative to a 'good' baseline
    # Let's say detecting 5+ skills is 'good'
    skill_count = len(skills)
    if skill_count >= 5:
        score += 40
        breakdown["strengths"].append(f"Strong skill presence ({skill_count} skills detected)")
    elif skill_count > 0:
        score += (skill_count / 5) * 40
        breakdown["weaknesses"].append("Could add more relevant technical skills")
    else:
         breakdown["weaknesses"].append("No technical skills detected")
    
    # 5. Generate Missing Keywords - Enhanced with role-specific suggestions
    # Detect role from resume
    detected_role = None
    common_roles = {
        "developer": ["python", "javascript", "react", "node.js", "api", "git", "docker", "aws", "ci/cd", "testing"],
        "engineer": ["system design", "architecture", "scalability", "microservices", "kubernetes", "devops"],
        "data": ["sql", "python", "machine learning", "pandas", "visualization", "statistics", "big data"],
        "manager": ["leadership", "stakeholder management", "agile", "scrum", "roadmap", "kpis", "budgeting"],
        "designer": ["ui/ux", "figma", "adobe", "wireframing", "prototyping", "user research", "design systems"],
        "analyst": ["excel", "sql", "data analysis", "reporting", "dashboards", "business intelligence"],
        "marketing": ["seo", "sem", "content marketing", "analytics", "campaign management", "social media"]
    }
    
    # Detect role from text
    for role, keywords in common_roles.items():
        if role in text_lower:
            detected_role = role
            break
    
    # Common industry keywords that should be in most resumes
    RECOMMENDED_KEYWORDS = {
        "technical": ["agile", "scrum", "ci/cd", "devops", "cloud", "api", "testing", "debugging", 
                     "version control", "git", "collaboration", "problem-solving"],
        "soft_skills": ["leadership", "communication", "teamwork", "analytical", "creative", 
                       "detail-oriented", "time management", "adaptable", "strategic thinking"],
        "achievements": ["improved", "increased", "reduced", "developed", "implemented", 
                        "designed", "optimized", "achieved", "led", "managed", "delivered"]
    }
    
    missing_keywords = []
    
    # First, add role-specific keywords if role detected
    if detected_role and detected_role in common_roles:
        role_keywords = common_roles[detected_role]
        for keyword in role_keywords:
            if keyword not in text_lower and len(missing_keywords) < 10:
                missing_keywords.append(keyword.title())
    
    # Then add general keywords
    for category, keywords in RECOMMENDED_KEYWORDS.items():
        for keyword in keywords:
            if keyword not in text_lower and len(missing_keywords) < 15:  # Limit to 15 suggestions
                # Avoid duplicates
                if keyword.title() not in missing_keywords:
                    missing_keywords.append(keyword.title())
    
    # If still no keywords found, add some default important ones
    if len(missing_keywords) == 0:
        default_keywords = ["Leadership", "Communication", "Problem-Solving", "Teamwork", 
                          "Project Management", "Analytical", "Strategic Thinking", "Innovation"]
        missing_keywords = default_keywords[:8]
    
    breakdown["missing_keywords"] = missing_keywords
    
    # 6. Generate Professional Summary
    summary = generate_professional_summary(text, skills)
    breakdown["professional_summary"] = summary

    return int(score), breakdown

def generate_professional_summary(text, skills):
    """
    Generates a professional summary based on resume content.
    """
    text_lower = text.lower()
    
    # Detect experience level
    years_exp = 0
    if "years" in text_lower or "year" in text_lower:
        # Try to extract years of experience
        import re
        year_matches = re.findall(r'(\d+)\s*(?:\+)?\s*years?', text_lower)
        if year_matches:
            years_exp = max([int(y) for y in year_matches])
    
    # Determine experience level
    if years_exp >= 7:
        level = "Senior"
    elif years_exp >= 3:
        level = "Mid-level"
    elif years_exp >= 1:
        level = "Junior"
    else:
        level = "Entry-level"
    
    # Detect role/title (simple heuristic)
    common_roles = ["developer", "engineer", "designer", "manager", "analyst", "scientist", 
                   "architect", "consultant", "specialist", "administrator"]
    detected_role = "Professional"
    for role in common_roles:
        if role in text_lower:
            detected_role = role.title()
            break
    
    # Build summary
    summary_parts = []
    
    # Opening
    if years_exp > 0:
        summary_parts.append(f"{level} {detected_role} with {years_exp}+ years of experience")
    else:
        summary_parts.append(f"{level} {detected_role}")
    
    # Skills
    if len(skills) > 0:
        top_skills = skills[:5]  # Top 5 skills
        skills_str = ", ".join(top_skills[:-1]) + f" and {top_skills[-1]}" if len(top_skills) > 1 else top_skills[0]
        summary_parts.append(f"specializing in {skills_str}")
    
    # Achievements/Focus
    focus_areas = []
    if "project" in text_lower or "projects" in text_lower:
        focus_areas.append("project delivery")
    if "team" in text_lower or "collaboration" in text_lower:
        focus_areas.append("team collaboration")
    if "client" in text_lower or "customer" in text_lower:
        focus_areas.append("client satisfaction")
    
    if focus_areas:
        focus_str = " and ".join(focus_areas)
        summary_parts.append(f"with a proven track record in {focus_str}")
    
    # Closing
    summary_parts.append("Seeking opportunities to leverage technical expertise and drive innovative solutions in a dynamic environment.")
    
    # Combine
    summary = ". ".join(summary_parts) + "."
    
    return summary

