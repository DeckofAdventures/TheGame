"""
Future versions should remove these init imports so that each class must be fetched
from the relevant ffile rather than the templates module
"""
from .bestiary import Beast, Bestiary
from .powers import Power, Powers
from .yaml_spec import YamlSpec

__all__ = ["YamlSpec", "Powers", "Power", "Bestiary", "Beast"]
