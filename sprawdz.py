import sqlite3

con = sqlite3.connect('experiments.db')
tabele = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tabele w bazie:", tabele)
con.close()