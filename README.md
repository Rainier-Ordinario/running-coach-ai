# Marathon AI Coach

An AI-powered marathon training coach that analyzes your Garmin running data and provides personalized training advice using Google Gemini.

## Features

- Sync running activities from Garmin Connect
- AI-powered coaching with context from your training data
- Chat interface for training questions
- Real-time activity analysis and pace calculations

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Garmin Connect account (https://connect.garmin.com)
- Google Gemini API key (get from https://aistudio.google.com/app/apikeys)

### Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `GARMIN_EMAIL`: Your Garmin Connect email
- `GARMIN_PASSWORD`: Your Garmin Connect password
- `GEMINI_API_KEY`: Your Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173`

## Usage

1. Start the backend server
2. Start the frontend development server
3. Click "Sync Garmin" to import your recent activities
4. Ask the coach questions about your training

## API Endpoints

- `GET /api/status` - Check if data is synced and get activity count
- `POST /api/sync` - Sync activities from Garmin
- `POST /api/chat` - Ask the coach a question
