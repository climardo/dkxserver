import dkextract, json, re, yaml
from requests import Session
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_wtf import FlaskForm
from os import environ
from .validate import valid_contest_id, get_missing_lineup

def create_app():
    app = Flask(__name__)
    # app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('settings.py')
    all_members = set(
        [
            "AmesSB",
            "BrunoDiaz",
            "climardo",
            "DarbyDiaz3",
            "Dash7",
            "ejmesa",
            "frank.corn",
            "g_mendoza",
            "geedee3",
            "glopez28",
            "hlimardo",
            "ismeyo",
            "JekellP",
            "LoLoGREEN",
            "luisdello",
            "MattyDel14",
            "olivadotij",
            "pshhidk",
            "rahianr"
        ]
    )
    winning_values = {1: 41, 2: 16, 3: 9}
    s = Session()
    
    navlinks = s.get('https://raw.githubusercontent.com/climardo/platanofb/gh-pages/_data/navlinks.yaml').content
    all_links = yaml.safe_load(navlinks)
    curr_link = all_links[0]['link']

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/generate', methods=['GET', 'POST'])
    def generate_form():
        if request.method == 'GET':
            return render_template('generate.html', curr_link=curr_link)
        elif request.method == 'POST':
            contest_id = request.form['contest_id']
        
            if valid_contest_id(contest_id):
                contest_id = valid_contest_id(contest_id)
                if request.form.get('generate'):
                    return redirect(url_for('generate', contest_id=contest_id))
                elif request.form.get('get_not_submitted'):
                    flash('Success! Members who did not submit a lineup are listed below.', category="success")
                    return redirect(url_for('not_submitted', contest_id=contest_id))
            else:
                flash('Please provide a valid contest ID or URL.', category='danger')
                return redirect(url_for('generate_form'))

    @app.route('/generate/<contest_id>', methods=['GET'])
    def generate(contest_id):
        if request.method == 'GET':
            weekly = dkextract.generate_results(s, contest_id=contest_id, winning_values=winning_values)
            return weekly

    @app.route('/not_submitted/<contest_id>', methods=['GET'])
    def not_submitted(contest_id):
        if request.method == 'GET':
            not_submitted = get_missing_lineup(contest_id=contest_id, all_members=all_members)
            return render_template('not_submitted.html', not_submitted=not_submitted)

    return app