from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
import time

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_leads():
    data = request.get_json()
    if not data or 'keyword' not in data or 'location' not in data:
        return jsonify({"error": "Missing 'keyword' or 'location' in JSON body"}), 400
    
    keyword = data['keyword'].replace(' ', '+')
    location = data['location'].replace(' ', '+')
    
    # YellowPages USA Search URL
    url = f"https://www.yellowpages.com/search?search_terms={keyword}&geo_location={location}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch data. Status code: {response.status_code}"}), 400
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result')
        
        leads = []
        
        for result in results:
            # Business Name
            name_tag = result.find('a', class_='business-name')
            name = name_tag.get_text(strip=True) if name_tag else "N/A"
            
            # Phone Number
            phone_tag = result.find('div', class_='phone')
            phone = phone_tag.get_text(strip=True) if phone_tag else "N/A"
            
            # Website Link
            web_tag = result.find('a', class_='track-visit-website')
            website = web_tag['href'] if web_tag else "N/A"
            
            # Business Category
            cat_tag = result.find('div', class_='categories')
            category = cat_tag.get_text(strip=True) if cat_tag else "N/A"
            
            if name != "N/A":
                leads.append({
                    "business_name": name,
                    "phone": phone,
                    "website": website,
                    "category": category
                })
        
        return jsonify({
            "status": "success",
            "total_leads_found": len(leads),
            "leads": leads
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
