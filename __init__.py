import os
from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    from . import weekly

    ALLOWED_EXTENSIONS = {'csv'}

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            uploaded_file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if uploaded_file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if uploaded_file and allowed_file(uploaded_file.filename):
                csv_file = uploaded_file.stream.read()
                if csv_file:
                    return render_template('index.html', uploaded_file=csv_file)
                else:
                    return redirect(request.url)
        return render_template('index.html')

    return app