
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql  # MySQL 用
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションを使うために必要

#ルーティングの確認
@app.route('/')
def home():
    return "Hello, Flask is running on AWS!"


# データベース接続のヘルパー関数
# RDS の接続情報
DB_HOST = "household-budget-db.cd8wawccuqal.ap-northeast-3.rds.amazonaws.com"
DB_NAME = "household_budget_db"
DB_USER = "admin"
DB_PASS = "9agj3CRr6tX3GgfwZier"
def get_db_connection():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

# ユーザー登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password,method="pbkdf2:sha256")

        conn = get_db_connection()
        cursor = conn.cursor()

        # 既に登録されているメールアドレスがないかチェック
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "このメールアドレスは既に登録されています。別のメールアドレスを使用してください。"

        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, hashed_password))
        conn.commit()
        conn.close()

        flash('アカウントが作成されました。ログインしてください。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = user['is_admin']  # 管理者フラグをセッションに保存
            flash('ログイン成功！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('メールアドレスまたはパスワードが間違っています。', 'danger')

    return render_template('login.html')

# ダッシュボード
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # 月ごとの支出・収入を集計
    cursor.execute('''
    SELECT DATE_FORMAT(date, '%%Y-%%m') AS month, 
            SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) AS income,
            SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) AS expense
    FROM transactions 
    WHERE user_id = %s
    GROUP BY month
    ORDER BY month DESC
''', (session['user_id'],))

    
    monthly_totals = cursor.fetchall()

    # 取引履歴（最新月のデータを取得）
    cursor.execute('''
        SELECT t.id, t.date, c.name AS category_name, t.amount, pm.name AS payment_method, t.note
        FROM transactions t
        JOIN categories c ON t.category = c.id
        LEFT JOIN payment_methods pm ON t.payment_method = pm.name
        WHERE t.user_id = %s 
        ORDER BY t.date DESC
    ''', (session['user_id'],))
    
    

    transactions = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', transactions=transactions, monthly_totals=monthly_totals)



# **🔹 編集機能**
@app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # 該当する取引を取得
    cursor.execute('SELECT * FROM transactions WHERE id = %s AND user_id = %s', (id, session['user_id']))
    transaction = cursor.fetchone()

    # カテゴリーデータを取得
    categories = cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall()

    #支払い方法データを取得
    payment_methods = cursor.execute('SELECT * FROM payment_methods')
    payment_methods = cursor.fetchall() 

    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = int(request.form['amount'])
        payment_method = request.form.get('payment_method') if request.form['transaction_type'] == 'expense' else None
        note = request.form['note']

        cursor.execute('''UPDATE transactions SET date = %s, category = %s, amount = %s, payment_method = %s, note = %s 
                          WHERE id = %s AND user_id = %s''', 
                       (date, category, amount, payment_method, note, id, session['user_id']))
        conn.commit()
        conn.close()

        flash('データが更新されました。', 'success')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_transaction.html', transaction=transaction, categories=categories,payment_methods=payment_methods)

# **🔹 削除機能**
@app.route('/delete_transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # **ログイン中の `user_id` のデータのみ削除可能**
    cursor.execute('DELETE FROM transactions WHERE id = %s AND user_id = %s', (id, session['user_id']))
    
    conn.commit()
    conn.close()

    flash('データが削除されました。', 'success')
    return redirect(url_for('dashboard'))


# 家計簿データの追加
@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # ログインしていない場合はログインページへ

    conn = get_db_connection()
    cursor = conn.cursor()

    # カテゴリー一覧を取得
    cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall() or []

    # 支払い方法一覧を取得（payment_methods テーブルから）
    cursor.execute('SELECT * FROM payment_methods')
    payment_methods = cursor.fetchall() or []

    if request.method == 'POST':
        date = request.form['date']
        category = request.form.get('category', '0')  # カテゴリーIDを取得
        amount_str = request.form.get('amount', '0')  # 文字列として取得
        if not amount_str.isdigit():  # ここで整数チェック
            flash('金額は整数のみ入力してください。', 'danger')
            return redirect(url_for('add_transaction'))

        amount = int(amount_str)  # ここで初めて int に変換

        transaction_type = request.form['transaction_type']  # 収入か支出か
        note = request.form['note']


        # 収入の場合は支払い方法を設定しない
        payment_method = request.form.get('payment_method') if transaction_type == 'expense' else None

        # データを追加
        cursor.execute('''
            INSERT INTO transactions (user_id, date, category, amount, payment_method, note)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (session['user_id'], date, category, amount, payment_method, note))

        conn.commit()
        conn.close()

        flash('データが追加されました。', 'success')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('add_transaction.html', categories=categories,  payment_methods=payment_methods)

#管理者専用の管理画面
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash("管理者権限が必要です。", "danger")
        return redirect(url_for('dashboard'))

    return render_template('admin_dashboard.html')


#管理者のみがカテゴリー・支払い方法を変更
def is_admin():
    """現在のユーザーが管理者かどうかを判定"""
    return 'user_id' in session and session.get('is_admin') == 1

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if not is_admin():
        flash("管理者のみがカテゴリーを追加できます。", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        category_name = request.form['category_name'].strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM categories WHERE name = %s', (category_name,))
        existing_category = cursor.fetchone()

        if existing_category:
            flash('このカテゴリーはすでに存在します。', 'warning')
        else:
            cursor.execute('INSERT INTO categories (name) VALUES (%s)', (category_name,))
            conn.commit()
            flash('カテゴリーが追加されました！', 'success')

        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('add_category.html')

@app.route('/add_payment_method', methods=['GET', 'POST'])
def add_payment_method():
    if not is_admin():
        flash("管理者のみが支払い方法を追加できます。", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        payment_method_name = request.form['payment_method_name'].strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM payment_methods WHERE name = %s', (payment_method_name,))
        existing_method = cursor.fetchone()

        if existing_method:
            flash('この支払い方法はすでに存在します。', 'warning')
        else:
            cursor.execute('INSERT INTO payment_methods (name) VALUES (%s)', (payment_method_name,))
            conn.commit()
            flash('支払い方法が追加されました！', 'success')

        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('add_payment_method.html')


# ログアウト
@app.route('/logout')
def logout():
    session.clear()  # セッションをクリア
    flash('ログアウトしました。', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)





