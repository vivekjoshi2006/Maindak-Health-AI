from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# --- 💊 INTERNAL MEDICAL KNOWLEDGE BASE ---
# This ensures that even if scraping is blocked, the user gets data.
KNOWLEDGE_BASE = {
    "FEVER": {
        "details": [
            "Monitor your body temperature regularly using a digital thermometer.",
            "Stay well-hydrated by drinking plenty of water, electrolytes, or warm soups.",
            "Get adequate rest to allow your immune system to fight the underlying infection.",
            "Use a cool compress on the forehead to help reduce discomfort naturally."
        ],
        "medicines": ["Paracetamol (Dolo 650, Crocin)", "Ibuprofen (Brufen)", "Nimesulide (Sumo)"],
        "links": [{"title": "Fever Care - Mayo Clinic", "url": "https://www.mayoclinic.org/diseases-conditions/fever/diagnosis-treatment/drc-20352764"}]
    },
    "COLD": {
        "details": [
            "Keep the nasal passages moist using saline sprays or a humidifier.",
            "Gargle with warm salt water to relieve a sore throat.",
            "Avoid cold drinks and prefer warm herbal teas or ginger water.",
            "Steam inhalation can help clear a congested nose."
        ],
        "medicines": ["Cetirizine (Okacet)", "Levocetirizine (1-AL)", "Phenylephrine (Solvin Cold)"],
        "links": [{"title": "Common Cold Guide - Healthline", "url": "https://www.healthline.com/health/common-cold"}]
    }
}

DEFAULT_TIPS = [
    "Ensure you are getting enough rest and sleep to recover.",
    "Drink at least 8-10 glasses of water to stay hydrated.",
    "If symptoms persist for more than 3 days, consult a professional doctor."
]

def clean_snippet(text):
    if not text: return ""
    text = re.sub(r'(₹|Rs\.?)\s?\d+([\d,.]*)', '', text)
    text = text.replace('...', '').strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if len(s) > 10]
    if len(sentences) > 1 and not re.search(r'[.!?]$', sentences[-1]):
        sentences.pop()
    final = " ".join(sentences).strip()
    if final and not final.endswith(('.', '!', '?')): final += "."
    return final

def fetch_data(query, stype):
    query_upper = query.upper().strip()
    
    # Initialize Data
    data = {
        "name": query_upper,
        "details": [],
        "medicines": ["Consult a doctor for specific salt names."],
        "links": [{"title": "Healthline Medical Advice", "url": "https://www.healthline.com"}]
    }

    # 1. First, check Internal Knowledge Base (Fastest & Safest)
    for key, info in KNOWLEDGE_BASE.items():
        if key in query_upper:
            data["details"] = info["details"]
            data["medicines"] = info["medicines"]
            data["links"] = info["links"]
            break

    # 2. Try Web Scraping (Only if Internet allows)
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={query}+treatment+care+precautions"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(search_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all('div', class_='result__body')
            
            scraped_details = []
            scraped_links = []
            
            for res in results:
                snippet = res.find('a', class_='result__snippet')
                title = res.find('a', class_='result__a')
                
                if snippet and title:
                    clean_p = clean_snippet(snippet.text)
                    if len(clean_p) > 40 and clean_p not in scraped_details:
                        scraped_details.append(clean_p)
                    
                    if len(scraped_links) < 3:
                        scraped_links.append({"title": title.text.strip(), "url": title['href']})

            # Update data if scraping gave us more/better info
            if len(scraped_details) >= 2: data["details"] = scraped_details[:4]
            if scraped_links: data["links"] = scraped_links[:3]

    except Exception as e:
        print(f"Scraping failed, using internal backup: {e}")

    # 3. Final Fallback if both failed
    if not data["details"]: data["details"] = DEFAULT_TIPS
    
    return data

@app.route('/api/chatbot/ask', methods=['POST'])
def ask():
    req = request.json
    res = fetch_data(req.get('message', ''), req.get('type', 'disease'))
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True)
