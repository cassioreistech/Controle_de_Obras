import sqlite3
db = sqlite3.connect('data/app.db')
db.execute("UPDATE empresa SET logo_path = '' WHERE logo_path IS NULL")
db.commit()
print("OK")
db.close()
