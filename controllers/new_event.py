from app import app
from flask import render_template, request, session
from utils import get_db_connection
from models.new_event_model import get_free_rooms, get_roles, \
    get_new_event, get_role_event, set_manager, get_new_schedule, \
    add_role, add_room, get_date_rooms, get_room_dates, get_free_dates
from datetime import date, timedelta


@app.route('/new_event', methods=['GET', 'POST'])
def new_event():
    conn = get_db_connection()

    min_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    entered_role_count = {key:0 for key in get_roles(conn)['role_id']}

    add_check = False

    if 'is_date_state' not in session:
        session['is_date_state'] = True
    if 'selected_room_id' not in session:
        session['selected_room_id'] = []
    if 'event_date' not in session:
        session['event_date'] = ''
    if 'date_from' not in session:
        session['date_from'] = min_date
    if 'date_to' not in session:
        session['date_to'] = min_date
    if 'event_name' not in session:
        session['event_name'] = ''
    if 'room_id' not in session:
        session['room_id'] = -1


    if request.method == 'POST': 
        if 'find' in request.form:
            session['event_name'] = request.form.get('event_name')
            session['date_from'] = request.form.get('date_from')
            session['date_to'] = request.form.get('date_to')
        elif 'change_mode' in request.form:
            session['event_name'] = request.form.get('event_name')
            if request.form['change_mode'] == 'Искать по аудитории':
                session['is_date_state'] = False
            elif request.form['change_mode'] == 'Искать по дате':
                session['is_date_state'] = True
        elif 'date_next' in request.form:
            session['event_name'] = request.form.get('event_name')
            session['event_date'] = request.form.get('event_date')
        elif 'room_next' in request.form:
            session['event_name'] = request.form.get('event_name')
            session['room_id'] = int(request.form.get('room_id'))
        elif 'add' in request.form:
            session['event_name'] = request.form.get('event_name')
            if session['is_date_state']:
                session['selected_room_id']  = [int(x) for x in request.form.getlist('free_rooms')]
            else:
                session['event_date'] = request.form.get('event_date')
            add_check = True

            print(session['event_date'], session['event_name'])

            if session['event_date'] and session['event_name']:
                added_event = get_new_event(conn, session['event_name'])
                role_event_id = get_role_event(conn, added_event)
                
                set_manager(conn, session['manager_id'], role_event_id)
                
                schedule_id = get_new_schedule(conn, session['event_date'], added_event)
                for i in entered_role_count.keys():
                    entered_role_count[i] = int(request.form.get(f'{i}'))

                for i in entered_role_count.keys():
                    if entered_role_count[i]:
                        add_role(conn, added_event, i, entered_role_count[i])
                
                if session['is_date_state']:
                    for room_id in session['selected_room_id']:
                        add_room(conn, schedule_id, room_id)
                else:
                    add_room(conn, schedule_id, session['room_id'])
            
        elif 'new_event' in request.form:
            session['date_from'] = min_date
            session['date_to'] = min_date
            session['event_name'] = ''
            session['event_date'] = ''
            session['selected_room_id'] = []
            session['is_date_state'] = True
            session['room_id'] = -1
   
    df_roles = get_roles(conn)
    df_date_rooms = get_date_rooms(conn,  session['date_from'],  session['date_to'])
    df_free_rooms = get_free_rooms(conn,  session['event_date'])
    df_room_dates = get_room_dates(conn,  session['date_from'],  session['date_to'])
    df_free_dates = get_free_dates(conn, session['room_id'], session['date_from'],  session['date_to'])

    html = render_template(
        'new_event.html',
        event_name=session['event_name'],
        event_date= session['event_date'],
        min_date=min_date,
        df_free_rooms=df_free_rooms,
        room_id=session['room_id'],
        selected_room_id=session['selected_room_id'],
        entered_role_count=entered_role_count,
        add_check=add_check,
        df_roles=df_roles,
        date_from=session['date_from'],
        date_to=session['date_to'],
        is_date_state=session['is_date_state'],
        df_date_rooms=df_date_rooms,
        df_room_dates=df_room_dates,
        df_free_dates=df_free_dates,
        len=len,
    )
    return html
