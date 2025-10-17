import React, { useState } from 'react';
import { Upload, Briefcase, ArrowRight, Star, ExternalLink, TrendingUp, User, Mail, Phone, MapPin, GraduationCap, Award, Edit2, Check, X } from 'lucide-react';

// =================================================================================
// PAGE COMPONENTS
// =================================================================================

const HomePage = ({ allInternships, setCurrentPage }) => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <nav className="bg-white shadow-sm border-b"><div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4"><div className="flex justify-between items-center"><div className="flex items-center space-x-2"><Briefcase className="w-8 h-8 text-blue-600" /><h1 className="text-2xl font-bold text-gray-800">CareerMatch</h1></div><div className="flex items-center space-x-4"><button onClick={() => setCurrentPage('profile')} className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 font-medium transition-colors"><User className="w-5 h-5" /><span>Profile</span></button><button onClick={() => setCurrentPage('recommendations')} className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-sm"><TrendingUp className="w-5 h-5" /><span>Get Recommendations</span><ArrowRight className="w-4 h-4" /></button></div></div></div></nav>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"><div className="text-center mb-12"><h2 className="text-4xl font-bold text-gray-900 mb-4">Available Internships</h2><p className="text-lg text-gray-600">Explore exciting opportunities to kickstart your career</p></div><div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{allInternships.map((internship) => (<div key={internship.id} className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow p-6 border border-gray-100"><div className="flex items-start justify-between mb-4"><div className="bg-blue-100 p-3 rounded-lg"><Briefcase className="w-6 h-6 text-blue-600" /></div><span className="text-sm font-semibold text-green-600 bg-green-50 px-3 py-1 rounded-full">{internship.stipend}</span></div><h3 className="text-xl font-bold text-gray-900 mb-2">{internship.title}</h3><p className="text-gray-600 font-medium mb-1">{internship.company}</p><p className="text-sm text-gray-500 mb-4">{internship.location} • {internship.duration}</p><p className="text-gray-700 text-sm mb-4 line-clamp-2">{internship.description}</p><div className="flex flex-wrap gap-2 mb-4">{internship.skills.slice(0, 3).map((skill, idx) => (<span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">{skill}</span>))}</div><button className="w-full bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 transition-colors font-medium">View Details</button></div>))}</div></div>
    </div>
);

const RecommendationsPage = ({ setCurrentPage, setUploadedFile, setRecommendations, uploadedFile, isProcessing, recommendations, handleFileUpload, getMatchColor }) => (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
        <nav className="bg-white shadow-sm border-b"><div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4"><div className="flex justify-between items-center"><button onClick={() => { setCurrentPage('home'); setUploadedFile(null); setRecommendations([]); }} className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"><ArrowRight className="w-5 h-5 rotate-180" /><span>Back to Home</span></button><div className="flex items-center space-x-2"><Briefcase className="w-8 h-8 text-blue-600" /><h1 className="text-2xl font-bold text-gray-800">CareerMatch</h1></div><button onClick={() => setCurrentPage('profile')} className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 font-medium transition-colors"><User className="w-5 h-5" /><span>Profile</span></button></div></div></nav>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">{!uploadedFile ? (<div className="text-center"><div className="bg-white rounded-2xl shadow-xl p-12 border-2 border-dashed border-gray-300"><Upload className="w-20 h-20 text-blue-600 mx-auto mb-6" /><h2 className="text-3xl font-bold text-gray-900 mb-4">Get Personalized Recommendations</h2><p className="text-gray-600 mb-8 text-lg">Upload your resume to receive AI-powered internship matches</p><label className="inline-block cursor-pointer"><input type="file" accept=".pdf" onChange={handleFileUpload} className="hidden" /><div className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg shadow-lg">Upload Resume (PDF)</div></label><p className="text-sm text-gray-500 mt-4">We analyze your skills, experience, and preferences</p></div></div>) : isProcessing ? (<div className="text-center bg-white rounded-2xl shadow-xl p-12"><div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-6"></div><h3 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Your Resume</h3><p className="text-gray-600">Parsing skills, experience, and matching with opportunities...</p></div>) : (<div><div className="text-center mb-8"><h2 className="text-3xl font-bold text-gray-900 mb-2">Your Top Matches</h2><p className="text-gray-600">Based on your resume analysis</p></div><div className="space-y-6">
            {/* START: THIS IS THE RESTORED CODE BLOCK */}
            {recommendations.map((rec, index) => (
                <div key={rec.id} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all p-6 border-l-4 border-blue-600">
                    <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center space-x-3">
                            <div className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg">#{index + 1}</div>
                            <div>
                                <h3 className="text-2xl font-bold text-gray-900">{rec.title}</h3>
                                <p className="text-gray-600 font-medium">{rec.company}</p>
                            </div>
                        </div>
                        <div className={`${getMatchColor(rec.matchScore)} px-4 py-2 rounded-lg flex items-center space-x-2`}>
                            <Star className="w-5 h-5" fill="currentColor" />
                            <span className="font-bold text-lg">{rec.matchScore}% Match</span>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                        <div><span className="text-gray-500">Location:</span><span className="ml-2 font-medium text-gray-900">{rec.location}</span></div>
                        <div><span className="text-gray-500">Duration:</span><span className="ml-2 font-medium text-gray-900">{rec.duration}</span></div>
                        <div><span className="text-gray-500">Stipend:</span><span className="ml-2 font-medium text-green-600">{rec.stipend}</span></div>
                    </div>
                    <p className="text-gray-700 mb-4">{rec.description}</p>
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded">
                        <p className="text-sm font-semibold text-blue-900 mb-1">Why This Match?</p>
                        <p className="text-sm text-blue-800">{rec.reason}</p>
                    </div>
                    <div className="flex flex-wrap gap-2 mb-4">
                        {rec.skills.map((skill, idx) => (<span key={idx} className="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full font-medium">{skill}</span>))}
                    </div>
                    <button onClick={() => window.open(rec.applicationUrl, '_blank')} className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold flex items-center justify-center space-x-2 shadow-md">
                        <span>Apply Now</span><ExternalLink className="w-5 h-5" />
                    </button>
                </div>
            ))}
            {/* END: RESTORED CODE BLOCK */}
            </div><div className="text-center mt-8"><button onClick={() => { setUploadedFile(null); setRecommendations([]); }} className="text-blue-600 hover:text-blue-700 font-medium">Upload a different resume</button></div></div>)}</div>
    </div>
);

