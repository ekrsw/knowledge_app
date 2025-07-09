## 初めての接続
psql -U postgres -h localhost -p 5432

## データベース一覧表示
\l

## ロール一覧表示
\du

## ユーザーの作成
create user <USER_POSTGRES_USER>;

## ユーザーにパスワードを持たせる
\password <USER_POSTGRES_USER>

## データベースに接続
\c <USER_POSTGRES_DB>

## データベースの作成
create database <USER_POSTGRES_DB>;

## データベースの削除
drop database <USER_POSTGRES_DB>

## テーブル一覧の表示
\z

## テーブル定義の表示
\d <TABLE_NAME>

## データベース初期セットアップ手順
### **ユーザーの作成**
create user with password <USER_POSTGRES_PASSWORD>;
### **データベースの作成**
create database <USER_POSTGRES_DB> owner <USER_POSTGRES_USER>;
