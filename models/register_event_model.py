import pandas

def get_roles(conn):
    return pandas.read_sql(
        '''
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

def get_all_role_id(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT role_id FROM role WHERE role_name <> 'Организатор' ")
    role_id = [int(row[0]) for row in cursor.fetchall()]
    cursor.close()
    return role_id 

def get_min_date(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(event_date) FROM schedule")
    min_date = cursor.fetchone()[0]
    cursor.close()
    return min_date

def get_max_date(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(event_date) FROM schedule")
    max_date = cursor.fetchone()[0]
    cursor.close()
    return max_date  

def get_events(conn, date_from, date_to, selected_roles):
    return pandas.read_sql(
        f'''
            WITH get_worker_count (role_event_id, worker_count)
            AS (
                SELECT
                    role_event_id,
                    COUNT(worker_id)
                FROM
                    event_workers
                GROUP BY
                    role_event_id
            )

            SELECT
                event_id,
                event_name,
                event_date,
                role_id,
                role_name,
                worker_count,
                role_amount
            FROM
                schedule
                JOIN event USING (event_id)
                JOIN role_event USING (event_id)
                JOIN role USING (role_id)
                JOIN get_worker_count USING (role_event_id)
            WHERE
                role_name <> 'Организатор'
                AND role_id IN {'({})'.format(', '.join([str(elem) for elem in selected_roles]))}
                AND strftime('%Y-%m-%d', event_date) BETWEEN '{date_from}' AND '{date_to}'
            ORDER BY
                event_date,
                event_name
        ''',
        conn
    )

def register_worker(conn, event_id, role_id, worker_id):
    conn.executescript(
        f'''
            WITH get_role_event_id (role_event_id)
            AS (
                SELECT
                    role_event_id
                FROM
                    role_event
                WHERE
                    event_id = {event_id}
                    AND role_id = {role_id}
            ),
            get_event_workers_id (event_workers_id)
            AS (
                SELECT
                    event_workers_id
                FROM 
                    event_workers 
                    JOIN get_role_event_id USING (role_event_id)
                WHERE
                    worker_id IS NULL
                LIMIT 1
            )

            UPDATE 
                event_workers AS ew
            SET 
                worker_id = {worker_id}
            FROM
                get_event_workers_id AS cte
            WHERE
                ew.event_workers_id = cte.event_workers_id
        '''
    )
