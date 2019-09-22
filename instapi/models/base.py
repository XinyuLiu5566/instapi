from typing import AbstractSet
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Type
from typing import TypeVar

from dataclasses import Field
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

from instapi.types import StrDict
from instapi.utils import LoggingMeta

ModelT_co = TypeVar('ModelT_co', bound='BaseModel', covariant=True)


@dataclass(frozen=True)
class BaseModel(metaclass=LoggingMeta):
    __dataclass_fields__: ClassVar[Dict[str, Field]]

    @classmethod
    def fields(cls) -> AbstractSet[str]:
        return cls.__dataclass_fields__.keys() - {'__dataclass_fields__'}

    @classmethod
    def create(cls: Type[ModelT_co], data: Any) -> ModelT_co:
        # noinspection PyArgumentList
        return cls(**{k: data[k] for k in cls.fields() if k in data})  # type: ignore

    def as_dict(self) -> StrDict:
        """
        Convert model into native instagram representation.
        Should be overridden at delivered classes if model
        has specific representation.

        :return: native instagram representation
        """
        return {
            key: value.as_dict() if isinstance(value, BaseModel) else value
            for key, value in asdict(self).items()
        }


@dataclass(frozen=True)
class Entity(BaseModel):
    pk: int = field(repr=False)

    def __hash__(self) -> int:
        return hash(self.pk)

    def __int__(self) -> int:
        return self.pk

    @classmethod
    def create(cls: Type[ModelT_co], data: StrDict) -> ModelT_co:
        return super().create(data)


__all__ = [
    'BaseModel',
    'Entity',
    'ModelT_co',
]
