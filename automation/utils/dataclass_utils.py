from dataclasses import fields
from operator import attrgetter


def my_repr(self, separator: str = "\n", indent: int = 0):
    """Print formatting for custom dataclasses"""
    no_default_f_vals = (
        (f.name, attrgetter(f.name)(self))
        for f in fields(self)  # for each data field
        # Only print if it is not the default, and it is marked for inclusion in repr
        if attrgetter(f.name)(self) != f.default and f.repr
    )
    tabs = "\t" * indent
    # Separate fields with \n newlines
    no_default_f_repr = f"{separator}{tabs}".join(
        f"{name}={value}" for name, value in no_default_f_vals
    )
    return f"{self.__class__.__name__}{separator}{tabs}({no_default_f_repr})"
