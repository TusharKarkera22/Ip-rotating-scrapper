from flask import Flask, render_template_string, jsonify
from scraper import scrape_trends
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Twitter Trends Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .result { margin: 20px 0; }
        button { padding: 10px 20px; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 4px; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 4px; }
    </style>
</head>
<body>
    <button onclick="runScraper()">Click here to run the script</button>
    <div id="result" class="result"></div>
    <div id="debug"></div>

    <script>
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZoneName: 'short'
            });
        }

        function runScraper() {
            document.getElementById('result').innerHTML = 'Scraping in progress...';
            
            fetch('/scrape')
                .then(response => response.json())
                .then(data => {
                    
                    
                    let html = `
                        <h3>These are the most happening topics as of ${data.timestamp}</h3>
                        <ul>
                            <li>${data.nameoftrend1}</li>
                            <li>${data.nameoftrend2}</li>
                            <li>${data.nameoftrend3}</li>
                            <li>${data.nameoftrend4}</li>
                            <li>${data.nameoftrend5}</li>
                        </ul>
                        <p>The IP address used for this query was ${data.ip_address}</p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                    document.getElementById('result').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('result').innerHTML = 'Error: ' + error;
                    console.error('Fetch error:', error);
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape')
def scrape():
    result = scrape_trends()
    # Convert only the timestamp to a readable string format
    if isinstance(result.get('timestamp'), datetime):
        formatted_time = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"Formatted timestamp: {formatted_time}")
        print(type(formatted_time))
        return jsonify({
            '_id': result['_id'],
            'ip_address': result['ip_address'],
            'nameoftrend1': result['nameoftrend1'],
            'nameoftrend2': result['nameoftrend2'],
            'nameoftrend3': result['nameoftrend3'],
            'nameoftrend4': result['nameoftrend4'],
            'nameoftrend5': result['nameoftrend5'],
            'timestamp': formatted_time
        })
    

if __name__ == '__main__':
    app.run(debug=True)