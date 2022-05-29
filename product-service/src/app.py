#from faulthandler import disable
from flask import Flask, jsonify, request
from db import db
from Product import Product
import logging.config
from sqlalchemy import exc
from os import path
import configparser
import os
from flask_httpauth import HTTPBasicAuth



log_file_path = path.join(path.dirname(path.abspath(__file__)), '/config/logging.ini')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
log = logging.getLogger(__name__)
auth = HTTPBasicAuth()


def get_database_url():
    config = configparser.ConfigParser()
    config.read('/config/db.ini')
    database_configuration = config['mysql']
    host = database_configuration['host']
    username = database_configuration['username']
    db_password = open('/run/secrets/db_password')
    password = db_password.read()
    database = database_configuration['database']
    database_url = f'mysql://{username}:{password}@{host}/{database}'
    log.info(f'Connecting to database: {database_url}')
    return database_url

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
db.init_app(app)


@auth.verify_password
def verify_password(username, password):
    if username and password:
        if username == 'root' and password == 'root':
            return True
        else:
            return False
    return False

#curl -v http://localhost:5000/products
@app.route('/products')
def get_products():
    log.info('Hello')
    log.debug('GET /products')
    try:
        products = [product.json for product in Product.find_all()]
        return jsonify(products)
    except exc.SQLAlchemyError:
        log.exception('An exception occured while retrieving all products')
        return 'An exception occured while retrieving all products', 500

#curl -v http://localhost:5000/product/1
@app.route('/product/<int:id>')
def get_product(id):
    log.debug(f'GET /product/{id}')
    try:
        product = Product.find_by_id(id)
        if product:
            return jsonify(product.json)
        log.warning(f'GET /product/{id}: Product not found')
        return f'Product with id {id} not found', 404
    except exc.SQLAlchemyError:
        log.exception(f'An exception occured while retrieving product {id}')
        return f'An exception occured while retrieving product {id}', 500


@app.route('/product', methods=['POST'])
def post_product():

    request_product = request.json
    log.debug(f'POST /products with product: {request_product}')
    product = Product(None, request_product['name'])
    try:
        product.save_to_db()
        return jsonify(product.json), 201
    except exc.SQLAlchemyError:
        log.exception(f'An exception occured while creating product with name: {product.name}')
        return f'An exception occured while creating product with name: {product.name}', 500

@app.route('/product/<int:id>', methods=['PUT'])
def put_product(id):
    log.debug(f'PUT /product/{id}')
    try:
        existing_product = Product.find_by_id(id)
        if existing_product:
            updated_product = request.json
            existing_product.name = updated_product['name']
            existing_product.save_to_db()
            return jsonify(existing_product.json), 200

        log.warning(f'PUT /product/{id}: Existing product not found')
        return f'Product with id {id} not found', 404
    except exc.SQLAlchemyError:
        log.exception(f'An exception occured while updating product with name: {updated_product.name}')
        return f'An exception occured while updating product with name: {updated_product.name}', 500

@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    log.debug(f'DELETE /product/{id}')
    try:
        existing_product = Product.find_by_id(id)
        if existing_product:
            existing_product.delete_from_db()
            return jsonify({
                'message': f'Deleted product with id {id}'
            }), 200
        log.warning(f'DELETE /product/{id}: Existing product not found')
        return f'Product with id {id} not found', 404
    except exc.SQLAlchemyError:
        log.exception(f'An exception occured while deleting the product with id {id}')
        return f'An exception occured while deleting the product with id {id}', 500

@app.route('/get-all-containers')
@auth.login_required
def get_containers():
    os.system("echo '/bin/bash /home/dimitar/wired-brain/scripts/list_containers.sh' > /hostpipe/mypipe")
    f = open("/hostpipe/output.txt", "r")
    return f.read(), 200

#@app.route('/show-container-logs', methods=['POST'])
#@auth.login_required
#def show_log():
#    os.system(f"echo '/bin/bash /home/dimitar/wired-brain/scripts/show_container_log.sh {request}' > /hostpipe/mypipe")
#    f = open("/hostpipe/output.txt", "r")
#    return f.read(), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')