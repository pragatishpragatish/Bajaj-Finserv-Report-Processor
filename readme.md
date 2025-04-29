# 🧪 Bajaj Finserv Report Processor

This project extracts **lab test details** from scanned medical reports using OCR (Tesseract) and a FastAPI backend.

### 🔍 Features
- Upload a lab report image (`.png`, `.jpg`, etc.)
- Extracts test names and values from the report using OCR
- Returns the output as a structured JSON
- Supports both **local** and **hosted** deployments

---

## 🚀 API Endpoint

### `POST /get-lab-tests`

**Form Data:**
- `image`: An image file (`.png`, `.jpg`) of a lab report

**Response:**  
Returns extracted test results in JSON format.

---

## 🖥️ Local Development

### 🔧 Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install dependencies:
    ```bash
    pip install -r requirements.txt

3. Run the server:
    ```bash
    uvicorn main:app --reload
    
4. Test with curl:
    ```bash
    curl -X POST -F "image=@path_to_image.png" http://127.0.0.1:8000/get-lab-tests | python -m json.tool

## 🌐 Live Deployment (PythonAnywhere)
Hosted URL:
https://ampragatish1.pythonanywhere.com/get-lab-tests

## Project Structure:
            .
        ├── main.py           # FastAPI backend
        ├── flask_app.py      # Flask wrapper for WSGI compatibility (PythonAnywhere)
        ├── requirements.txt  # Dependencies
        └── README.md

## 🧠 Credits
Built by @pragatish for Bajaj Finserv internal lab report processing use-case.

