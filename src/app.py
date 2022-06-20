from flask import Flask
from flask import request, jsonify

from src.extract_data import *

app = Flask(__name__)


@app.route('/api/v1/fandom', methods=['GET'])
def hello_world():
    works_dict = {}
    if 'id' in request.args:
        id = request.args['id']
        fnd, p = make_fandom_vars(id)
        works_dict = extract_works_metadata(fnd, p)
    return works_dict
