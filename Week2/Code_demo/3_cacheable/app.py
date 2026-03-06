from flask import Flask, jsonify, make_response
from datetime import datetime

app = Flask(__name__)

@app.route('/api/news', methods=['GET'])
def get_news():
    news = [
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},

        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"},
        {"id": 1, "title": "Breaking News 1", "date": "2026-03-06"},
        {"id": 2, "title": "Breaking News 2", "date": "2026-03-06"}
    ]
    
    response = make_response(jsonify(news))
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['ETag'] = 'news-v1'
    
    return response

@app.route('/api/time', methods=['GET'])
def get_time():
    current_time = datetime.now().isoformat()
    
    response = make_response(jsonify({"time": current_time}))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/api/static-data', methods=['GET'])
def get_static():
    data = {"config": "v1.0", "settings": {"theme": "dark"}}
    
    response = make_response(jsonify(data))
    response.headers['Cache-Control'] = 'public, max-age=86400'
    
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5003)
