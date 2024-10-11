from queue import Queue
from enum import Enum, unique
from dataclasses import dataclass
from typing import Any


@unique  # 保證唯一值
class TaskTpyes(Enum):
    exit = 0
    close = 1


@dataclass
class Task:
    type: TaskTpyes
    data: Any


class Single:
    task = Queue()
