

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
, is_admin INTEGER DEFAULT 0);
INSERT INTO users VALUES(1,'Alice','alice@example.com','password123','2025-01-21 13:46:36',0);
INSERT INTO users VALUES(2,'testman','test@mail.com','scrypt:32768:8:1$LooyBq9h5vigk1AR$31840871097322025171367357ec215af4a2515b14a283ce5ddc97b0631fc01caea469622293ce7771f4baa0b6f922c190ea71505c3d23a9d6b758146814d2e3','2025-01-21 13:50:54',0);
INSERT INTO users VALUES(3,'伊達政宁E','masa@mail.com','scrypt:32768:8:1$zwnb8Ei21nwWwaiC$0e60a27e24313c36dee8cad3423bf8ddeba12ebcd26c38b9f701c94b13f6507846a7d97e5ead8751dc87b04120b6dacfa41f3aace6712297503c3ed6cd709797','2025-02-04 09:49:01',0);
INSERT INTO users VALUES(4,'管琁E��E','admin@example.com','scrypt:32768:8:1$zIs7NCn0oJ0nMkky$1c80368668c4f6bd2af5c23770eb0dc809b684b0c3fe85c10320d22d2bc87cc183b4a7af8b620e17a96681f3b5d6b3fcb2e052ac2e1754bd3fde8df92e2d20f6','2025-02-18 12:24:00',1);
INSERT INTO users VALUES(5,'長宗�E部允E��','test2@mail.com','scrypt:32768:8:1$2Y7bhq9bxCPbA0rQ$a7b48394bdd36672db960fdc6a10602f5c5c8b1a81ee6bfe444097c0da722daa900293cae686d5dc56ae4b9ca7fa35800e5033cf5928a78a8c3ce11edf9888f3','2025-02-18 12:47:23',0);
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO categories VALUES(1,'食費','2025-02-04 06:03:45');
INSERT INTO categories VALUES(2,'交通費','2025-02-04 06:36:26');
INSERT INTO categories VALUES(3,'給斁E','2025-02-18 12:27:27');
CREATE TABLE payment_methods (
    id INT PRIMARY KEY AUTO_INCREMENT AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL
);
INSERT INTO payment_methods VALUES(1,'現釁E');
INSERT INTO payment_methods VALUES(2,'クレジチE��カーチE');
INSERT INTO payment_methods VALUES(3,'paypay');
INSERT INTO payment_methods VALUES(4,'test');
INSERT INTO payment_methods VALUES(5,'2');
INSERT INTO payment_methods VALUES(6,'test2');
CREATE TABLE IF NOT EXISTS transactions (
        id INT PRIMARY KEY AUTO_INCREMENT ,
        user_id INTEGER NOT NULL,
        date VARCHAR(255) NOT NULL,
        category INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method VARCHAR(255) NULL,  -- NOT NULL 制紁E��削除
        note VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(category) REFERENCES categories(id)
    );
INSERT INTO transactions VALUES(1,1,'2025-01-17','食費',1500.0,'クレジチE��カーチE','ランチE','2025-01-21 13:47:01');
INSERT INTO transactions VALUES(3,2,'2025-01-23','食費',300.0,'クレジチE��カーチE','モーニング','2025-01-22 12:53:57');
INSERT INTO transactions VALUES(4,2,'2025-01-22','食費',900.0,'現釁E','ランチE','2025-01-22 12:54:24');
INSERT INTO transactions VALUES(10,2,'2025-01-23',1,344.0,'cash','','2025-01-22 14:43:21');
INSERT INTO transactions VALUES(11,2,'2025-01-23',1,123.0,'cash','','2025-01-22 14:47:49');
INSERT INTO transactions VALUES(12,2,'2025-01-21',2,567.0,'credit','','2025-01-22 14:49:11');
INSERT INTO transactions VALUES(13,2,'2025-01-23',1,300.0,'cash','','2025-01-22 14:54:24');
INSERT INTO transactions VALUES(15,2,'2025-01-26',2,15000.0,'credit','','2025-02-04 06:36:43');
INSERT INTO transactions VALUES(16,3,'2025-02-03',1,300.0,'現釁E','','2025-02-04 10:06:23');
INSERT INTO transactions VALUES(17,2,'2025-02-11',1,300.0,'現釁E','','2025-02-18 12:41:03');
INSERT INTO transactions VALUES(18,5,'2025-02-12',1,300.0,'現釁E','','2025-02-18 12:48:02');
INSERT INTO transactions VALUES(19,5,'2025-02-17',2,1300.0,'paypay','','2025-02-18 12:48:21');
INSERT INTO transactions VALUES(20,5,'2025-01-15',2,300.0,'クレジチE��カーチE','','2025-02-18 14:13:58');
INSERT INTO transactions VALUES(22,5,'2025-01-28',3,1234.0, '','','2025-02-18 14:35:18');
INSERT INTO sqlite_sequence VALUES('users',5);
INSERT INTO sqlite_sequence VALUES('categories',3);
INSERT INTO sqlite_sequence VALUES('payment_methods',6);
INSERT INTO sqlite_sequence VALUES('transactions',22);

