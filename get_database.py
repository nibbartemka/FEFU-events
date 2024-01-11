import sqlite3

conn = sqlite3.connect("event_db.sqlite")
cursor = conn.cursor()

cursor.executescript(
    '''
        DROP TABLE IF EXISTS role;

        CREATE TABLE role (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name VARCHAR(30)  
        );
    '''
)

cursor.executescript(
    '''
        DROP TABLE IF EXISTS room;

        CREATE TABLE room (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name VARCHAR(20),
            room_capacity INTEGER 
        );
    '''
)

cursor.executescript(
    '''
        DROP TABLE IF EXISTS worker;

        CREATE TABLE worker (
            worker_id VARCHAR(11) PRIMARY KEY,
            worker_name VARCHAR(30),
            role_id INTEGER,

            FOREIGN KEY (role_id) REFERENCES role (role_id) ON DELETE CASCADE  
        );
    '''
)

cursor.executescript(
    '''
        DROP TABLE IF EXISTS event;

        CREATE TABLE event (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name VARCHAR(50),
            people_amount INTEGER 
        );
    '''
)

cursor.executescript(
    '''
        DROP TABLE IF EXISTS role_event;

        CREATE TABLE role_event (
            role_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER,
            event_id INTEGER,
            role_amount INTEGER,

            FOREIGN KEY (role_id) REFERENCES role (role_id) ON DELETE CASCADE,
            FOREIGN KEY (event_id) REFERENCES event (event_id) ON DELETE CASCADE 
        );
    '''
)

cursor.executescript(
    '''
        DROP TABLE IF EXISTS event_workers;

        CREATE TABLE event_workers (
            event_workers_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_event_id INTEGER,
            worker_id VARCHAR(11),

            FOREIGN KEY (role_event_id) REFERENCES role_event (role_event_id) ON DELETE CASCADE,
            FOREIGN KEY (worker_id) REFERENCES worker (worker_id) ON DELETE CASCADE 
        );
    '''
)

cursor.executescript(
    '''
        DROP TABLE IF EXISTS schedule;

        CREATE TABLE schedule (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date DATE,
            event_id INTEGER,

            FOREIGN KEY (event_id) REFERENCES event (event_id) ON DELETE CASCADE 
        );
    '''
)

cursor.executescript(
    '''
        DROP TRIGGER IF EXISTS role_event_trigger;

        CREATE TRIGGER role_event_trigger
        AFTER INSERT
        ON role_event
        FOR EACH ROW
        BEGIN
            INSERT INTO 
                event_workers (role_event_id, worker_id)
            WITH RECURSIVE add_data (role_amount, role_event_id, worker_id)
            AS (
                SELECT
                    NEW.role_amount,
                    NEW.role_event_id,
                    NULL
                UNION ALL
                SELECT
                    role_amount - 1,
                    role_event_id,
                    NULL
                FROM
                    add_data
                WHERE
                    role_amount > 1
            )
            SELECT 
                role_event_id, 
                worker_id 
            FROM 
                add_data;
        END
       
    '''
)

cursor.executescript(
    '''
        DROP TABLE IF EXISTS room_schedule;

        CREATE TABLE room_schedule (
            room_id INTEGER,
            schedule_id INTEGER,

            PRIMARY KEY (room_id, schedule_id),
            FOREIGN KEY (room_id) REFERENCES room (room_id) ON DELETE CASCADE,
            FOREIGN KEY (schedule_id) REFERENCES schedule (schedule_id) ON DELETE CASCADE 
        );
    '''
)

conn.commit()
conn.close()