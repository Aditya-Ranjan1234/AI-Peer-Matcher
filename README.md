# AI-Powered Peer Learning Matcher

An intelligent matchmaking system that pairs students with complementary strengths and weaknesses for collaborative learning, using Natural Language Processing to analyze student profiles and optimize study groups.

## 🚀 Features

- **Hybrid Matching Engine**: Combines **NLP Semantic Analysis** with a structured **Knowledge Graph** to understand both context and skill relationships.
- **Dual Matching Scores**: View both "AI Match" (sentiment/context) and "Graph Match" (structural skill overlap) for every pairing.
- **Modern UI**: Premium dark-themed interface with glassmorphism effects and dynamic score badges.
- **REST API**: FastAPI-powered backend with automatic validation and Knowledge Graph integration.
- **Project Relevance Hub**: Find projects that fit your skills using a combination of semantic and structural relevance.

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **NLP Engine**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Knowledge Graph**: Custom Ontology-based Graph Matching Service
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Matching Algorithm**: Hybrid (NLP Cosine Similarity + Graph Jaccard Similarity)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

## 🔧 Setup Instructions

### 1. Clone/Navigate to the Project

```bash
cd "d:/5th Sem/peer matcher"
```

### 2. Activate Virtual Environment

The virtual environment is already created. Activate it:

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

**Note**: The first time you run the application, it will download the Sentence Transformer model (~80MB). This is a one-time download and will be cached.

### 4. Start the Backend Server

```bash
cd backend
python -m uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

API Documentation (Swagger): `http://localhost:8000/docs`

### 5. Open the Frontend

Open `frontend/index.html` in your web browser or use a local server:

**Using Python:**
```bash
cd frontend
python -m http.server 3000
```

Then visit: `http://localhost:3000`

**Or simply open:**
```
frontend/index.html
```
(Open directly in browser - works with file:// protocol)

## 📖 Usage

### Creating Student Profiles

1. Fill in the profile form with:
   - **Student ID**: Unique identifier (e.g., stu001)
   - **Name**: Student's full name
   - **Strengths**: Subjects/topics they excel at (e.g., "Mathematics, Calculus, Physics")
   - **Weaknesses**: Subjects/topics they need help with (e.g., "Literature, Essay Writing")
   - **Preferences** (optional): Study preferences (e.g., "Evenings, small groups")
   - **Description** (optional): Additional learning style info

2. Click "Create Profile & Find Matches"

3. View your top matches with similarity scores

### Understanding Match Scores

- **70-100%**: Excellent match - highly complementary skills
- **40-69%**: Good match - some overlap in complementary areas
- **0-39%**: Lower match - limited complementary alignment

## 🔌 API Endpoints

### `GET /`
Health check endpoint

### `POST /profiles`
Create a new student profile
```json
{
  "id": "stu001",
  "name": "John Doe",
  "strengths": "Mathematics, Physics",
  "weaknesses": "Literature, History",
  "preferences": "Evenings, online",
  "description": "Visual learner"
}
```

### `GET /profiles`
Get all student profiles

### `GET /match/{student_id}?top_k=3`
Get top K matches for a student

### `DELETE /profiles/{student_id}`
Delete a student profile

## 🧪 Testing the System

### Test Scenario 1: Complementary Students

**Student 1:**
- Strengths: "Mathematics, Calculus, Algebra, Problem Solving"
- Weaknesses: "Literature, Essay Writing, History"

**Student 2:**
- Strengths: "English Literature, Writing, History, Reading Comprehension"
- Weaknesses: "Mathematics, Calculus, Physics"

These students should have a **high match score** (70%+) because they can help each other.

### Test Scenario 2: Similar Students

**Student 3:**
- Strengths: "Programming, Computer Science, Algorithms"
- Weaknesses: "Data Structures, System Design"

**Student 4:**
- Strengths: "Software Development, Coding, Web Development"
- Weaknesses: "Algorithms, Mathematics"

These students should have a **lower match score** because their strengths overlap and may not complement each other as well.

## 🏗️ Project Structure

```
peer matcher/
├── venv/                    # Virtual environment
├── backend/
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic schemas
│   ├── matcher.py          # Core matching engine
│   ├── knowledge_graph.py  # Knowledge Graph service & Ontology
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Styling
│   └── app.js              # Frontend logic
├── Procfile                # Deployment config
└── README.md               # This file
```

## 🚀 Deployment

### Deploy Backend to Railway

1. Install Railway CLI:
```bash
npm install -g railway
```

2. Initialize and deploy:
```bash
railway init
railway up
```

3. Set environment variables if needed

### Deploy Frontend to Netlify

1. Create `netlify.toml`:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. Drag and drop the `frontend` folder to Netlify

3. Update `API_BASE_URL` in `app.js` to your Railway backend URL

### Alternative: Deploy to Heroku

```bash
heroku create your-app-name
git push heroku main
```

## 🧠 How It Works

### Hybrid Matching Algorithm

1. **Semantic Layer (NLP)**:
   - Strengths and weaknesses are converted to 384-dimensional vectors.
   - Measures "contextual similarity" (e.g., "Designing UIs" and "Front-end engineering").

2. **Graph Layer (Knowledge Graph)**:
   - Uses a structured ontology to find direct relationships between skills.
   - Maps specific tools (e.g., "FastAPI") to parent categories ("Web Development").
   - Measures "structural overlap" using expanded node sets.

3. **Combined Scoring**:
   - Every match provides two scores, allowing users to see both how well they fit contextually and how their practical skills align.

## 🎨 UI Features

- **Dark Mode**: Premium dark theme with vibrant accents
- **Glassmorphism**: Modern glass-like effects on cards
- **Animations**: Smooth transitions and micro-interactions
- **Responsive**: Works on desktop, tablet, and mobile
- **Gradient Accents**: Purple-blue gradient palette

## 🔒 Security Notes

For production deployment:
- Change CORS settings in `main.py` to specific origins
- Add authentication for profile creation/deletion
- Use environment variables for sensitive config
- Add rate limiting to prevent abuse

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- NLP powered by [Sentence Transformers](https://www.sbert.net/)
- UI inspired by modern web design trends

## 🐛 Troubleshooting

**Backend won't start:**
- Make sure you activated the venv
- Check if port 8000 is already in use
- Verify all dependencies are installed

**Model download fails:**
- Check internet connection
- The model download is ~80MB, may take time
- Will be cached after first download

**Frontend can't connect to backend:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify `API_BASE_URL` in `app.js`

**No matches found:**
- Need at least 2 profiles to generate matches
- Try creating profiles with more distinct strengths/weaknesses
