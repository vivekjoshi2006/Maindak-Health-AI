from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# --- DEFAULT MEDICINES DATABASE ---
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

# --- DEFAULT CARE TIPS (Fallback) ---
DEFAULT_TIPS = [
    "Take plenty of rest to help your body recover faster.",
    "Stay hydrated by drinking water, juice, or soup frequently.",
    "Monitor your symptoms closely and consult a doctor if they worsen."
]

def clean_snippet(text):
    if not text: return ""
    # Remove currency/pricing mentions
    text = re.sub(r'(₹|Rs\.?)\s?\d+([\d,.]*)', '', text)
    text = text.replace('...', '').strip()
    
    # Ensure complete sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    if len(sentences) > 1 and not re.search(r'[.!?]$', sentences[-1]):
        sentences.pop()
    
    final = " ".join(sentences).strip()
    if final and not final.endswith(('.', '!', '?')): 
        final += "."
    return final

def fetch_data(query, stype):
    disease_key = query.upper().strip()
    
    # 1. Fetch Medicines from Local DB
    medicines_list = DEFAULT_MEDS.get(disease_key, ["Consult a doctor for specific salts."])

    # 2. Fetch Precautions from Web
    search_query = f"{query} symptoms treatment and home care precautions"
    url = f"https://html.duckduckgo.com/html/?q={search_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    data = {
        "name": disease_key,
        "details": [], 
        "links": [],   
        "medicines": medicines_list
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all('div', class_='result')

        if results:
            for res in results:
                snippet_tag = res.find('a', class_='result__snippet')
                title_tag = res.find('a', class_='result__a')
                
                if snippet_tag and title_tag:
                    snippet = snippet_tag.text.strip()
                    title = title_tag.text.strip()
                    link = title_tag['href']
                    
                    point = clean_snippet(snippet)
                    
                    # Filter for quality points
                    if len(data["details"]) < 3 and len(point) > 50:
                        if point not in data["details"]: 
                            data["details"].append(point)

                    if len(data["links"]) < 3:
                        data["links"].append({"title": title, "url": link})

                    if len(data["details"]) == 3 and len(data["links"]) == 3:
                        break
        
        # 3. FALLBACK: Use default tips if web results are empty
        if not data["details"]:
            data["details"] = DEFAULT_TIPS
        if not data["links"]:
            data["links"] = [{"title": "Healthline - Medical Advice", "url": "https://www.healthline.com"}]
            
        return data

    except Exception as e:
        print(f"Error occurred: {e}")
        data["details"] = DEFAULT_TIPS
        return data

@app.route('/api/chatbot/ask', methods=['POST'])
def ask():
    req = request.json
    res = fetch_data(req.get('message'), req.get('type'))
    if res: 
        return jsonify(res)
    return jsonify({"error": "Resource not found"}), 404

if __name__ == '__main__':
    print("Backend is Running!")
    app.run(debug=True, port=5000)
