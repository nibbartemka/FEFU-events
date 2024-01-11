import pandas

def get_room_dates(conn, date_from, date_to):
    return pandas.read_sql(
        f'''
            WITH RECURSIVE create_date(event_date)
            AS (
                SELECT '{date_from}'
                UNION ALL
                SELECT DATE(event_date, '+1 day')
                FROM create_date
                WHERE event_date < '{date_to}'
            ),
            get_occupied_date_count(room_id, occupied_date_count)
            AS (
                SELECT
                    room_id,
                    COUNT(event_date)
                FROM
                    room
                    JOIN room_schedule USING (room_id)
                    JOIN schedule USING (schedule_id)
                    JOIN create_date USING (event_date)
                GROUP BY
                    room_id
            ),
            get_all_date_count(date_count)
            AS (
                SELECT
                    COUNT(event_date)
                FROM
                    create_date
            )

            SELECT
                room_id,
                room_name,
                date_count - occupied_date_count AS free_date_count
            FROM
                room
                JOIN get_occupied_date_count USING (room_id),
                get_all_date_count
            UNION
            SELECT
                room_id,
                room_name,
                date_count AS free_date_count
            FROM
                room,
                get_all_date_count
            WHERE
                room_id NOT IN (SELECT room_id FROM get_occupied_date_count)
            ORDER BY
                room_id
        ''',
        conn
    )

def get_free_dates(conn, room_id, date_from, date_to):
    return pandas.read_sql(
        f'''
            WITH RECURSIVE create_date(event_date)
            AS (
                SELECT '{date_from}'
                UNION ALL
                SELECT DATE(event_date, '+1 day')
                FROM create_date
                WHERE event_date < '{date_to}'
            ),
            get_occupied_date(occupied_date)
            AS (
                SELECT
                    event_date
                FROM
                    room
                    LEFT JOIN room_schedule USING (room_id)
                    LEFT JOIN schedule USING (schedule_id)
                    JOIN create_date USING (event_date)
                WHERE
                    room_id = {room_id}
            )

            SELECT
                event_date
            FROM
                create_date
            WHERE
                event_date NOT IN (SELECT occupied_date FROM get_occupied_date)
        ''',
        conn
    )

def get_date_rooms(conn, date_from, date_to):
    return pandas.read_sql(
        f'''
            WITH RECURSIVE create_date(event_date)
            AS (
                SELECT '{date_from}'
                UNION ALL
                SELECT DATE(event_date, '+1 day')
                FROM create_date
                WHERE event_date < '{date_to}'
            ),
            get_schedule_id (schedule_id, event_date)
            AS (
                SELECT
                    schedule_id,
                    event_date
                FROM
                    create_date
                    LEFT JOIN schedule USING (event_date)
            ),
            get_occupied_room_count(event_date, occupied_room_count)
            AS (
                SELECT
                    event_date,
                    COUNT(room_id)
                FROM
                    get_schedule_id
                    LEFT JOIN room_schedule USING (schedule_id)
                GROUP BY
                    event_date
            ),
            get_all_room_count(room_count)
            AS (
                SELECT
                    COUNT(room_id)
                FROM
                    room
            )

            SELECT
                event_date,
                room_count - occupied_room_count AS free_room_count
            FROM
                get_all_room_count,
                get_occupied_room_count
        ''',
        conn
    )

def get_free_rooms(conn, date):
    return pandas.read_sql(
        f'''
            WITH occupied_rooms (room_id)
            AS (
                SELECT
                    room_id
                FROM
                    room
                    JOIN room_schedule USING (room_id)
                    JOIN schedule USING (schedule_id)
                WHERE
                    strftime('%Y-%m-%d', event_date) = '{date}'
            )

            SELECT
                room_id,
                room_name || " - " || room_capacity AS full_room_name
            FROM
                room
            WHERE
                room_id NOT IN (
                    SELECT
                        room_id
                    FROM
                        occupied_rooms
                )
        ''',
        conn
    )

def get_roles(conn):
    return pandas.read_sql(
        f'''
            SELECT
                role_id,
                role_name
            FROM
                role
            WHERE
                role_name <> 'Организатор'
        ''',
        conn
    )

def get_new_event(conn, new_event):
    cur = conn.cursor()
    cur.execute(
        '''
            INSERT INTO event (event_name)
            VALUES (:new_event)
        ''',
        {"new_event": new_event}
    )
    conn.commit()
    return cur.lastrowid

def get_role_event(conn, event_id):
    cur = conn.cursor()
    cur.execute(
        ''' 
            INSERT INTO role_event (role_id, event_id, role_amount)
            VALUES 
                (5, :event_id, 1)
        ''',
        {"event_id":event_id}
    )
    conn.commit()
    return cur.lastrowid

def set_manager(conn, manager_id, role_event_id):
    cur = conn.cursor()
    cur.execute(
        '''
            UPDATE event_workers
            SET worker_id = :manager_id
            WHERE role_event_id = :role_event_id
        ''',
        {"manager_id":manager_id, "role_event_id":role_event_id}
    )
    conn.commit()

def get_new_schedule(conn, event_date, event_id):
    cur = conn.cursor()
    cur.execute(
        ''' 
            INSERT INTO schedule (event_date, event_id)
            VALUES 
                (:event_date, :event_id)
        ''',
        {"event_date":event_date, "event_id":event_id}
    )
    conn.commit()
    return cur.lastrowid

def add_role(conn, event_id, role_id, role_amount):
    cur = conn.cursor()
    cur.execute(
        ''' 
            INSERT INTO role_event (role_id, event_id, role_amount)
            VALUES 
                (:role_id, :event_id, :role_amount)
        ''',
        {"event_id":event_id, "role_id":role_id, "role_amount":role_amount}
    )
    conn.commit()

def add_room(conn, schedule_id, room_id):
    cur = conn.cursor()
    cur.execute(
        ''' 
            INSERT INTO room_schedule (room_id, schedule_id)
            VALUES 
                (:room_id, :schedule_id)
        ''',
        {"room_id":room_id, "schedule_id":schedule_id}
    )
    conn.commit()