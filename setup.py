from f_sql import *
from model import *  # Import từ model.py
from app import app, db

def creat_database_senser():
    try:
        clear_sensor_data()
    except:
        print('Khong co database, Tu dong tao moi')
    creat_database()
    insert_table_sensor("temp", 25.6)
    insert_table_sensor("humi", 30.3)
    insert_table_sensor("soil", 11.1)
    insert_table_sensor("co2", 0.23)
    insert_table_sensor("light", 1)

    insert_table_actualtor("mode", "AUTO")
    insert_table_actualtor("pump", "ON")
    insert_table_actualtor("led", "ON")
    insert_table_actualtor("fan", "ON")

    insert_table_setting("temp", 25.6)
    insert_table_setting("humi", 30.3)
    insert_table_setting("soil", 11.1)
    insert_table_setting("co2", 0.23)
    insert_table_setting("light", 1)

    fetch_data()

def setup_database():
    with app.app_context():
        # Tạo bảng nếu chưa có
        db.create_all()
        print("✅ Database và bảng đã được tạo!")

        # Kiểm tra xem user "admin" đã tồn tại chưa
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            hashed_password = generate_password_hash("1234")
            new_user = User(username="admin", password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            print("✅ Người dùng mặc định 'admin' đã được tạo!")

if __name__ == "__main__":
    setup_database()
    creat_database_senser()