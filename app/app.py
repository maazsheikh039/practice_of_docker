from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__, template_folder='templates')

# =============================================
#   DATABASE CONFIG — sirf password bharo
# =============================================
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '1006467@Maaz',   
    'database': 'docker_app_flask'
}

# =============================================
#   DATABASE CONNECTION HELPER
# =============================================
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] Connection failed: {e}")
        return None


# =============================================
#   AUTO SETUP — DB + TABLE
# =============================================
def setup_database():
    try:
        temp_conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = temp_conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"[SETUP] Database '{DB_CONFIG['database']}' ready.")

        cursor.execute(f"USE {DB_CONFIG['database']}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                name         VARCHAR(150)  NOT NULL,
                email        VARCHAR(255)  NOT NULL,
                message      TEXT          NOT NULL,
                submitted_at DATETIME      DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[SETUP] Table 'contact_messages' ready.")

        temp_conn.commit()
        cursor.close()
        temp_conn.close()

    except Error as e:
        print(f"[SETUP ERROR] {e}")


# =============================================
#   ROUTES
# =============================================

# -- Home Page --
@app.route('/')
def index():
    return render_template('index.html')


# -- Form Submit (AJAX POST) --
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    name    = (data.get('name')    or '').strip()
    email   = (data.get('email')   or '').strip()
    message = (data.get('message') or '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'error': 'Tamam fields bharna zaroori hain.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database se connect nahi ho saka.'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Message database mein save ho gaya!'})

    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# -- Admin: View All Messages --
@app.route('/messages')
def view_messages():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact_messages ORDER BY submitted_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    for row in rows:
        if isinstance(row.get('submitted_at'), datetime):
            row['submitted_at'] = row['submitted_at'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify(rows)


# =============================================
#   ENTRY POINT
# =============================================
if __name__ == '__main__':
    setup_database()
    app.run(debug=True, port=5000)