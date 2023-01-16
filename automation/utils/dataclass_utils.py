from dataclasses import fields
from operator import attrgetter


def my_repr(self, seperator: str = "\n", indent: int = 0):
    """Print formatting for custom dataclasses"""
    nodef_f_vals = (
        (f.name, attrgetter(f.name)(self))
        for f in fields(self)  # for each data field
        # Only print if it is not the default, and it is marked for inclusion in repr
        if attrgetter(f.name)(self) != f.default and f.repr
    )
    tabs = "\t" * indent
    # Separate fields with \n newlines
    nodef_f_repr = f"{seperator}{tabs}".join(
        f"{name}={value}" for name, value in nodef_f_vals
    )
    return f"{self.__class__.__name__}{seperator}{tabs}({nodef_f_repr})"
