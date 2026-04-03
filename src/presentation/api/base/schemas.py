from collections.abc import Collection
from dataclasses import dataclass

from litestar.dto import DataclassDTO, DTOConfig
from litestar.types.protocols import DataclassProtocol

type DataclassDTOData = DataclassProtocol | Collection[DataclassProtocol]


@dataclass
class CamelModel:
    config = DTOConfig(
        rename_strategy="camel",
    )


class BaseRequestDTO[T: DataclassDTOData](DataclassDTO[T], CamelModel): ...


class BaseResponseDTO[T: DataclassDTOData](DataclassDTO[T], CamelModel): ...
