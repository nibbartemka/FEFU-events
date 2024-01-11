import pandas

def get_manager(conn):
    return pandas.read_sql (
        '''
            SELECT 
                worker_id,
                worker_name
            FROM 
                worker
                JOIN role USING (role_id)
            WHERE
                role_name = 'Организатор'
        ''', 
        conn
    )

def get_events_view(conn, manager_id):
    return pandas.read_sql(
        f'''
            WITH get_schedule_id
            AS (
                SELECT
                    schedule_id
                FROM
                    worker
                    JOIN event_workers USING (worker_id)
                    JOIN role_event USING (role_event_id)
                    JOIN event USING (event_id)
                    JOIN schedule USING (event_id)
                WHERE
                    event_date >= DATE('NOW')
                    AND worker_id = '{manager_id}'
            ), 
            get_rooms (schedule_id, full_room_name)
            AS (
                SELECT
                    schedule_id,
                    room_name || ' - ' || room_capacity
                FROM
                    room_schedule
                    JOIN room USING (room_id)
            ),
            get_worker_count (role_event_id, worker_count)
            AS (
                SELECT
                    role_event_id,
                    COUNT(worker_id)
                FROM
                    event_workers
                GROUP BY
                    role_event_id
            ),
            get_roles (event_id, full_role_name)
            AS (
                SELECT
                    event_id,
                    role_name || ' - ' || worker_count || '/' || role_amount
                FROM
                    role_event
                    JOIN get_worker_count USING (role_event_id)
                    JOIN role USING (role_id)
                WHERE
                    role_name <> 'Организатор'
            ),
            cte_a (schedule_id, event_name, event_date)
            AS (
                SELECT
                    schedule_id,
                    event_name,
                    event_date
                FROM
                    get_schedule_id
                    JOIN schedule USING (schedule_id)
                    JOIN event USING (event_id)
            ),
            cte_b (schedule_id, group_role)
            AS (
                SELECT
                    schedule_id,
                    GROUP_CONCAT(full_role_name, ', ')
                FROM
                    get_schedule_id
                    JOIN schedule USING (schedule_id)
                    JOIN event USING (event_id)
                    JOIN get_roles USING (event_id)
                GROUP BY
                    schedule_id
            ),
            cte_c (schedule_id, group_room)
            AS (
                SELECT
                    schedule_id,
                    GROUP_CONCAT(full_room_name, ', ')
                FROM
                    get_schedule_id
                    JOIN schedule USING (schedule_id)
                    JOIN get_rooms USING (schedule_id)
                GROUP BY
                    schedule_id
            )

            SELECT
                schedule_id,
                event_name AS Название,
                event_date AS Дата,
                group_room AS Аудитории,
                group_role AS Состав
            FROM
               cte_a 
               LEFT JOIN cte_b USING (schedule_id)
               LEFT JOIN cte_c USING (schedule_id)
        ''',
        conn
    )

def get_free_rooms(conn, schedule_id, date):
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
                    schedule_id <> {schedule_id}
                    AND strftime('%Y-%m-%d', event_date) = '{date}'
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

def get_roles(conn, schedule_id):
    return pandas.read_sql(
        f'''
            WITH cte (role_id, event_id)
            AS (
                SELECT
                    role_id, event_id
                FROM
                    role
                    JOIN role_event USING (role_id)
                    JOIN event USING (event_id)
                    JOIN schedule USING (event_id)
                WHERE
                    schedule_id = {schedule_id}
            )
        
            SELECT
                role_id,
                role_name,
                role_amount
            FROM
                role
                JOIN role_event USING (role_id)
                JOIN cte USING (event_id, role_id)
            WHERE
                role_name <> 'Организатор'
            UNION
            SELECT
                role_id,
                role_name, 
                0
            FROM
                role
            WHERE
                role_id NOT IN (SELECT role_id FROM cte)
            ORDER BY
                role_amount DESC
        ''',
        conn
    )

def del_event_rooms(conn, schedule_id):
    cursor = conn.cursor()
    cursor.executescript(
        f'''
            DELETE 
            FROM room_schedule
            WHERE
                schedule_id = {schedule_id}
        ''')
    conn.commit()

def add_event_room(conn, room_id, schedule_id):
    cursor = conn.cursor()
    cursor.executescript(
        f'''
            INSERT INTO room_schedule (room_id, schedule_id)
            VALUES
                ({room_id}, {schedule_id})
        ''')
    conn.commit()

def get_selected_rooms(conn, schedule_id):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT 
                room_id 
            FROM 
                room_schedule 
            WHERE 
                schedule_id = {schedule_id} 
        ''')
    room_id = [int(row[0]) for row in cursor.fetchall()]
    cursor.close()
    return room_id

def get_filled_roles(conn, schedule_id):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT
                role_id
            FROM
                role
                JOIN role_event USING (role_id)
                JOIN event USING (event_id)
                JOIN schedule USING (event_id)
            WHERE
                schedule_id = {schedule_id}
        ''')
    role_id = [int(row[0]) for row in cursor.fetchall()]
    cursor.close()
    return role_id

def get_new_manager(conn, id, name):
    cur = conn.cursor()
    cur.execute(
        '''
            INSERT INTO worker (worker_id, worker_name, role_id)
            VALUES (:worker_id, :worker_name, 5)
        ''',
        {"worker_id": id, "worker_name": name}
    )
    conn.commit()
    return id

def get_event_id(conn, schedule_id):
    cursor = conn.cursor()
    cursor.execute(f"SELECT event_id FROM schedule WHERE schedule_id = {schedule_id}")
    event_id = cursor.fetchone()[0]
    cursor.close()
    return event_id  

def get_role_id(conn):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT
                role_id
            FROM
                role
            WHERE
                role_name <> 'Организатор'
        ''')
    role_id = [int(row[0]) for row in cursor.fetchall()]
    cursor.close()
    return role_id

def add_role_event(conn, role_id, role_amount, event_id):
    cur = conn.cursor()
    cur.execute(
        '''
            INSERT INTO role_event (role_id, event_id, role_amount)
            VALUES (:role_id, :event_id, :role_amount)
        ''',
        {"role_id": role_id, "event_id": event_id, "role_amount": role_amount}
    )
    conn.commit()