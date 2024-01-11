from app import app
from flask import render_template, request
from utils import get_db_connection
from models.register_event_model import get_roles, get_events, get_all_role_id, get_min_date, get_max_date, register_worker
from datetime import date, timedelta


@app.route('/register_event', methods=['GET', 'POST'])
def register_event():
    conn = get_db_connection()

    min_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    date_from = ''
    date_to = ''
    selected_roles = []

    register_event_id = -1
    register_role_id = -1

    action_response = ''

    if request.method == 'POST':
        if 'find' in request.form:
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            selected_roles = [int(x) for x in request.form.getlist('role')]
            action_response = ''
            register_event_id = -1
            register_role_id = -1
        if 'enter' in request.form:
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            selected_roles = [int(x) for x in request.form.get('role')[1:-1].split(',')]
            register_event_id = int(request.values.get('event_id'))
            register_role_id = int(request.values.get('role_id'))
            action_response = ''
        if 'register' in request.form:
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            selected_roles = [int(x) for x in request.form.get('role')[1:-1].split(',')]
            register_event_id = int(request.values.get('event_id'))
            register_role_id = int(request.values.get('role_id'))
            register_worker_id = request.values.get('worker_id')

            register_worker(conn, register_event_id, register_role_id, register_worker_id)

            action_response = 'Вы были успешно зарегистрированы!'
            register_event_id = -1
            register_role_id = -1


    df_roles = get_roles(conn)
    df_events = get_events(
        conn, 
        date_from if date_from else get_min_date(conn), 
        date_to if date_to else get_max_date(conn), 
        selected_roles if selected_roles else get_all_role_id(conn)
    )

    html = render_template(
        'register_event.html',
        df_roles=df_roles,
        df_events=df_events,
        min_date=min_date,
        date_to=date_to,
        date_from=date_from,
        selected_roles=selected_roles,
        register_event_id=register_event_id,
        register_role_id=register_role_id,
        action_response=action_response,
        len=len,
    )
    return html
