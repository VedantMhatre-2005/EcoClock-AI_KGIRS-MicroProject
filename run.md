# 1. Navigate to the backend directory
cd backend

# 2. Activate your virtual environment (if not already active)
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS / Linux:
# source .venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Generate the dataset and 2-page PDFs (only needed on initial setup; auto-skips thereafter)
python scripts/generate_synthetic_data.py

# 5. Ingest all 22 documents into the Knowledge Graph
python scripts/ingest_documents.py

# 6. (Optional) Run the verification test suite
python -m pytest tests -v

# 7. Start the FastAPI backend server
uvicorn app.main:app --reload --port 8000


# 1. Navigate to the frontend directory
cd frontend

# 2. Install frontend dependencies (first time only)
npm install

# 3. Start the Vite development server
npm run dev -- --port 5173