import sqlite3
import time

def creat_database():
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_sensor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parameter TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp DATATIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_setting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parameter TEXT NOT NULL,
            value_setting REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_actualtor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def insert_table_sensor(parameter, value):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO table_sensor (parameter, value) VALUES (?, ?)", 
        (parameter, value)
    )
    conn.commit()
    conn.close()

def insert_table_setting(parameter, value):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO table_setting (parameter, value_setting) VALUES (?, ?)", 
        (parameter, value)
    )
    conn.commit()
    conn.close()

def insert_table_actualtor(object_t, status):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO table_actualtor (object, status) VALUES (?, ?)", 
        (object_t, status)
    )
    conn.commit()
    conn.close()

def clear_sensor_data():
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM table_sensor")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='table_sensor'")
    conn.commit()

    cursor.execute("DELETE FROM table_actualtor")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='table_actualtor'")
    conn.commit()

    cursor.execute("DELETE FROM table_setting")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='table_setting'")
    conn.commit()

    conn.close()
    print("Đã xóa toàn bộ dữ liệu trong bảng.")

def fetch_data():
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM table_sensor")
    rows = cursor.fetchall()

    cursor.execute("SELECT * FROM table_actualtor")
    rows1 = cursor.fetchall()

    cursor.execute("SELECT * FROM table_setting")
    rows2 = cursor.fetchall()
    
    conn.close()

    # Lấy dữ liệu và hiển thị
    for row in rows:
        print(row)

    # Lấy dữ liệu và hiển thị
    for row in rows1:
        print(row)

    for row in rows2:
        print(row)

def fetch_latest():
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    # Truy vấn lấy giá trị mới nhất của từng loại cảm biến
    cursor.execute("""
        SELECT parameter, value, timestamp 
        FROM table_sensor 
        WHERE timestamp = (SELECT MAX(timestamp) FROM table_sensor AS t WHERE t.parameter = table_sensor.parameter)
    """)

    rows = cursor.fetchall()
    conn.close()

    # Chuyển kết quả thành dictionary
    latest_data = {row[0]: {"value": row[1], "timestamp": row[2]} for row in rows}
    return latest_data

def fetch_get_table(table_name):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    if(table_name == 'table_setting'):
        # Truy vấn tất cả giá trị từ bảng `table_setting`
        cursor.execute(f"SELECT parameter, value_setting FROM {table_name}")
    else:
        cursor.execute(f"SELECT object, status FROM {table_name}")

    rows = cursor.fetchall()
    conn.close()

    # Chuyển kết quả thành dictionary
    settings = {row[0]: row[1] for row in rows}
    return settings

# Hàm lấy dữ liệu cảm biến theo từng loại, sắp xếp theo thời gian
def get_sensor_data(sensor_type):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, value FROM table_sensor
        WHERE parameter = ? 
        ORDER BY timestamp ASC
        LIMIT 50
    """, (sensor_type,))

    rows = cursor.fetchall()
    conn.close()

    # Trả về danh sách JSON { "timestamp": ..., "value": ... }
    return [{"timestamp": row[0], "value": row[1]} for row in rows]


# Table Actualtor
def update_actualtor(object_t, new_status):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE table_actualtor
        SET status = ? 
        WHERE object = ?
    """, (new_status, object_t))

    conn.commit()
    conn.close()

def fetch_get_mode():
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status FROM table_actualtor WHERE object = 'mode'
    """)

    mode = cursor.fetchall
    conn.close()
    return mode


# Table Setting
def update_setting(parameter, value):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE table_setting
        SET value_setting = ? 
        WHERE parameter = ?
    """, (value, parameter))

    conn.commit()
    conn.close()