from flask import Flask, request, jsonify
from amazon import AmazonScraper

app = Flask(__name__)
scraper = AmazonScraper()

# health check route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Amazon scraper API running"})

@app.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    page = request.args.get('page', default=1, type=int)
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    try:
        results = scraper.search_products(query, page)
        return jsonify({
            "query": query,
            "page": page,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/product/<product_id>', methods=['GET'])
def get_product(product_id):
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    try:
        product_details = scraper.get_product_details(product_id)
        if product_details:
            return jsonify(product_details)
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # host=0.0.0.0 makes it reachable from outside too
    app.run(host="0.0.0.0", port=5000, debug=True)
