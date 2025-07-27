
import importlib
import sys
import pytest #type: ignore

from cffi_stubgen.stubgen import get_functions

EXAMPLE_MOD = "example_module._example"

@pytest.fixture(scope="module")
def example_mod():
    mod = importlib.import_module(EXAMPLE_MOD)
    return mod

def test_get_functions_names(example_mod):
    funcs, ctypes = get_functions(example_mod)
    names = {f.name for f in funcs}
    # From example.h: add, sub, addf, subf
    assert {"add", "sub", "addf", "subf"}.issubset(names)

def test_get_functions_signatures(example_mod):
    funcs, ctypes = get_functions(example_mod)
    func_map = {f.name: f for f in funcs}
    add = func_map["add"]
    assert add.ret_t.cname == "int"
    assert [a.ctype.cname for a in add.args] == ["int", "int"]
    addf = func_map["addf"]
    assert addf.ret_t.cname == "double"
    assert [a.ctype.cname for a in addf.args] == ["double", "double"]
