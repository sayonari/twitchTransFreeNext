'''
en : All comments were translated using DeepL.
ja : すべてのコメントはDeepLを使用して翻訳されました。

'''

import os, sqlite3, asyncio

db_name = 'database.db'					# en:Filename of database		ja:データベースのファイル名
table_name = 'translations'
cwd = os.getcwd()						# en:Current Working Directory 	ja:現在の作業フォルダ
db_file = os.path.join(cwd,db_name)		# en:Database File				ja:データベース・ファイル

try:									# en:Create the database File	ja:データベース・ファイルの作成
	with open(db_file, "x") as fp:		# "x" = en:"Create file"		ja:「ファイル作成」
		pass
	print("Database created.")
except FileExistsError as e:			# en:Continue if file exists	ja:ファイルが存在する場合、続行
	pass

db = sqlite3.connect(db_file)
print("Connected to database.")
cursor = db.cursor()
print("Created cursor object for database")

try:									# en:Create translation table	ja:翻訳テーブルの作成
	sql = "CREATE TABLE translations (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, MESSAGE TEXT NOT NULL, DLANG TEXT NOT NULL, TRANSLATION TEXT);"
	cursor.execute(sql)
	print("Table created.")
except sqlite3.OperationalError as e:  # en:Continue if table exists   ja:テーブルが存在する場合、続行する
	print(e)
	pass

async def save(message,translation,dlang):	# en:Save the translations   ja:翻訳を保存する
	sql = "INSERT INTO translations (MESSAGE,DLANG,TRANSLATION) VALUES (?, ?, ?);"
	args = (message, dlang, translation)
	cursor.execute(sql, args)
	db.commit()

async def get(message,dlang):  # en:Get the translations    ja:翻訳を入手する
	# en:Return translation or None if nothing found   ja:翻訳を返すか、何も見つからなければ None を返す
	sql = "SELECT TRANSLATION FROM translations WHERE MESSAGE=? AND DLANG=?"
	args = (message, dlang)
	return cursor.execute(sql, args).fetchone()

def delete(target_size:int = 52428800):
	size = os.path.getsize(db_file)
	if size >= target_size:
		os.remove(db_file)

def close():
	db.close()
