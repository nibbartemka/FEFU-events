from app import app
from flask import render_template, request

@app.route('/new_manager', methods=['GET', 'POST'])
def new_manager():

    html = render_template(
        'new_manager.html',
    )
    return html
