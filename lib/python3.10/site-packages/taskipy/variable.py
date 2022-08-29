class Variable:
    def __init__(self, name: str, value: str, recursive: bool) -> None:
        self.__name = name
        self.__value = value
        self.__recursive = recursive

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> str:
        return self.__value

    @property
    def recursive(self) -> bool:
        return self.__recursive
