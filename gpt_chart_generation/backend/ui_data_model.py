from pydantic import BaseModel
from typing import List, Union


class PathItem(BaseModel):
    name: str


class Path(BaseModel):
    path: List[PathItem]


class FilterItem(BaseModel):
    filter_name: Union[str, None]
    filter_value: Union[str, None]


class Filter(BaseModel):
    filter: FilterItem


class ColorValue(BaseModel):
    color: Union[str, None]