# MindBlocks

# Smart Academic Workflow Assistant

An interactive web app that helps students and professionals stay organized by:  
- Uploading or pasting a syllabus (PDF or text)  
- Automatically generating study/work schedules  
- Viewing and managing events on a full interactive calendar  
- Syncing planned blocks directly to **Google Calendar**  



##  Features

- **Upload or Paste Syllabus** → Extract topics and deadlines from your course plan.  
- **AI-Powered Schedule Generation** → Creates smart study/work blocks.  
- **Interactive Calendar** → View events with day/week/month/agenda modes.  
- **Event Sync** → Add planned events directly to Google Calendar.  
- **Clean Modern UI** → Built with TailwindCSS and themed with black, blue, and pink.  



##  Tech Stack

- **React (Next.js)** → Frontend framework  
- **TailwindCSS** → Styling and responsive design  
- **Lucide Icons** → Beautiful SVG icons  
- **Google Calendar API** → Event syncing
- **ShadCn** → Component styling library
- **FastAI** → Backend framework
- **Authlib** → An authentication library
- **Google Cloud AI** → Gemini AI
- **LangChain** → AI Agents framework







## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/NanditaRK/MindBlocks.git
```


### Frontend

```bash
cd frontend
npm install
npm run dev
```
### Backend

```bash
cd backend
poetry env use python3.10
poetry activate # generates source /path/to/venv
poetry env use source /path/to/venv
poetry install
uvicorn main:app --port 8000
```

