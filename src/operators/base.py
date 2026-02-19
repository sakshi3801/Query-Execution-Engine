from abc import ABC, abstractmethod
from typing import Any, Iterator, List


class Operator(ABC):
    
    @abstractmethod
    def __iter__(self) -> Iterator[List[Any]]:
        ...

    @abstractmethod
    def __next__(self) -> List[Any]:
        ...

    def next(self) -> List[Any]:
        return self.__next__()

    def execute(self) -> List[List[Any]]:
        return list(self)
