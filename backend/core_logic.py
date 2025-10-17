import os
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from models import Job

# Initialize embeddings model (singleton pattern)
_embeddings = None
_vectorstore = None

def get_embeddings():
    """Get or initialize embeddings model"""
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            print("✅ Hugging Face Embeddings Model loaded.")
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            raise
    return _embeddings

def initialize_vectorstore_from_db():
    """Initialize vector store from database jobs"""
    global _vectorstore
    
    try:
        embeddings = get_embeddings()
        
        # Get all jobs from database
        jobs = Job.query.all()
        
        if not jobs:
            print("⚠️ No jobs found in database")
            return None
        
        print(f"📊 Loading {len(jobs)} jobs into vector store...")
        
        # Create documents
        docs = []
        for job in jobs:
            content = (
                f"Title: {job.internship_title}\n"
                f"Company: {job.company_name}\n"
                f"Description: {job.full_description}\n"
                f"Skills: {job.required_skills}"
            )
            doc = Document(
                page_content=content,
                metadata={
                    "id": job.id,
                    "internship_title": job.internship_title,
                    "company_name": job.company_name,
                    "location": job.location,
                    "full_description": job.full_description,
                    "required_skills": job.required_skills,
                    "stipend_inr": job.stipend_inr,
                    "duration_months": job.duration_months,
                }
            )
            docs.append(doc)
        
        # Create vector store
        _vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=None
        )
        print("✅ Vector store created successfully.")
        return _vectorstore
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        raise

def get_vectorstore():
    """Get or initialize vector store"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = initialize_vectorstore_from_db()
    return _vectorstore

def get_job_recommendations(resume_summary_data, top_n=10):
    """
    Get job recommendations based on resume summary using semantic search
    
    Args:
        resume_summary_data: Dictionary containing parsed resume information
        top_n: Number of recommendations to return
    
    Returns:
        List of recommended jobs with similarity scores
    """
    try:
        vectorstore = get_vectorstore()
        
        if vectorstore is None:
            return {"error": "Vector store not initialized"}
        
        # Build resume text for search
        resume_text_parts = []
        
        # Add AI summary if available
        if resume_summary_data.get('ai_summary'):
            resume_text_parts.append(resume_summary_data['ai_summary'])
        
        # Add skills
        if resume_summary_data.get('skills'):
            skills_text = "Skills: " + ", ".join(resume_summary_data['skills'])
            resume_text_parts.append(skills_text)
        
        # Add experience
        if resume_summary_data.get('experience'):
            for exp in resume_summary_data['experience'][:3]:  # Top 3 experiences
                exp_text = f"Experience: {exp.get('title', '')} at {exp.get('company', '')}"
                if exp.get('bullets'):
                    exp_text += " - " + " ".join(exp['bullets'][:2])
                resume_text_parts.append(exp_text)
        
        # Add projects
        if resume_summary_data.get('projects'):
            for proj in resume_summary_data['projects'][:2]:  # Top 2 projects
                proj_text = f"Project: {proj.get('title', '')}"
                if proj.get('bullets'):
                    proj_text += " - " + " ".join(proj['bullets'][:2])
                resume_text_parts.append(proj_text)
        
        # Add education
        if resume_summary_data.get('education'):
            for edu in resume_summary_data['education'][:2]:
                edu_text = f"Education: {edu.get('degree', '')} from {edu.get('institution', '')}"
                resume_text_parts.append(edu_text)
        
        # Combine all parts
        resume_text = "\n".join(resume_text_parts)
        
        if not resume_text.strip():
            resume_text = "Looking for internship opportunities"
        
        print(f"🔍 Searching with resume text (length: {len(resume_text)} chars)")
        
        # Perform semantic search with scores
        matched_docs_and_scores = vectorstore.similarity_search_with_score(resume_text, k=top_n)
        
        print(f"✅ Found {len(matched_docs_and_scores)} matches")
        
        # Build recommendations
        recommendations = []
        for doc, score in matched_docs_and_scores:
            meta = doc.metadata
            
            # Get the full job object from database for complete data
            job = Job.query.get(meta.get('id'))
            if job:
                job_dict = job.to_dict()
                # Convert distance score to similarity percentage (lower distance = higher similarity)
                # Chroma returns L2 distance, so we invert it
                similarity_percentage = max(0, min(100, (1 - score) * 100))
                job_dict['similarity_score'] = round(similarity_percentage, 2)
                job_dict['raw_distance'] = round(float(score), 4)
                recommendations.append(job_dict)
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error in recommendation logic: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def reinitialize_vectorstore():
    """Force reinitialize vector store (useful after database updates)"""
    global _vectorstore
    _vectorstore = None
    return initialize_vectorstore_from_db()