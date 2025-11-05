# 🧠 ResumeMatch – AI-Powered Internship Recommendation System
**ResumeMatch** is a web-application that helps students and job seekers find **personalized internship opportunities** by analyzing their uploaded resume.
The system uses **AI-based semantic matching** (ready for future Gemini/LLM integration) to recommend the most relevant internships based on skills, education, and experience.
---
## 🌟 Features
- 📄 **Resume Upload** – Upload your resume (`.pdf`, `.docx`, `.txt`) to automatically extract key information.
- ⚙️ **AI-Based Recommendations** – Receive internship suggestions based on extracted skills and summary.
- 💼 **Internship Cards** – Modern, clean display of each recommended internship.
- 🧭 **Smooth Navigation** – Simple and intuitive 3-page flow:
`Home → Upload Resume → Recommendations`.
- 🎨 **Responsive UI** – Built using **React + TailwindCSS** for a sleek, consistent design.
- 🧠 **Mock API Ready** – Uses simulated API responses (`src/utils/api.js`) so you can preview the full flow without a backend.
---

##💡 How It Works (Flow)
- **Upload Resume**:
The user uploads a .pdf, .docx, or .txt resume.
(Simulated parsing handled by parseResume() in api.js.)
- **Extract Resume Data**:
The system extracts a mock summary, skills, and experience.
- **Generate Recommendations**:
The frontend calls getRecommendations() (mock API) to fetch relevant internships.
- **Display Results**:
Recommendations are shown in interactive cards with:
Title, Company, Location
Stipend, Duration
Match Score (%)
Reason for Recommendation
