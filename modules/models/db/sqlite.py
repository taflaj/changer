# modules/models/db/sqlite.py

import logging
import sqlite3
from dataclasses import dataclass


@dataclass(init=False)
class DbManager:
    filename: str

    def __init__(self, filename: str):
        self.filename = filename
        self.transaction = False
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        script: str = """CREATE TABLE IF NOT EXISTS t_files(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT UNIQUE NOT NULL,
            created DATETIME DEFAULT CURRENT_TIMESTAMP);

            CREATE UNIQUE INDEX IF NOT EXISTS i_files ON t_files(ID, file);"""
        self.cursor.executescript(script)

    def add_to_repo(self, file: str) -> None:
        query: str = "SELECT COUNT(*) FROM t_files WHERE file=?;"
        params = (file,)
        response = self.cursor.execute(query, params)
        if response.fetchone()[0] == 0:
            query = "INSERT INTO t_files(file) VALUES(?);"
            self.cursor.execute(query, params)
            if not self.transaction:
                self.conn.commit()

    def begin(self) -> None:
        query: str = "BEGIN TRANSACTION;"
        self.cursor.execute(query)
        self.transaction = True

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()

    def commit(self) -> None:
        if self.transaction:
            self.conn.commit()
            self.transaction = False

    def get_count(self) -> int:
        query: str = "SELECT COUNT(*) FROM t_files;"
        response = self.cursor.execute(query)
        return response.fetchone()[0]

    def get_nth_file(self, n: int) -> str:
        query: str = """SELECT file, ID FROM t_files WHERE ID=?
            + (SELECT seq FROM sqlite_sequence WHERE name=?)
            - (SELECT COUNT(*) FROM t_files)
            + 1;"""
        params = (
            n,
            "t_files",
        )
        response = self.cursor.execute(query, params)
        result = response.fetchone()
        logging.debug(f"{n} => {result}")
        return result[0]

    def reset_repo(self) -> None:
        query: str = "DELETE FROM t_files"
        self.cursor.execute(query)
