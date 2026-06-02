import requests
import re
import pdfplumber
import google.generativeai as genai
import os

url = "https://epaper.gorkhapatraonline.com/single/gorkhapatra"
html = requests.get(url).text

pdf_links = re.findall(r'https://epaper\.gorkhapatraonline\.com/pdf/[^\s"]+', html)
latest_pdf = pdf_links[0]

pdf_path = "latest.pdf"
pdf = requests.get(latest_pdf).content

with open(pdf_path, "wb") as f:
    f.write(pdf)

text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text += page.extract_text() or ""

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content(f"""
Extract ONLY construction/bolpatra tenders.

Return JSON:
title, organization, deadline, details

TEXT:
{text}
""")

print(response.text)
