import os, re, tempfile
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv'}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config.from_mapping(
        SECRET_KEY='UD1KbD__RZujhpV2p6r9MQ',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    from . import weekly

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    '''
    class UploadForm(FlaskForm):
        csv = FileField(validators=[FileRequired()])

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if form.validate_on_submit():
            f = form.csv.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(
                app.instance_path, filename
            ))
            flash(f'{filename} was uploaded successfully.')
            return redirect(url_for('index'))

        return render_template('upload.html', form=form)
    '''

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                blogpost = weekly.create_blogpost(f"{app.config['UPLOAD_FOLDER']}/{session['filename']}", week=request.form['week'], contest_id=request.form['contest_id'], outdir=f"{app.config['UPLOAD_FOLDER']}")
                flash(f"week: {request.form['week']}", category='info')
                return render_template('index.html', data_submitted=True)
            uploaded_file = request.files['file']
            # if user does not select file or
            # submits an empty part without filename
            if uploaded_file.filename == '':
                flash('Please select a file to be uploaded.', category='warning')
                return redirect(request.url)
            if uploaded_file and allowed_file(uploaded_file.filename):
                flash(f'{uploaded_file.filename} was uploaded successfully.', category='success')
                session['filename'] = secure_filename(uploaded_file.filename)
                uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], session['filename']))
                return render_template('index.html', 
                    week=weekly.get_curr_week(),
                    results_file=session['filename'],
                    contest_id=re.split('-|\.', session['filename'])[2]
                )
            else:
                flash(f'Invalid file type. Please upload CSV files only.', category='danger')
                return redirect(request.url)
        return render_template('index.html')

    @app.route('/generate', methods=['GET'])
    def generate():
        None


    return app