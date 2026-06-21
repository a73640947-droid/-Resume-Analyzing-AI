from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from google import genai
import io

app = FastAPI()

# फ्रंटेंड को अनुमति देना
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# आपकी जनरेट की हुई असली Gemini API Key
GEMINI_API_KEY = "AQ.Ab8RN6LKF-UlEzuKxezpSbjyA9HaKrZsSYpxvpKvU3GDb5AnLw"

# Gemini Client को इनिशियलाइज करना
client = genai.Client(api_key=GEMINI_API_KEY)

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...), 
    job_description: str = Form(...)
):
    try:
        # 1. अपलोड की गई PDF फाइल को पढ़ना और टेक्स्ट निकालना
        pdf_content = await file.read()
        pdf_file = io.BytesIO(pdf_content)
        reader = PdfReader(pdf_file)
        
        resume_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                resume_text += text + "\n"
        
        if not resume_text.strip():
            return {"status": "Error", "message": "PDF में से टेक्स्ट नहीं निकाला जा सका।"}

        # 2. Gemini AI के लिए प्रॉम्प्ट (Instructions) तैयार करना
        prompt = f"""
        You are an expert ATS (Applicant Tracking System). 
        Analyze the following Resume against the Job Description.
        
        Job Description:
        {job_description}
        
        Resume:
        {resume_text}
        
        Provide the response in clear Hindi mixed with English keywords using this format:
        - Match Percentage: [X]%
        - Missing Skills: [List skills]
        - Recommendations: [Brief tips]
        """

        # 3. Gemini Model से रिस्पांस मांगना
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )

        return {
            "status": "Success",
            "filename": file.filename,
            "analysis": response.text
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {"status": "Error", "message": f"सर्वर एरर: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)