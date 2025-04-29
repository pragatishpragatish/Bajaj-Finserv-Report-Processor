from PIL import Image, ImageFilter, ImageOps
import re
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def preprocess_image(image):
    image = image.convert('L')
    image = image.filter(ImageFilter.MedianFilter())
    image = image.point(lambda x: 0 if x < 140 else 255, '1')
    return image

def clean_number(text):
    text = text.replace(',', '.')
    text = re.sub(r'^:\s*', '', text)
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)', text)
    return match.group(1) if match else re.sub(r'[^\d.]', '', text)

def is_decimal_range(bio_range):
    parts = re.findall(r"[\d.]+", bio_range)
    return any('.' in p for p in parts)

def format_result_to_range(result, bio_range):
    try:
        if is_decimal_range(bio_range):
            if '.' not in result and len(result) > 1:
                range_parts = re.findall(r"[\d.]+", bio_range)
                if len(range_parts) == 2:
                    low, high = map(float, range_parts)
                    for i in range(1, len(result)):
                        candidate = result[:i] + '.' + result[i:]
                        try:
                            if low <= float(candidate) <= high:
                                return candidate
                        except: continue
            return f"{float(result):.2f}" if '.' in result else result
        else:
            return str(int(float(result)))
    except:
        return result

def lab_test_out_of_range(measured_value, bio_range):
    try:
        measured = float(measured_value)
        range_parts = re.findall(r"[\d.]+", bio_range)
        if len(range_parts) == 2:
            low, high = map(float, range_parts)
            return measured < low or measured > high
    except:
        return False
    return False

def extract_lab_tests(image):
    try:
        processed_image = preprocess_image(image)
        ocr_data = pytesseract.image_to_string(processed_image)
        lines = [line.strip() for line in ocr_data.split("\n") if line.strip()]

        results = []
        pattern1 = re.compile(r'^([\w\s./()\-]{1,50})\s+([:]?\s*[\d.,]+)\s+([a-zA-Z/%μ]+)\s+(\d+[\d.]*\s*-\s*\d+[\d.]*)')
        pattern2 = re.compile(r'^([\w\s./()\-]{1,50})\s+([:]?\s*[\d.,]+)\s+(\d+[\d.]*\s*-\s*\d+[\d.]*)\s+([a-zA-Z/%μ]+)')
        pattern3 = re.compile(r'^([\w\s./()\-]{1,50})\s+([:]?\s*[\d.,]+)\s+(\d+[\d.]*\s*-\s*\d+[\d.]*)')

        for line in lines:
            match = pattern1.match(line) or pattern2.match(line) or pattern3.match(line)
            if match:
                groups = match.groups()
                test_name = groups[0].strip()
                result_raw = groups[1].strip()
                bio_range = groups[-1].strip()
                unit = groups[2].strip() if len(groups) > 3 else ""

                result_clean = clean_number(result_raw)
                result = format_result_to_range(result_clean, bio_range)
                
                results.append({
                    "test_name": test_name,
                    "test_value": result,
                    "bio_reference_range": bio_range,
                    "test_unit": unit,
                    "lab_test_out_of_range": lab_test_out_of_range(result, bio_range)
                })

        return {"is_success": True, "data": results}
    
    except Exception as e:
        return {"is_success": False, "error": str(e)}

@app.post("/get-lab-tests")
async def process_lab_report(image: UploadFile = File(...)):
    if not image.content_type.startswith('image/'):
        raise HTTPException(400, "Invalid file type. Please upload an image.")
    
    try:
        image_data = await image.read()
        image = Image.open(io.BytesIO(image_data))
        return extract_lab_tests(image)
    
    except Exception as e:
        return {"is_success": False, "error": str(e)}
