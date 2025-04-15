import sqlite3
from sqlite_class import SQLiteDB
import datetime
s = SQLiteDB(db_name = 'ideas_users.db')

#DROP TABLE
# conn = sqlite3.connect('ideas_users.db')
# cursor = conn.execute(f"DROP TABLE IF EXISTS ideas")
# cursor = conn.execute(f"DROP TABLE IF EXISTS users")
# conn.close()

#CHECK if table exists
# conn = sqlite3.connect('ideas_users.db')
# table_name = "users"
# cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
# res = cursor.description
# # # (('name', None, None, None, None, None, None),)
# print(res)
# conn.close()


# CREATE TABLE
# 1. Create tables, done once.
# "id" - id in db, user_tg_id - id in telegram, 
# tg_name - telegram name
# name - name, user has entered 
# is_agree_to_save_name - if user has agreed to save his name and address with it
# s.create_table('users',{"id":"INTEGER PRIMARY KEY NOT NULL",
# 						"user_tg_id": "INTEGER UNIQUE NOT NULL",
# 						"tg_name": "TEXT",
# 						"name": "TEXT",
# 						"is_agree_to_save_name": "INTEGER",
# 						"created_at": "current_timestamp"})

# s.create_table('ideas', {"id_i": "INTEGER PRIMARY KEY NOT NULL",
# 						"user_tg_id": "INTEGER",
# 						"idea": "TEXT",
# 						"created_at_i": "current_timestamp"})

# s.insert_data("users", {"user_tg_id":212,"tg_name":"mansur","name":"Mansur S",
# 						"is_agree_to_save_name":1,
# 						"created_at": datetime.datetime.now()})
# s.insert_data("users", {"user_tg_id":2562,"tg_name":"shams","name":"Shams",
# 						"is_agree_to_save_name":0,
# 						"created_at": datetime.datetime.now()})

# TRUNCATE TABLE
# conn = sqlite3.connect('ideas_users.db')
# cursor = conn.execute(f"DELETE FROM ideas")
# conn.close()


#    def fetch_all(self, table_name: str, 
#                   columns: List[str] = None, 
#                   condition: str = None, 
#                   params: tuple = (),
#                   is_limit_one: bool = False):
#         cols = '*' if columns is None else ', '.join(columns)
#         query = f"SELECT {cols} FROM {table_name}"
#         if condition:
#             query += f" WHERE {condition}"
#         if is_limit_one:
#             query += f" LIMIT 1"
#         self.execute_query(query, params)
#         columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
#         return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    

# SELECT users
id_to_check = 329200678
res = s.fetch_all('users', ["is_agree_to_save_name"], f"user_tg_id={id_to_check}" ,(), True)
if len(res) == 0:
    print('Not found')
else:
    print("User found")
    
    # for r in res:
	#     print(r)


