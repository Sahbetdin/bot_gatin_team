import sqlite3
import csv
from typing import Optional, List, Dict, Any


class SQLiteDB:
    def __init__(self, db_name: str = 'ideas_users.db'):
        """Initialize the database connection"""
        self.db_name = db_name
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self):
        """Support context manager protocol (for with statements)"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context"""
        self.close()

    def connect(self):
        """Establish a database connection"""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # print(f"Connected to database '{self.db_name}'")

    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            # print(f"Closed connection to database '{self.db_name}'")

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query"""
        if not self.connection:
            self.connect()
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """
        Create a new table
        :param table_name: Name of the table
        :param columns: Dictionary of column names and types (e.g., {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'})
        """
        columns_def = ', '.join([f"{name} {type_}" for name, type_ in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        self.execute_query(query)
        print(f"Created table '{table_name}'")
        
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Insert data into a table
        :param table_name: Name of the table
        :param data: Dictionary of column names and values
        :return: ID of the inserted row
        """
        columns = ','.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        # print(placeholders)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            self.execute_query(query, tuple(data.values()))               
        except sqlite3.IntegrityError:
            # print("User exists")
            pass
        return self.cursor.lastrowid

    def fetch_all(self, table_name: str, 
                  columns: List[str] = None, 
                  condition: str = None, 
                  params: tuple = (),
                  is_limit_one: bool = False) -> List[Dict]:
        """
        Fetch all rows from a table
        :param table_name: Name of the table
        :param columns: List of columns to select (None for all)
        :param condition: WHERE condition (None for no condition)
        :param params: Parameters for the WHERE condition
        :return: List of dictionaries representing rows
        """
        cols = '*' if columns is None else ', '.join(columns)
        query = f"SELECT {cols} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        if is_limit_one:
            query += f" LIMIT 1"
        self.execute_query(query, params)
        columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def fetch_from_join(self, table_name1: str, table_name2: str) -> List[Dict]:
        """
        Fetch all rows from a joining users and ideas tables
        :return: List of dictionaries representing rows
        """
        query = f"""
        SELECT 
            t1.user_tg_id, t1.tg_name, t1.name, t1.is_agree_to_save_name, t2.idea, t2.created_at_i
        FROM
            {table_name1} t1 RIGHT JOIN {table_name2} t2 ON t1.user_tg_id = t2.user_tg_id
        ORDER BY 
            t2.created_at_i DESC,
            t1.user_tg_id ASC
        """
        self.execute_query(query, ())
        columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    
    def select_to_csv(self, table_name1: str, table_name2: str = None, 
                      filename: str = "default.csv") -> None:
        # data = self.fetch_all(table_name, None, None, ())
        data = self.fetch_from_join(table_name1="users", table_name2="ideas")

        if not data:
            raise ValueError("Empty data list provided")
        
        fieldnames = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-16') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(fieldnames)
            # Write data rows
            for row in data:
                writer.writerow(row.values())
        
        print(f"Successfully exported {len(data)} records to {filename}")
