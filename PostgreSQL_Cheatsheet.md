## 初めての接続
psql -U postgres -h localhost -p 5432

## データベース一覧表示
\l

## ロール一覧表示
\du

## ユーザーの作成
create user <username>;

## ユーザーにパスワードを持たせる
\password <username>

## データベースに接続
\c <dbname>

## データベースの作成
create database <dbname>;

## データベースの削除
drop database <dbname>

## テーブル一覧の表示
\z

## テーブル定義の表示
\d <tablename>

## データベース初期セットアップ手順
### **ユーザーの作成**
create user with password <USER_POSTGRES_PASSWORD>;
### **データベースの作成**
create database <USER_POSTGRES_DB> owner <USER_POSTGRES_USER>;
