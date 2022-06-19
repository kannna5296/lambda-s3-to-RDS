CREATE TABLE  user (
   ID INT IDENTITY(1,1) NOT NULL,
   NAME VARCHAR(255) NOT NULL
)

CREATE TABLE task (
   id INT IDENTITY(1,1) NOT NULL,
   name varchar(255) NOT NULL,
   file_id varchar(MAX) NOT NULL
)

CREATE TABLE task_detail (
   id INT IDENTITY(1,1) NOT NULL,
   task_id INT NOT NULL,
   user_id INT NOT NULL,
   content VARCHAR(255) NOT NULL,
   created_at DATETIME NOT NULL
)

--マスタデータ（lambda起動時には登録されてる前提）
INSERT INTO user (name) VALUES ('tanaka')
INSERT INTO user (name) VALUES ('taro')