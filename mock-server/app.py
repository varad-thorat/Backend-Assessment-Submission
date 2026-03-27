from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Load customer data from JSON file
def load_customers():
    """Load customer data from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')
    with open(json_path, 'r') as f:
        return json.load(f)

# Cache the customers data
CUSTOMERS = load_customers()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "flask-mock-server",
        "total_customers": len(CUSTOMERS)
    }), 200

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get paginated list of customers"""
    try:
        # Get pagination parameters from query string
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Validate parameters
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if limit < 1 or limit > 100:
            return jsonify({"error": "Limit must be between 1 and 100"}), 400
        
        # Calculate pagination
        total = len(CUSTOMERS)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get paginated data
        paginated_data = CUSTOMERS[start_idx:end_idx]
        
        # Return response
        return jsonify({
            "data": paginated_data,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid page or limit parameter"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a single customer by ID"""
    try:
        # Find customer by ID
        customer = next((c for c in CUSTOMERS if c['customer_id'] == customer_id), None)
        
        if customer is None:
            return jsonify({
                "error": "Customer not found",
                "customer_id": customer_id
            }), 404
        
        return jsonify(customer), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)