import pandas as pd
from models import db, Job
from config import Config

def import_jobs_from_csv(csv_path=None):
    """Import jobs from CSV file into database"""
    if csv_path is None:
        csv_path = Config.CSV_FILE
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_path, encoding="utf-8").fillna("N/A")
        
        print(f"Found {len(df)} jobs in CSV file")
        
        # Clear existing jobs (optional - remove if you want to keep existing data)
        Job.query.delete()
        
        # Import each job
        imported_count = 0
        for index, row in df.iterrows():
            try:
                job = Job(
                    internship_title=str(row.get('internship_title', '')),
                    company_name=str(row.get('company_name', '')),
                    location=str(row.get('location', '')),
                    full_description=str(row.get('full_description', '')),
                    required_skills=str(row.get('required_skills', '')),
                    stipend_inr=str(row.get('stipend_inr', '')),
                    duration_months=str(row.get('duration_months', ''))
                )
                db.session.add(job)
                imported_count += 1
                
                # Commit in batches of 100
                if imported_count % 100 == 0:
                    db.session.commit()
                    print(f"Imported {imported_count} jobs...")
                    
            except Exception as e:
                print(f"Error importing row {index}: {e}")
                continue
        
        # Final commit
        db.session.commit()
        print(f"Successfully imported {imported_count} jobs!")
        
        # Reinitialize vector store after import
        from core_logic import reinitialize_vectorstore
        reinitialize_vectorstore()
        print("✅ Vector store reinitialized with new data!")
        
        return True
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        db.session.rollback()
        return False

def get_import_status():
    """Check how many jobs are in database"""
    count = Job.query.count()
    return count