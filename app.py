from flask import Flask, request, jsonify
from db import get_products, create_product, update_product, delete_product
from exceptions import ValidationError
from serializers import serialize_product
from deserializers import deserialize_product
from dp import get_categories, create_category

app = Flask(__name__)

@app.route('/hello_world')
def hello_world():
    # Return hello world
    return "Hello, World!"


def get_categories_api():
    try:
        categories = get_categories()
        return jsonify(
            [{'id': category.id, 'name': category.name, 'is_adult_only':
                category.is_adult_only} for category in
             categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/categories', methods=['POST'])
def create_category_api():
    try:
        data = request.json
        name = data.get('name')
        is_adult_only = data.get('is_adult_only', False)

        if not name:
            raise ValidationError("Name is required")

        category = create_category(name, is_adult_only)
        return jsonify({'id': category.id, 'name': category.name,
                        'is_adult_only': category.is_adult_only}), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/categories', methods=['GET'])
def get_categories_api():
    categories = get_categories()
    return jsonify([{'id': category.id, 'name': category.name, 'is_adult_only':
        category.is_adult_only} for category in categories])

@app.route('/categories', methods=['POST'])
def create_category_api():
    data = request.json
    name = data.get('name')
    is_adult_only = data.get('is_adult_only', False)
    category = create_category(name, is_adult_only)
    return jsonify({'id': category.id, 'name': category.name, 'is_adult_only': category.is_adult_only}), 201

@app.route('/products', methods=['GET', 'POST'])
def products_api():
    if request.method == "GET":
        name_filter = request.args.get('name')

        products = get_products(name_filter)

        # Convert products to list of dicts
        products_dicts = [
            serialize_product(product)
            for product in products
        ]

        # Return products
        return products_dicts
    if request.method == "POST":
        # Create a product
        product = deserialize_product(request.get_json())

        # Return success
        return serialize_product(product), 201


@app.route('/products/<int:product_id>', methods=['PUT', 'PATCH', 'DELETE'])
def product_api(product_id):
    if request.method == "PUT":
        # Update a product
        product = deserialize_product(request.get_json(), product_id)
        # Return success
        return serialize_product(product)
    if request.method == "PATCH":
        # Update a product
        product = deserialize_product(request.get_json(), product_id, partial=True)
        # Return success
        return serialize_product(product)
    if request.method == "DELETE":
        delete_product(product_id)

        return "", 204


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return {
        'error': str(e)
    }, 422


if __name__ == '__main__':
    app.run(debug=True, port=5001)
