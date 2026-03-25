ATS Resume Checker is an AI-powered web application that evaluates resumes against job descriptions and provides a detailed ATS score, helping users optimize their resumes for better job selection chances.

💡 Built with a focus on real-world usability, this project helps job seekers understand exactly why their resume gets rejected — and how to fix it.

🎯 Key Features

✨ Smart ATS Score
Get a percentage score based on resume-job match

🔍 Missing Keywords Detection
Find exactly what recruiters are looking for

🧠 AI-Powered Analysis
Intelligent comparison using NLP techniques

✍️ Grammar Check (Optional)
Improve professionalism and readability

📁 Easy Resume Upload
Supports quick analysis

🔐 Secure Login System
Firebase Authentication integrated

☁️ Cloud Storage (Firestore)
Stores only relevant data:

Email
ATS Score
Job Description
Missing Keywords
Timestamp


⚙️ Tech Stack
Layer	Technology
Frontend	Streamlit
Backend	Python
Database	Firebase Firestore
Auth	Firebase Authentication
AI Logic	NLP-based text matching

🧠 How It Works
📂 Project Structure
ATS-Resume-Checker/
│
├── app.py                 # Main Streamlit app
├── firebase_config.py     # Firebase setup
│
├── pages/
│   ├── 1_Student_Dashboard.py
│   ├── 2_ATS_Score_Checker.py
│   └|── 3_Grammar_Enhancer.py
│
├── assets/
├── requirements.txt
└── README.md

🚀 Getting Started
🔧 Installation
git clone https://github.com/your-username/ATS-Resume-Checker.git
cd ATS-Resume-Checker
pip install -r requirements.txt

🔥 Firebase Setup
Create project on Firebase
Enable:
Authentication
Firestore Database
Add credentials in:
firebase_config.py

▶️ Run the App
streamlit run app.py

📈 Future Scope

🚀 AI Resume Suggestions
📄 Downloadable Report (PDF)
🎯 Role-Based Scoring System
🌐 Live Deployment (Streamlit Cloud)
📊 Admin Dashboard (Analytics)

💡 Why This Project?

✔️ Solves a real-world problem
✔️ Combines AI + Web Development
✔️ Helps students & job seekers
✔️ Clean and scalable architecture

🤝 Contributing

Contributions are welcome!

fork → clone → improve → pull request 🚀
