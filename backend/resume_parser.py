import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from difflib import get_close_matches

# Attempt to import external libraries
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None

try:
    import phonenumbers
except ImportError:
    phonenumbers = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Import config for API key
from config import Config

# ---------------------------
# Config / Mini knowledge base
# ---------------------------
HEADINGS = [
    "education", "education and qualifications", "academic qualifications", "academics",
    "experience", "work experience", "professional experience", "employment history",
    "skills", "technical skills", "expertise",
    "projects", "personal projects", "achievements",
    "certifications", "certificates",
    "summary", "objective", "professional summary"
]

SKILLS_MASTER = [
    "python", "java", "c++", "javascript", "react", "nodejs", "django", "flask",
    "sql", "mongodb", "postgresql", "aws", "azure", "gcp", "docker", "kubernetes",
    "data science", "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "html", "css",
    "spring", "hibernate", "git", "linux", "bash", "rest", "api", "microservices",
    "spark", "hadoop", "etl", "tableau", "power bi", "fastapi", "selenium",
    "android", "ios", "swift", "kotlin", "reactjs", "nodejs", "vuejs", "angular"
]

COMMON_CITIES = [
    "bengaluru", "bangalore", "mumbai", "delhi", "new delhi", "chennai", "hyderabad", "pune", "kolkata",
    "gurgaon", "noida", "greater noida", "kochi", "thiruvananthapuram", "ahmedabad", "jaipur", "lucknow"
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.I)
DURATION_PATTERN = r"\(([^)]*(?:20\d{2}|Present|current)[^)]*)\)"


def _extract_text_from_pdf(p: Path) -> str:
    if pdfplumber is None:
        print("⚠️ pdfplumber not installed. Cannot parse PDF.")
        return ""
    text = []
    with pdfplumber.open(str(p)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text.append(t)
    return "\n".join(text)

def _extract_text_from_docx(p: Path) -> str:
    if docx is None:
        print("⚠️ python-docx not installed. Cannot parse DOCX.")
        return ""
    doc = docx.Document(str(p))
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs)

