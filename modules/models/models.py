# modules/models/models.py

from dataclasses import dataclass

from modules.models.db.sqlite import DbManager


@dataclass
class Models:
    filename: str

    def __enter__(self):
        self.db = DbManager(self.filename)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()

    def add_to_repo(self, file: str) -> None:
        self.db.add_to_repo(file)

    def begin(self) -> None:
        self.db.begin()

    def commit(self) -> None:
        self.db.commit()

    def get_count(self) -> int:
        return self.db.get_count()

    def get_nth_file(self, n: int) -> str:
        return self.db.get_nth_file(n)

    def reset_repo(self) -> None:
        self.db.reset_repo()
