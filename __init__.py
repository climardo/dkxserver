import dkextract, json
from requests import Session
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_wtf import FlaskForm

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='UD1KbD__RZujhpV2p6r9MQ',
    )

    all_members = set(["arianna29", "climardo", "DarbyDiaz3", "Dash7", "ejmesa", "frank.corn", "glopez28", "Halvworld", "hlimardo", "JekellP", "jlopez0809", "LoLoGREEN", "olivadotij", "pshhidk", "rogdiaz", "XplicitK", "g_mendoza"])
    winning_values = {1: 30, 2: 15, 3: 8}
    s = Session()

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.route('/', methods=['GET'])
    def index():
        not_submitted_set = dkextract.get_not_submitted_list(s, 93745891, all_members)
        not_submitted_json = json.dumps(list(not_submitted_set))
        return render_template('index.html', not_submitted=not_submitted_json)
    
    @app.route('/generate', methods=['GET'])
    def generate():
        None


    return app