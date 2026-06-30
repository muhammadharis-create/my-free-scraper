from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    # 1. Get the URL sent by Make.com
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' parameter in JSON body"}), 400
    
    url = data['url']
    
    # 2. Pretend to be a normal web browser so we don't get instantly blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to load page. Status code: {response.status_code}"}), 400
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Extract the Page Title, Headings, and Paragraphs
        title = soup.title.string if soup.title else "No Title Found"
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text(strip=True)]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        
        # 4. Clean up lists (extract list items like directory details/bullets)
        list_items = [li.get_text(strip=True) for li in soup.find_all('li') if li.get_text(strip=True)]
        
        # 5. Send it back to Make.com
        return jsonify({
            "status": "success",
            "page_title": title,
            "headings": headings[:30],       # Limits to top 30 to keep data clean
            "text_content": paragraphs[:30],  # Limits to top 30 paragraphs
            "list_data": list_items[:50]      # Limits to top 50 list items
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render requires the app to run on a dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