const ProfilePage = ({ setCurrentPage, isEditing, setIsEditing, userProfile, editableProfile, handleSave, handleCancel, handleProfileChange, handleSkillsChange }) => (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <button onClick={() => setCurrentPage('home')} className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
              <ArrowRight className="w-5 h-5 rotate-180" />
              <span>Back to Home</span>
            </button>
            <div className="flex items-center space-x-2">
              <User className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-800">My Profile</h1>
            </div>
            <div className="w-36"></div> {/* Spacer */}
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-xl border p-8">
          <div className="flex justify-between items-start mb-8 pb-8 border-b">
            <div>
              {isEditing ? (<input type="text" name="name" value={editableProfile.name} onChange={handleProfileChange} className="text-4xl font-bold text-gray-900 border-b-2 border-blue-300 focus:border-blue-500 outline-none w-full" />) : (<h2 className="text-4xl font-bold text-gray-900">{userProfile.name}</h2>)}
              <div className="flex items-center text-lg text-gray-500 mt-2">
                <MapPin className="w-5 h-5 mr-2" />
                {isEditing ? (<input type="text" name="location" value={editableProfile.location} onChange={handleProfileChange} className="border-b w-full" />) : (<span>{userProfile.location}</span>)}
              </div>
            </div>
            {isEditing ? (
              <div className="flex space-x-2">
                <button onClick={handleSave} className="flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-all"><Check className="w-4 h-4" /><span>Save</span></button>
                <button onClick={handleCancel} className="flex items-center space-x-2 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-all"><X className="w-4 h-4" /><span>Cancel</span></button>
              </div>
            ) : (<button onClick={() => setIsEditing(true)} className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-all"><Edit2 className="w-4 h-4" /><span>Edit Profile</span></button>)}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="flex items-center space-x-4"><Mail className="w-8 h-8 text-blue-500 flex-shrink-0" /><div><p className="text-sm text-gray-500">Email</p>{isEditing ? <input type="email" name="email" value={editableProfile.email} onChange={handleProfileChange} className="font-medium text-gray-800 border-b w-full" /> : <p className="font-medium text-gray-800">{userProfile.email}</p>}</div></div>
            <div className="flex items-center space-x-4"><Phone className="w-8 h-8 text-blue-500 flex-shrink-0" /><div><p className="text-sm text-gray-500">Phone</p>{isEditing ? <input type="tel" name="phone" value={editableProfile.phone} onChange={handleProfileChange} className="font-medium text-gray-800 border-b w-full" /> : <p className="font-medium text-gray-800">{userProfile.phone}</p>}</div></div>
          </div>
          <div className="mb-8">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center"><GraduationCap className="w-6 h-6 mr-3 text-blue-600" />Education</h3>
            <div className="pl-9 space-y-2">
              {isEditing ? <input type="text" name="education" value={editableProfile.education} onChange={handleProfileChange} className="font-semibold text-gray-900 text-lg border-b w-full" /> : <p className="font-semibold text-gray-900 text-lg">{userProfile.education}</p>}
              {isEditing ? <input type="text" name="university" value={editableProfile.university} onChange={handleProfileChange} className="text-gray-600 border-b w-full" /> : <p className="text-gray-600">{userProfile.university}</p>}
              {isEditing ? <input type="text" name="graduationYear" value={editableProfile.graduationYear} onChange={handleProfileChange} className="text-sm text-gray-500 border-b w-full" /> : <p className="text-sm text-gray-500">Graduated: {userProfile.graduationYear}</p>}
            </div>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center"><Award className="w-6 h-6 mr-3 text-blue-600" />Skills</h3>
            <div className="pl-9">{isEditing ? (<div><input type="text" value={editableProfile.skills.join(', ')} onChange={handleSkillsChange} className="bg-blue-50 text-blue-800 text-sm font-semibold px-4 py-2 rounded-lg w-full" /><p className="text-xs text-gray-500 mt-1">Enter skills separated by commas.</p></div>) : (<div className="flex flex-wrap gap-3">{userProfile.skills.map(skill => (<span key={skill} className="bg-blue-100 text-blue-800 text-sm font-semibold px-4 py-2 rounded-full">{skill}</span>))}</div>)}</div>
          </div>
        </div>
      </div>
    </div>
);

// =================================================================================
// MAIN APP COMPONENT
// =================================================================================

const JobRecommendationSystem = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [userProfile, setUserProfile] = useState({ name: 'John Doe', email: 'john.doe@example.com', phone: '+91 98765 43210', location: 'Narasaraopet, Andhra Pradesh', education: 'B.Tech Computer Science', university: 'Example University', graduationYear: '2024', skills: ['React', 'JavaScript', 'Python', 'Node.js', 'MongoDB', 'UI/UX Design', 'Cloud Computing'], resumeUploaded: false });
  const [editableProfile, setEditableProfile] = useState(userProfile);
  
  const allInternships = [
    { id: 1, title: "Frontend Developer Intern", company: "TechCorp Inc.", location: "Remote", duration: "3 months", stipend: "$800/month", description: "Work on React-based projects...", skills: ["React", "JavaScript", "CSS", "HTML"] },
    { id: 2, title: "Data Science Intern", company: "DataMinds AI", location: "Bangalore, India", duration: "6 months", stipend: "₹15,000/month", description: "Assist in building ML models...", skills: ["Python", "Machine Learning", "Pandas", "TensorFlow"] },
    { id: 3, title: "Backend Developer Intern", company: "CloudSoft Solutions", location: "Hybrid", duration: "4 months", stipend: "$1000/month", description: "Develop REST APIs...", skills: ["Node.js", "Express", "MongoDB", "AWS"] },
    { id: 4, title: "Mobile App Developer Intern", company: "AppVentures", location: "Mumbai, India", duration: "3 months", stipend: "₹12,000/month", description: "Build cross-platform mobile apps...", skills: ["React Native", "JavaScript", "Mobile Development", "Firebase"] },
    { id: 5, title: "UI/UX Design Intern", company: "DesignHub", location: "Remote", duration: "3 months", stipend: "$700/month", description: "Create user interfaces...", skills: ["Figma", "Adobe XD", "User Research", "Prototyping"] }
  ];

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setUploadedFile(file);
      setIsProcessing(true);
      setTimeout(() => {
        const mockRecommendations = [
            { ...allInternships[0], matchScore: 92, reason: "Your strong React and JavaScript skills align perfectly with this role. Your previous project experience demonstrates the exact technical stack required.", applicationUrl: "https://example.com/apply/1" },
            { ...allInternships[2], matchScore: 87, reason: "Your backend development experience with Node.js and database management makes you an excellent fit. Your cloud computing coursework is highly relevant.", applicationUrl: "https://example.com/apply/2" },
            { ...allInternships[3], matchScore: 84, reason: "Your JavaScript proficiency and interest in mobile development match well. Your understanding of modern frameworks is a strong advantage.", applicationUrl: "https://example.com/apply/3" },
            { ...allInternships[1], matchScore: 78, reason: "Your Python programming skills and coursework in statistics provide a good foundation. Consider strengthening ML knowledge for better fit.", applicationUrl: "https://example.com/apply/4" },
            { ...allInternships[4], matchScore: 72, reason: "Your creative portfolio and attention to detail in previous projects show potential. Your basic design tool knowledge is a good starting point.", applicationUrl: "https://example.com/apply/5" }
        ];
        setRecommendations(mockRecommendations);
        setIsProcessing(false);
      }, 2500);
    } else {
      alert('Please upload a PDF file');
    }
  };
  const getMatchColor = (score) => {
    if (score >= 85) return 'text-green-600 bg-green-50';
    if (score >= 70) return 'text-blue-600 bg-blue-50';
    return 'text-orange-600 bg-orange-50';
  };
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setEditableProfile(prev => ({ ...prev, [name]: value }));
  };
  const handleSkillsChange = (e) => {
    const skillsArray = e.target.value.split(',').map(skill => skill.trim());
    setEditableProfile(prev => ({ ...prev, skills: skillsArray }));
  };
  const handleSave = () => {
    setUserProfile(editableProfile);
    setIsEditing(false);
  };
  const handleCancel = () => {
    setEditableProfile(userProfile);
    setIsEditing(false);
  };

  if (currentPage === 'recommendations') {
    return <RecommendationsPage {...{ setCurrentPage, setUploadedFile, setRecommendations, uploadedFile, isProcessing, recommendations, handleFileUpload, getMatchColor }} />;
  }
  if (currentPage === 'profile') {
    return <ProfilePage {...{ setCurrentPage, isEditing, setIsEditing, userProfile, editableProfile, handleSave, handleCancel, handleProfileChange, handleSkillsChange }} />;
  }
  return <HomePage {...{ allInternships, setCurrentPage }} />;
};

export default JobRecommendationSystem;

