from argparse import ArgumentParser
from typing import Optional

class TaskipyError(Exception):
    exit_code = 1


class InvalidRunnerTypeError(TaskipyError):
    def __str__(self):
        return (
            'invalid value: runner is not a string. '
            'please check [tool.taskipy.settings.runner]'
        )


class MissingPyProjectFileError(TaskipyError):
    def __str__(self):
        return 'no pyproject.toml file found in this directory or parent directories'


class MalformedPyProjectError(TaskipyError):
    def __init__(self, reason: Optional[str] = None):
        super().__init__()
        self.reason = reason

    def __str__(self):
        message = 'pyproject.toml file is malformed and could not be read'

        if self.reason:
            message += f'. reason: {self.reason}'

        return message


class TaskNotFoundError(TaskipyError):
    exit_code = 127

    def __init__(self, task_name: str):
        super().__init__()
        self.task = task_name

    def __str__(self):
        return f'could not find task "{self.task}"'

class MalformedTaskError(TaskipyError):
    def __init__(self, task_name: str, reason: str):
        super().__init__()
        self.task = task_name
        self.reason = reason

    def __str__(self):
        return f'the task "{self.task}" in the pyproject.toml file is malformed. reason: {self.reason}'

class InvalidUsageError(TaskipyError):
    exit_code = 127

    def __init__(self, parser: ArgumentParser):
        super().__init__()
        self.__parser = parser

    def __str__(self):
        return self.__parser.format_usage().strip('\n')

class MissingTaskipySettingsSectionError(TaskipyError):
    exit_code = 127

    def __str__(self):
        return (
            'no settings found. add a [tools.taskipy.settings]'
            'section to your pyproject.toml'
        )


class MissingTaskipyTasksSectionError(TaskipyError):
    exit_code = 127

    def __str__(self):
        return (
            'no tasks found. add a [tool.taskipy.tasks] '
            'section to your pyproject.toml'
        )


class CircularVariableError(TaskipyError):
    exit_code = 127

    def __str__(self):
        return 'cannot resolve variables, found variables that depend on each other.'


class InvalidVariableError(TaskipyError):
    exit_code = 127

    def __init__(self, variable: str, reason: str) -> None:
        super().__init__()
        self.variable = variable
        self.reason = reason

    def __str__(self):
        return f'variable {self.variable} is invalid. reason: {self.reason}'
