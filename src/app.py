from flask import Flask
import sys
import os
from flask import request, jsonify

sys.path.insert(0, '/Users/mariamilusheva/code/Fandom_Analyser/src')
sys.path.insert(0, '/Users/mariamilusheva/code/Fandom_Analyser')
from src.gc_util import init_storage

from src.extract_data import *

credential_path = "/Users/mariamilusheva/code/Fandom_Analyser/fanfic-an-f719b5feb60f.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
app = Flask(__name__)


@app.route('/api/v1/fandom', methods=['GET'])
def hello_world():
    works_dict = {}
    bucket = init_storage()
    if 'id' in request.args:
        id = request.args['id']
        fnd, p = make_fandom_vars(id)
        works_dict = extract_works_metadata(fnd, p, bucket)
    return works_dict
