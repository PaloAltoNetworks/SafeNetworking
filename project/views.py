from flask import Blueprint, render_template


sfn_blueprint = Blueprint('sfn', __name__, template_folder='./templates')
@sfn_blueprint.route('/')
def index():
    return render_template('index.html')
