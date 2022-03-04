
from collections import OrderedDict
from dataclasses import dataclass
import itertools
from typing import Iterable, List, Type


def setattrs(objs: Iterable[object], name, value):
    for obj in objs:
        if callable(value):
            setattr(obj, name, value())
        else:
            setattr(obj, name, value)

def cartesian_product_dataclass(cls: Type[object], **kwargs) -> List[object]:
    fields = OrderedDict(kwargs)
    objs = []
    for field_set in itertools.product(*fields.values()):
        obj = cls(**dict(zip(fields.keys(), field_set)))
        objs.append(obj)
    return objs
