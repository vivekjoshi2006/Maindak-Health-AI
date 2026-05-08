from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# --- 💊 ENHANCED MEDICINES DATABASE ---
DEFAULT_MEDS = {
    "FEVER": ["Paracetamol (Dolo 650, Crocin)", "Ibuprofen (Brufen)", "Nimesulide (Sumo)"],
    "COLD": ["Cetirizine (Okacet)", "Levocetirizine (1-AL)", "Phenylephrine (Solvin Cold)"],
    "COUGH": ["Dextromethorphan (Dry Cough)", "Ambroxol (Wet Cough)", "Honitus (Ayurvedic)"],
    "HEADACHE": ["Paracetamol", "Aspirin (Disprin)", "Diclofenac Gel (Volini)"],
    "STOMACH PAIN": ["Meftal-Spas", "Cyclopam", "Digene (For Acidity)"],
    "ACIDITY": ["Pantoprazole (Pan-40)", "Eno", "Digene Syrup"],
    "DIARRHEA": ["ORS (Electral)", "Loperamide (Imodium)", "Sporlac DS"],
    "BODY PAIN": ["Aceclofenac (Zerodol-P)", "Naproxen", "Ibuprofen"],
    "VOMITING": ["Ondansetron (Ondem)", "Domperidone (Domstal)"],
    "ALLERGY": ["Avil", "Allegra (Fexofenadine)", "Cetirizine"]
}

# --- 🛡️ FALLBACK CARE TIPS ---
DEFAULT_TIPS = [
    "Take plenty of rest to help your body recover faster.",
    "Stay hydrated by drinking water, juice, or soup frequently.",
    "Monitor your symptoms closely and consult a doctor if they worsen."
]

def clean_snippet(text):
    """Cleans snippets to ensure they are complete sentences and ad-free."""
    if not text: return ""
    # Remove prices and commercial keywords
    text = re.sub(r'(₹|Rs\.?)\s?\d+([\d,.]*)', '', text)
    blacklist = ['buy', 'discount', 'cashback', 'shop', 'order online', 'genuine']
    for word in blacklist:
        text = re.sub(f'(?i){word}', '', text)
    
    text = text.replace('...', '').strip()
    
    # Sentence completion logic: Cut at the last full stop
    sentences = re.split(r'(?<=[.!?]) +', text)
    if len(sentences) > 1:
        if not re.search(r'[.!?]$', sentences[-1]):
            sentences.pop() # Remove the last incomplete sentence
    
    final_text = " ".join(sentences).strip()
    if final_text and not final_text.endswith(('.', '!', '?')):
        final_text += "."
    return final_text

def fetch_data(query, stype):
    disease_key = query.upper().strip()
    
    # 1. Match Medicine using Fuzzy Matching (e.g., 'Fevers' matches 'FEVER')
    medicines_list = ["Consult a doctor for specific salts."]
    for key in DEFAULT_MEDS:
        if key in disease_key or disease_key in key:
            medicines_list = DEFAULT_MEDS[key]
            break

    # 2. Scrape DuckDuckGo with better headers
    search_query = f"{query} treatment care precautions"
    url = f"https://html.duckduckgo.com/html/?q={search_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    data = {
        "name": disease_key,
        "details": [], 
        "links": [],   
        "medicines": medicines_list
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # DuckDuckGo HTML results are usually in result__body or result__snippet
            results = soup.find_all('div', class_='result__body')

            for res in results:
                snippet_tag = res.find('a', class_='result__snippet')
                title_tag = res.find('a', class_='result__a')
                
                if snippet_tag and title_tag:
                    snippet = snippet_tag.text.strip()
                    title = title_tag.text.strip()
                    link = title_tag['href']
                    
                    point = clean_snippet(snippet)
                    
                    # Store only high-quality care points
                    if len(data["details"]) < 3 and len(point) > 50:
                        if point not in data["details"]: 
                            data["details"].append(point)

                    # Store top 3 resources
                    if len(data["links"]) < 3:
                        data["links"].append({"title": title, "url": link})

                    if len(data["details"]) == 3 and len(data["links"]) == 3:
                        break
        
        # 3. 🚨 FINAL VALIDATION (If Scraping Failed)
        if not data["details"]:
            data["details"] = DEFAULT_TIPS
        if not data["links"]:
            data["links"] = [{"title": "Healthline - Medical Advice", "url": "https://www.healthline.com"}]
            
        return data

    except Exception as e:
        print(f"Backend Error: {e}")
        data["details"] = DEFAULT_TIPS
        return data

@app.route('/api/chatbot/ask', methods=['POST'])
def ask():
    try:
        req = request.json
        user_message = req.get('message', '')
        user_type = req.get('type', 'disease')
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
            
        res = fetch_data(user_message, user_type)
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Maindak Backend is Running! 🐸")
    app.run(debug=True, port=5000)
