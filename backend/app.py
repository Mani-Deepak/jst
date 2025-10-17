from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Job, User
from config import Config
from resume_parser import parse_resume
from csv_importer import import_jobs_from_csv, get_import_status
from core_logic import get_job_recommendations, initialize_vectorstore_from_db, get_vectorstore
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": "*"}})

db.init_app(app)

with app.app_context():
    db.create_all()
    # Check if jobs exist, if not, import from CSV
    if get_import_status() == 0:
        print("No jobs found in database, importing from CSV...")
        import_jobs_from_csv()
    else:
        print(f"{get_import_status()} jobs already in database.")
    
    # Initialize the vector store on app startup
    initialize_vectorstore_from_db()
    print("Application context initialized.")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Job Recommender API!"})

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = Job.query.paginate(page=page, per_page=per_page, error_out=False)
        
        jobs = [job.to_dict() for job in pagination.items]
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get specific job by ID"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        return jsonify({'success': True, 'job': job.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    """Search jobs by title, company, or skills"""
    try:
        query = request.args.get('q', '', type=str)
        
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400
        
        jobs = Job.query.filter(
            db.or_(
                Job.internship_title.ilike(f'%{query}%'),
                Job.company_name.ilike(f'%{query}%'),
                Job.required_skills.ilike(f'%{query}%')
            )
        ).all()
        
        return jsonify({'success': True, 'jobs': [job.to_dict() for job in jobs]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def recommend_jobs():
    """Upload resume, parse it, and get job recommendations"""
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No resume file part'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            print(f"Resume saved to {filepath}")
            
            # Parse resume
            parsed_resume_data = parse_resume(filepath)
            
            if "error" in parsed_resume_data:
                return jsonify({'success': False, 'error': parsed_resume_data["error"]}), 500
            
            # Get recommendations
            recommendations = get_job_recommendations(parsed_resume_data)
            
            return jsonify({
                'success': True,
                'parsed_resume': parsed_resume_data,
                'recommendations': recommendations
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/profile', methods=['GET', 'POST'])
def user_profile():
    """Get or update user profile"""
    try:
        user_id = request.args.get('user_id', type=int) # Assuming user_id for simplicity, in real app use auth token
        
        if request.method == 'GET':
            if not user_id:
                return jsonify({'success': False, 'error': 'User ID is required for GET request'}), 400
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            return jsonify({'success': True, 'profile': user.to_dict()})
            
        elif request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'Request body must be JSON'}), 400

            user = None
            if user_id:
                user = User.query.get(user_id)
            elif data.get('email'): # Try to find user by email if no ID provided
                user = User.query.filter_by(email=data['email']).first()

            if user: # Update existing user
                user.name = data.get('name', user.name)
                user.email = data.get('email', user.email)
                user.phone = data.get('phone', user.phone)
                user.skills = json.dumps(data.get('skills', []))
                user.experience = json.dumps(data.get('experience', []))
                user.education = json.dumps(data.get('education', []))
                # resume_path not updated via this endpoint, only via resume upload
            else: # Create new user
                user = User(
                    name=data.get('name'),
                    email=data.get('email'),
                    phone=data.get('phone'),
                    skills=json.dumps(data.get('skills', [])),
                    experience=json.dumps(data.get('experience', [])),
                    education=json.dumps(data.get('education', []))
                )
                db.session.add(user)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile updated/created successfully', 'profile': user.to_dict()}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        job_count = get_import_status()
        user_count = User.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_jobs': job_count,
                'total_users': user_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/import-jobs', methods=['POST'])
def admin_import_jobs():
    """Manually trigger CSV job import"""
    try:
        result = import_jobs_from_csv()
        if result:
            return jsonify({'success': True, 'message': 'Jobs imported successfully and vector store reinitialized'})
        else:
            return jsonify({'success': False, 'error': 'Failed to import jobs from CSV'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)