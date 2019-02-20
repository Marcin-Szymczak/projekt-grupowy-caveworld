"""
Network message models module.

There are types like Any, AnyOf, Type, List which allow for validating
the network received data.

The class `Model` allows for creating message models which are 
automatically validated (provided they define their fields in terms of
Any, AnyOf, Type, List) and automatically parsed as dicts (useful for
generating the protocol information)
"""

from abc import ABC, abstractmethod
import inspect


class ValidationException(Exception):
    """
    Thrown when a validation fails.

    Network-object models have restrictions on their type and whenever one is
    created with wrong data, validation exception will be thrown.

    It is used to protect the rest of the application from using invalid data.
    """
    pass

class Validator:
    def __call__(self, value):
        return value
        
    def validate(self, value):
        return self(value)

class Any(Validator):
    """
    All types are accepted in place of this variable.
    """
    def __init__(self):
        pass

    def __call__(self, value):
        return value

    def __repr__(self):
        return "Any"

class Type(Validator):
    """
    A single value of the specific type must be present in this variable.
    """
    def __init__(self, t):
        self.type = t

    def __call__(self, value):
        if isinstance(value, dict) and inspect.isclass(self.type) and issubclass(self.type, Model):
            return self.type(value)
        if not inspect.isclass(self.type) and isinstance(self.type, Validator):
            return self.type(value)
        elif isinstance(value, self.type):
            return value
        else:
            raise ValidationException(f"Expected type {self.type} instead of {value.__class__} while validating {self}")

    def __repr__(self):
        return f"Type({repr(self.type)})"

class List(Type):
    """
    A list of the provided types.

    Example:
    ```
    self.param = List(Type(int))
    ```
    """
    def __init__(self, t):
        self.type = t

    def __call__(self, value):
        if not isinstance(value, list):
            raise ValidationException(f"Expected a list type instead of {value.__class__}")

        return [super(List, self).__call__(el) for el in value]

    def __repr__(self):
        return f"List({repr(self.type)})"

class AnyOf(Validator):
    def __init__(self, *types):
        if len(types) == 0:
            raise TypeError(
                "AnyOf expects at least 1 type to be provided, to be useful."
                )
        self.types = types
    
    def __call__(self, value):
        for t in self.types:
            try:
                return t(value)
            except:
                pass
        raise ValidationException(F"Expected any type from {self.types}, not {value.__class__}")

    def __repr__(self):
        return f"AnyOf({repr(self.types)})"

class Enum(Validator):
    def __init__(self, *variants):
        if len(variants) == 0:
            raise TypeError(
                "Enum expects at least 1 variant to be provided."
            )
        self.variants = variants

    def __call__(self, value):
        if value in self.variants:
            return value

def as_dict(value):
    try:
        return value.as_dict()
    except Exception:
        if isinstance(value, (list, tuple)):
            return [as_dict(e) for e in value]
        elif isinstance(value, (dict)):
            return {k: as_dict(v) for k, v in value.items()}
        else:
            return value

class Option(Type):
    def __call__(self, value):
        if value is None:
            return value
        return super().__call__(value)

class Model(Validator, ABC):
    def __init__(self, d=None, **kvars):
        self.model()
        if d is not None:
            self.load(d)
        elif kvars:
            self.load(kvars)

    @abstractmethod
    def model(self):
        pass

    def as_dict(self):
        result = {}
        for k, v in vars(self).items():
            if k.startswith("_"):
                continue

            """
            try:
                result[k] = v.as_dict()
            except Exception:
                if isinstance(v, (list, tuple)):

                result[k] = v
            """
            result[k] = as_dict(v)

        return result

    def load(self, data):
        for k, v in vars(self).items():
            if k.startswith("_"):
                continue

            if k not in data:
                raise ValidationException(f"Expected key {k}")
        
        for k, v in data.items():
            if k.startswith("_"):
                continue
            # getattr(self, k)(v)
            setattr(self, k, getattr(self, k)(v))
        
        return self

    __call__ = load