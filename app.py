import datetime
import threading
from flask import Flask, render_template, redirect, url_for, jsonify, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, User  # Import từ model.py

from f_sql import *
from read_sensor import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            print(f'User {username} logged in successfully')  # Debug log
            return jsonify({'success': True, 'message': 'Đăng nhập thành công!', 'redirect': url_for('home')}), 200
        else:
            flash('Sai tài khoản hoặc mật khẩu', 'danger')
            print('Invalid credentials')  # Debug log
            return jsonify({'success': False, 'message': 'Sai tài khoản hoặc mật khẩu'}), 401
    return render_template('login.html')


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/setting')
def setting():
    return render_template('setting.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/get_data_chart', methods=['GET'])
def get_data_chart():
    return jsonify({
        "temperature": get_sensor_data("temp"),
        "humidity": get_sensor_data("humi"),
        "soil_moisture": get_sensor_data("soil"),
        "co2": get_sensor_data("co2")
    })

@app.route('/api/latest', methods=['GET'])
def get_latest_data():
    return jsonify(fetch_latest())

@app.route('/api/get_setting', methods=['GET'])
def get_settings():
    return jsonify(fetch_get_table('table_setting'))

@app.route('/api/get_control', methods=['GET'])
def get_control():
    return jsonify(fetch_get_table('table_actualtor'))

@app.route('/api/set_status_control', methods=['GET'])
def set_status_control():
    object_t = request.args.get('object')
    status_t = request.args.get('status')
    status_o = "ON"
    if status_t == "ON":
        status_o = "OFF"
    update_actualtor(object_t, status_o)
    print(f"{object_t} đã được đặt thành {status_o}")
    controll_relay()
    return jsonify({"message": f"{object_t} đã được đặt thành {status_o}"})

@app.route('/api/set_mode', methods=['GET'])
def set_mode():
    mode_t = request.args.get('mode')
    if mode_t == "AUTO":
        mode_t = "MANUAL"
    else:
        mode_t = "AUTO"
    update_actualtor('mode', mode_t)
    return jsonify({"message": f"mode đã được đặt thành {mode_t}"})

@app.route('/api/set_value_setting', methods=['GET'])
def set_value_setting():
    temp = request.args.get('temp')
    update_setting('temp', float(temp))

    humi = request.args.get('humi')
    update_setting('humi', float(humi))

    soil = request.args.get('soil')
    update_setting('soil', float(soil))

    co2 = request.args.get('co2')
    update_setting('co2', float(co2))

    light = request.args.get('light')
    update_setting('light', float(light))

    return jsonify({"message": "Successfull"})


@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    # Kiểm tra mật khẩu hiện tại
    if not check_password_hash(current_user.password, current_password):
        return jsonify({"success": False, "message": "Mật khẩu hiện tại không đúng"}), 400

    # Kiểm tra mật khẩu mới có khớp không
    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Mật khẩu mới không khớp"}), 400

    # Cập nhật mật khẩu mới
    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()

    return jsonify({"success": True, "message": "Mật khẩu đã được cập nhật thành công"}), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Bạn đã đăng xuất thành công!"}), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Lấy dữ liệu JSON từ frontend
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Vui lòng nhập đầy đủ thông tin!"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "Tên đăng nhập đã tồn tại!"}), 400

    # Mã hóa mật khẩu trước khi lưu vào DB
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "Đăng ký thành công! Vui lòng đăng nhập."}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tạo database nếu chưa có

    # Thread
    thread_s = threading.Thread(target=thread_sensor, daemon=True)
    thread_s.start()

    app.run(host="0.0.0.0", port=5000, debug=True)

