import sqlite3
from werkzeug.security import generate_password_hash

# データベースファイルを作成（なければ自動生成）
conn = sqlite3.connect('household_budget.db')
cursor = conn.cursor()

# ユーザーテーブル
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# カテゴリテーブル
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# 支払い方法のテーブルを作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
''')

# 家計簿テーブル
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    category INTEGER,
    amount REAL NOT NULL,
    payment_methods INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(category) REFERENCES categories(id),
    FOREIGN KEY(payment_methods) REFERENCES payment_methods(id)
);
''')

# `type` カラムを追加（既にある場合はスキップ）
try:
    cursor.execute("ALTER TABLE transactions ADD COLUMN type TEXT DEFAULT 'expense'")
    conn.commit()
    print("transactions テーブルに 'type' カラムを追加しました。")
except sqlite3.OperationalError:
    print("すでに 'type' カラムは存在します。")

# `is_admin` カラムを追加（すでにある場合は無視）
cursor.execute('''
ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0
''')
print("管理者用の is_admin カラムを追加しました。")

# 管理者情報（変更可能）
admin_name = "管理者"
admin_email = "admin@example.com"
admin_password = "admin123"  # 必要に応じて変更
hashed_password = generate_password_hash(admin_password)

# 管理者を追加
cursor.execute('''
    INSERT INTO users (name, email, password, is_admin)
    VALUES (?, ?, ?, ?)
''', (admin_name, admin_email, hashed_password, 1))
print("管理者アカウントを作成しました。")

# データベースを保存して閉じる
conn.commit()
conn.close()

print("データベースとテーブルを作成しました。")
