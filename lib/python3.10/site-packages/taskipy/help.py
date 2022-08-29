import shutil
import textwrap
import colorama # type: ignore
from typing import List

from taskipy.task import Task


class HelpFormatter:
    def __init__(self, tasks: List[Task]):
        self.__tasks = tasks

    def print(self, line_width=shutil.get_terminal_size().columns):
        colorama.init()

        tasks_col = [task.name for task in self.__tasks]
        longest_item_in_tasks_col = len(max(tasks_col, key=len))

        desc_col_wrap_indent = ' ' * (longest_item_in_tasks_col + 1)
        desc_col_width = line_width - len(desc_col_wrap_indent)

        for task in self.__tasks:
            name_text = task.name
            desc_text = task.description or task.command

            tasks_col_text = f'{name_text:<{longest_item_in_tasks_col}}'
            desc_col_text = '\n'.join(textwrap.wrap(desc_text,
                                                    width=desc_col_width,
                                                    subsequent_indent=desc_col_wrap_indent))
            print(f'{self.__highlight(tasks_col_text)} {desc_col_text}')

    def __highlight(self, text: str):
        return f'{colorama.Fore.CYAN}{text}{colorama.Style.RESET_ALL}'
