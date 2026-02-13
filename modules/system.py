# modules/system.py

import logging
import os
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class System:
    config: dict

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            trash = self.config["files"]["trash"]
        except AttributeError:
            trash = None
        while trash:
            try:
                os.remove(trash.pop())
            except FileNotFoundError:
                pass

    def create_temp_file(
        self,
        prefix: str = "/tmp/changer_",
        suffix: str | None = None,
        mode: str = "w+b",
    ) -> str:
        with tempfile.NamedTemporaryFile(
            prefix=prefix, suffix=suffix, mode=mode, delete=False
        ) as f:
            self.config["files"]["trash"].append(f.name)
            return f.name


@dataclass(init=False)
class Script:
    system: System
    filename: str

    def __init__(self, system: System) -> None:
        self.system = system
        self.reset()

    def append(self, command: str) -> None:
        with open(self.filename, "a") as f:
            f.write(command)
            f.write("\n")

    def reset(self) -> None:
        self.filename = self.system.create_temp_file(suffix=".sh", mode="a")
        self.append(f"#! {os.getenv('SHELL')}\n")

    def run(self, *args) -> Tuple[int, str, str]:
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            logging.debug(self.filename)
            with open(self.filename, "r") as f:
                contents = f.read()
                logging.debug(contents)
        os.chmod(
            self.filename,
            stat.S_IRUSR
            | stat.S_IWUSR
            | stat.S_IXUSR
            | stat.S_IRGRP
            | stat.S_IXGRP
            | stat.S_IROTH
            | stat.S_IROTH
            | stat.S_IXOTH,
        )
        return execute([self.filename, *args])


def execute(command: List[str], shell: bool = False) -> Tuple[int, str, str]:
    logging.debug(f"Running {command}")
    result = subprocess.run(command, capture_output=True, shell=shell)
    code = result.returncode
    out = result.stdout.decode()
    err = result.stderr.decode()
    if len(err) > 0:
        logging.error(err)
    logging.debug(f"Return code: {code}")
    logging.debug(f"Output: {out}")
    return code, out, err
