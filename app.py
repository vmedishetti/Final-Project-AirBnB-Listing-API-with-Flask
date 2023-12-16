from flask import Flask, jsonify, request,make_response
from utils.data_handler import read_data, write_data


app = Flask(__name__)


listing_data = read_data("/Users/harshithathota/Desktop/airbnb_api_project/data/airbnb.json")

@app.route('/listings', methods=['GET'])
def get_all_listings():
    return jsonify(listing_data)

@app.route('/listings/<int:id>', methods=['GET'])
def get_listing_by_id(id):
    listing = next((item for item in listing_data if item.get("id") == id), None)
    if listing:
        return jsonify(listing)
    else:
        return jsonify({"error": "Listing not found"}), 404

@app.route('/listings/filter', methods=['GET'])
def filter_listings():
    try:
        neighborhood = int(request.args.get('neighborhood', 0))
        host_id = int(request.args.get('host_id', 0))
        room_type = request.args.get('room_type', '')
        invalid_param = request.args.get('invalid_param')
        if invalid_param:
            return jsonify({'error': 'Invalid query parameters'}), 400
        filtered_listings = [listing for listing in listing_data if
                             (not neighborhood or listing.get("neighbourhood") == neighborhood) and
                             (not host_id or listing.get("host_id") == host_id) and
                             (not room_type or listing.get("room_type") == room_type)]

        return jsonify(filtered_listings)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

listings_data = []  

@app.route('/listings', methods=['POST'])
def create_listing():
    try:
        new_listing = request.get_json()
        if not new_listing or "name" not in new_listing:
            return jsonify({"error": "Incomplete data provided"}), 400  

        listing_data.append(new_listing)
        # Assuming write_data is a function that writes to a file, if not, replace it with your logic
        write_data("/Users/harshithathota/Desktop/airbnb_api_project/airbnb.json", listing_data)

        return jsonify({"message": "Listing created successfully", "listing": new_listing}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/listing/search', methods=['POST'])
def search_listings():
    search_terms = request.get_json().get("search_terms", [])

    if not search_terms:
        return jsonify({"error": "Search terms not provided"}), 400

    results = [listing for listing in listing_data if any(term.lower() in listing.get("name", "").lower() for term in search_terms)]

    return jsonify(results)

@app.route('/listing/<int:listing_id>', methods=['PATCH'])
def update_listing(listing_id):
    listing = next((item for item in listing_data if item.get("id") == listing_id), None)

    if listing is None:
        response = make_response(jsonify({"error": "Listing not found"}), 404)
        return response

    update_data = request.get_json()
    valid_fields = ["name", "description", "price", "other_field"]
    for key, value in update_data.items():
        if key in valid_fields:
            listing[key] = value

    return jsonify({"message": "Listing updated successfully", "listing": listing}), 200 

@app.route('/listing/<int:id>', methods=['DELETE'])
def delete_listing(id):
    try:
        index = next((index for index, item in enumerate(listing_data) if item.get("id") == id), None)

        if index is not None:
            deleted_listing = listing_data.pop(index)
            write_data("/Users/harshithathota/Desktop/airbnb_api_project/data/airbnb.json", listing_data)
            return jsonify({"message": "Listing deleted successfully", "listing": deleted_listing})
        else:
            return jsonify({"error": "Listing not found"}), 404
    except KeyError:
        return jsonify({"error": f"Listing with id {id} does not have 'id' key"}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



if __name__ == '__main__':
    app.run(debug=True)

#curl http://127.0.0.1:5000/listings
#curl http://127.0.0.1:5000/listings/6413
#curl http://127.0.0.1:5000/listings/filter?neighborhood=78702&host_id=8028&room_type=Entire%20home%2Fapt
#curl -X POST -H "Content-Type: application/json" -d '{"id": 123, "name": "New Listing", "host_id": 456, "neighbourhood": 789, "room_type": "Private room", "price": 75}' http://127.0.0.1:5000/listings
#curl -X POST -H "Content-Type: application/json" -d '{"search_terms": ["Guesthouse", "1 bedroom"]}' http://127.0.0.1:5000/listing/search
#curl -X PATCH -H "Content-Type: application/json" -d '{"price": 150}' http://127.0.0.1:5000/listing/6413
#curl -X DELETE http://127.0.0.1:5000/listing/104099