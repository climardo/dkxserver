import dkextract, json
from requests import Session
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_wtf import FlaskForm
from os import environ

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=environ.get('SECRET_KEY'),
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
        return render_template('index.html')
    
    @app.route('/generate', methods=['GET', 'POST'])
    def generate():
        if request.method == 'GET':
            return render_template('generate.html')
        elif request.method == 'POST':
            if request.form.get('generate'):
                form = request.form
                weekly = dkextract.generate_results(s, contest_id=form['contest_id'], week=form['week'], year=form['year'], winning_values=winning_values)
                return weekly
            elif request.form.get('get_not_submitted'):
                form = request.form
                not_submitted = dkextract.get_not_submitted_list(s, contest_id=form['contest_id'], all_members=all_members)
                return render_template('not_submitted.html', not_submitted=not_submitted)

    @app.route('/not_submitted/<contest_id>', methods=['GET', 'POST'])
    def not_submitted(contest_id):
        if request.method == 'GET':
            not_submitted = dkextract.get_not_submitted_list(s, contest_id=contest_id, all_members=all_members)
            return render_template('not_submitted.html', not_submitted=not_submitted)

    return app