from app import app
from flask import render_template, request, session
from utils import get_db_connection
from models.index_model import get_manager, get_events_view, \
    get_new_manager, get_free_rooms, get_selected_rooms, del_event_rooms, \
    add_event_room, get_roles, get_role_id, get_event_id, add_role_event


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()

    if 'manager_id' not in session:
        session['manager_id'] = '89140000005'
        
    schedule_id = -1
    edit_field = ''

    df_rooms = []
    selected_rooms = []

    df_roles = []

    if request.method == 'POST':
        if 'room_edit' in request.form:
            edit_field = 'room'
            schedule_id = int(request.values.get('schedule_id'))
            event_date = request.values.get('event_date')
            df_rooms = get_free_rooms(conn, schedule_id, event_date)
            selected_rooms = get_selected_rooms(conn, schedule_id)
        elif 'role_edit' in request.form:
            edit_field = 'role'
            schedule_id = int(request.values.get('schedule_id'))
            df_roles = get_roles(conn, schedule_id)
        elif 'cancel' in request.form:
            edit_field = ''
            schedule_id = -1
        elif 'room_save' in request.form:
            schedule_id = int(request.values.get('schedule_id'))
            selected_rooms = [int(room) for room in request.values.getlist('rooms')]

            del_event_rooms(conn, schedule_id)
            for room_id in selected_rooms:
                add_event_room(conn, room_id, schedule_id)

            edit_field = ''
            schedule_id = -1
        elif 'role_save' in request.form:
            schedule_id = int(request.values.get('schedule_id'))
            all_role_id = get_role_id(conn)
            event_id = get_event_id(conn, schedule_id)
            new_roles = {}
            for role in all_role_id:
                count_ = request.values.get(str(role))
                if count_:
                    count_ = int(count_)
                    if count_ > 0:
                        new_roles[role] = count_
            
            for key, value in new_roles.items():
                add_role_event(conn, key, value, event_id)

            edit_field = ''
            schedule_id = -1

    elif request.values.get('new_manager_id') and request.values.get('new_manager_name'):
        new_manager_id = request.values.get('new_manager_id')
        new_manager_name = request.values.get('new_manager_name')
        session['manager_id'] = get_new_manager(conn, new_manager_id, new_manager_name)
    else:
        if request.values.get('manager'):
            session['manager_id'] = request.values.get('manager')         
    
    df_manager = get_manager(conn)
    df_events = get_events_view(conn, session['manager_id'])

    html = render_template(
        'index.html',
        manager_id=session['manager_id'],
        combo_box=df_manager,
        df_events=df_events,
        edit_field=edit_field,
        schedule_id=schedule_id,
        df_rooms=df_rooms,
        df_roles=df_roles,
        selected_rooms=selected_rooms,
        len=len,
    )
    
    return html