def _extract_text_from_txt(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def _extract_text(path_str: str) -> str:
    p = Path(path_str)
    if not p.exists():
        raise FileNotFoundError(f"Resume file not found: {p}")
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return _extract_text_from_pdf(p)
    elif suffix in (".docx", ".doc"):
        return _extract_text_from_docx(p)
    elif suffix in (".txt",):
        return _extract_text_from_txt(p)
    else:
        try:
            return _extract_text_from_txt(p)
        except Exception:
            raise RuntimeError(f"Unsupported file type or read error: {suffix}")

def _find_heading_positions(text: str) -> List[Dict]:
    lines = text.splitlines()
    positions = []
    for idx, line in enumerate(lines):
        normalized = re.sub(r'[^a-zA-Z ]', ' ', line).strip().lower()
        for h in HEADINGS:
            if normalized.startswith(h):
                positions.append({"heading": h, "line_index": idx, "raw_heading": line.strip()})
                break
    return positions

def _segment_by_headings(text: str) -> Dict[str, str]:
    lines = text.splitlines()
    headings = _find_heading_positions(text)
    if not headings:
        return {"summary": text.strip()}

    sections = {}
    for i, item in enumerate(headings):
        start = item["line_index"]
        end = headings[i + 1]["line_index"] if i + 1 < len(headings) else len(lines)
        section_text = "\n".join(lines[start:end]).strip()
        sections[item["heading"]] = section_text

    first_idx = headings[0]["line_index"]
    if first_idx > 0:
        summary = "\n".join(lines[:first_idx]).strip()
        if summary:
            sections.setdefault("summary", summary)
    return sections

def _extract_emails(text: str) -> List[str]:
    return list({m.group(0).strip() for m in EMAIL_RE.finditer(text)})

def _extract_phones(text: str) -> List[str]:
    if phonenumbers is None:
        fallback = re.findall(r"(?:\+?91[\-\s]?)?[6-9]\d{9}", text)
        return list(set(fallback))
    phones = []
    for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
        phones.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    return list(dict.fromkeys(phones))

def _extract_name_candidate(text: str, emails: List[str]) -> Optional[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        first = lines[0]
        if 1 <= len(first.split()) <= 4 and any(c.isalpha() for c in first):
            return first
    if emails:
        local = emails[0].split("@")[0]
        local = re.sub(r"[\.\_\-\d]+", " ", local).strip()
        return " ".join([w.capitalize() for w in local.split() if w])
    return None

def _extract_education(text: str) -> List[Dict]:
    lines = text.splitlines()
    education_entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.search(r"(B\.?\s?Tech|Intermediate|Bachelor|Master|B\.?Sc|M\.?Tech)", line, re.I):
            degree_line = line
            if i + 1 < len(lines):
                inst_line = lines[i + 1].strip()
                cgpa_match = re.search(r"[\d\.]+(?:\s?CGPA|%|percent)", degree_line, re.I)
                cgpa = cgpa_match.group(0) if cgpa_match else None
                
                year_match = re.search(r"\(([^)]*(?:20\d{2}|Present)[^)]*)\)", inst_line)
                if not year_match:
                     year_match = re.search(r"\(([^)]*(?:20\d{2}|Present)[^)]*)\)", degree_line)
                
                year = year_match.group(1) if year_match else None
                institution = re.sub(r"\s*\([^)]*\)\s*$", "", inst_line).strip()
                
                education_entries.append({
                    "degree": degree_line,
                    "institution": institution,
                    "cgpa_or_percentage": cgpa,
                    "duration": year
                })
                i += 2
                continue
        i += 1
    return education_entries

def _split_experience_blocks(section_text: str) -> List[Dict]:
    lines = [ln.strip() for ln in section_text.splitlines() if ln.strip()]
    blocks = []
    current_role = None
    current_bullets = []

    for ln in lines:
        is_new_role = re.search(r"(Intern|Engineer|Developer|Analyst|Manager|Researcher)", ln, re.I) and re.search(DURATION_PATTERN, ln)
        
        if is_new_role:
            if current_role:
                blocks.append({
                    "role_line": current_role,
                    "bullets": current_bullets
                })
            current_role = ln
            current_bullets = []
        elif ln.startswith(("•", "-", "*")):
            bullet = ln.lstrip("•-* ").strip()
            current_bullets.append(bullet)
        else:
            if current_bullets:
                current_bullets[-1] += " " + ln.strip()
            elif current_role:
                current_role += " " + ln.strip()

    if current_role:
        blocks.append({
            "role_line": current_role,
            "bullets": current_bullets
        })

    return blocks

def _extract_experience(section_text: str) -> List[Dict]:
    blocks = _split_experience_blocks(section_text)
    exps = []

    for block in blocks:
        role_line = block["role_line"]
        bullets = block["bullets"]

        title, company, duration = None, None, None

        dur_match = re.search(r"\(([^)]+)\)", role_line)
        if dur_match:
            duration = dur_match.group(1)
            role_line = role_line.replace(f"({duration})", "").strip()

        if " – " in role_line:
            parts = role_line.split(" – ", 1)
            title = parts[0].strip()
            company = parts[1].strip()
        elif " - " in role_line:
            parts = role_line.split(" - ", 1)
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            title = role_line.strip()
            company = None

        if company and (',' in company or '|' in company):
            company = company.split(',')[0].split('|')[0].strip()

        exps.append({
            "title": title or "N/A",
            "company": company or "N/A",
            "duration": duration,
            "bullets": bullets
        })

    return exps

def _extract_projects(section_text: str) -> List[Dict]:
    lines = [ln.strip() for ln in section_text.splitlines() if ln.strip()]
    projects = []
    current_proj = None

    for ln in lines:
        if re.match(r"^\d+\.", ln) or re.match(r"^[A-Z][a-zA-Z\s]+:", ln):
            if current_proj:
                projects.append(current_proj)
            title = ln.split(':')[0].strip() if ':' in ln else ln.strip()
            description = ln.split(':', 1)[1].strip() if ':' in ln else ""
            current_proj = {"title": title, "bullets": []}
            if description:
                 current_proj["bullets"].append(description)
        elif ln.startswith(("•", "-", "*")):
            if current_proj is not None:
                bullet = ln.lstrip("•-* ").strip()
                current_proj["bullets"].append(bullet)
        else:
            if current_proj:
                if current_proj["bullets"]:
                    current_proj["bullets"][-1] += " " + ln.strip()
                else:
                    current_proj["title"] += " " + ln.strip()

    if current_proj:
        projects.append(current_proj)

    return projects

def _extract_skills(text: str, master_list: List[str]=SKILLS_MASTER, cutoff=0.8) -> List[str]:
    text_lower = text.lower()
    found = set()
    
    for skill in master_list:
        if skill.lower() in text_lower:
            found.add(skill)

    words = re.findall(r"[a-zA-Z\+\#\.\-]{2,}", text_lower)
    uniq = sorted(set(words), key=lambda x: -len(x))
    for w in uniq:
        matches = get_close_matches(w, master_list, n=3, cutoff=cutoff)
        for m in matches:
            found.add(m)

    tech_patterns = re.findall(r"(React\.js|Node\.js|Next\.js|MongoDB|PostgreSQL|MySQL|Firebase|TensorFlow|PyTorch|scikit-learn)", text, re.I)
    for tp in tech_patterns:
        clean = tp.lower().replace('.js', '').capitalize()
        found.add(clean)

    return sorted(found)

def _guess_location(text: str) -> Optional[str]:
    t = text.lower()
    for city in COMMON_CITIES:
        if city in t:
            return city.title()
    if "india" in t:
        return "India"
    return None

def _generate_ai_summary(parsed_data: Dict) -> str:
    if genai is None:
        return "[Gemini not available - google-generativeai not installed]"

    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        name = parsed_data.get("name", "the candidate")
        experience_lines = [
            f"{exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
            for exp in parsed_data.get('experience', [])
        ]
        skills = ", ".join(parsed_data.get("skills", []))
        projects_titles = [
            proj.get('title', '').split('.')[0].strip()
            for proj in parsed_data.get('projects', [])
        ]

        prompt = f"""
You are a professional resume editor. Write a 2-3 sentence personal summary in **first person** for the candidate's resume header.

**Style:** Natural, confident, concise. Like a LinkedIn bio or resume profile.
**Focus:** Highlight key skills, experiences, and career goals.
**Avoid:** Buzzwords like "passionate", "hardworking", "team player". Be specific.

**Candidate Info:**
Name: {name}
Key Skills: {skills}
Recent Experience: {"; ".join(experience_lines[:2])}
Projects: {"; ".join(projects_titles[:2])}

**Goal:** Generate a profile summary for this candidate's resume.
"""
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"[Error generating AI summary: {str(e)}]"


def parse_resume(file_path: str) -> Dict:
    """
    Main function to parse resume and extract structured data
    
    Args:
        file_path: Path to the resume file
    
    Returns:
        Dictionary containing parsed resume data
    """
    try:
        text = _extract_text(file_path)
    except Exception as e:
        print(f"❌ Error during text extraction: {e}")
        return {"error": str(e)}
    
    sections = _segment_by_headings(text)

    emails = _extract_emails(text)
    phones = _extract_phones(text)
    name = _extract_name_candidate(text, emails)

    skills_text = ""
    for k in ("skills", "technical skills", "expertise"):
        if k in sections:
            skills_text = sections[k]
            break
    if not skills_text:
        skills_text = text

    education, experience, projects = [], [], []
    for k, v in sections.items():
        if "education" in k:
            education.extend(_extract_education(v))
        elif "experience" in k or "employment" in k or "work" in k:
            experience.extend(_extract_experience(v))
        elif "project" in k:
            projects.extend(_extract_projects(v))

    if not education:
        education.extend(_extract_education(text))
    if not experience:
        experience.extend(_extract_experience(text))

    skills = _extract_skills(skills_text)

    parsed = {
        "name": name,
        "contact": {
            "emails": emails,
            "phones": phones
        },
        "location_guess": _guess_location(text),
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": skills,
        "raw_sections": {k: (v[:800] + "..." if len(v) > 800 else v) for k, v in sections.items()},
        "ai_summary": ""
    }

    parsed["ai_summary"] = _generate_ai_summary(parsed)

    # Save to JSON file
    output_path = Path(file_path).with_suffix('.json')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully saved parsed resume to: {output_path}")
    except Exception as e:
        print(f"❌ Error writing JSON file: {e}")

    return parsed