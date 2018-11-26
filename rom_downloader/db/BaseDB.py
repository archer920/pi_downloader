import sqlite3


class BaseDB:

    def __init__(self) -> None:
        self.conn = None

    def open(self, db_file: str):
        self.conn = sqlite3.connect(db_file)

    def close(self) -> None:
        self.conn.close()

    def get_cursor(self) -> sqlite3.Cursor:
        return self.conn.cursor()

    def commit(self) -> None:
        self.conn.commit()
