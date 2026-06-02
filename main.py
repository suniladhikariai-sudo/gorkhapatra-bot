import os
import requests
import pdfplumber
import google.generativeai as genai
import urllib.parse

# =========================
# 1. GEMINI SETUP
# =========================
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# 2. GET LATEST PDF LINK (YOU ALREADY PASS THIS)
# =========================
latest_pdf = "https://epaper.gorkhapatraonline.com/pdf/4386?file=/uploads/file/2026/5/gorkhapatra/2026-05-31-11-43-34-2083-02-18.pdf"

# =========================
# 3. FIX PDF URL (IMPORTANT FIX)
# =========================
pdf_url = latest_pdf.split("file=")[-1]
pdf_url = urllib.parse.unquote(pdf_url)

if not pdf_url.startswith("http"):
    pdf_url = "https://epaper.gorkhapatraonline.com" + pdf_url

print("📄 Downloading PDF:", pdf_url)

# =========================
# 4. DOWNLOAD PDF
# =========================
response = requests.get(pdf_url)

if response.status_code != 200:
    print("❌ Failed to download PDF")
    exit(1)

pdf_path = "latest.pdf"

with open(pdf_path, "wb") as f:
    f.write(response.content)

print("✅ PDF downloaded")

# =========================
# 5. EXTRACT TEXT
# =========================
text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

if not text.strip():
    print("❌ No text extracted (PDF may be image-based)")
    exit(1)

print("✅ Text extracted")

# =========================
# 6. GEMINI PROMPT (TENDER FILTER)
# =========================
prompt = f"""
From the following newspaper text, extract ONLY construction/bolpatra/government tenders.

Return JSON array like:
[
  {{
    "title": "",
    "organization": "",
    "deadline": "",
    "location": ""
  }}
]

TEXT:
{text}
"""

# =========================
# 7. CALL GEMINI
# =========================
response = model.generate_content(prompt)

print("✅ GEMINI OUTPUT:")
print(response.text)
