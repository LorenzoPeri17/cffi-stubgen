
import pytest
from cffi_stubgen.functions import parse_func

def make_fake_func(docstring):
    def f():
        pass
    f.__doc__ = docstring
    return f

@pytest.mark.parametrize("decl,ret_type,arg_types", [
    ("int *foo(int *a, float b[]);", "int *", ["int *", "float []"]),
    ("void bar(const int a, float *const b);", "void", ["const int", "float const *"]),
    ("unsigned int baz(unsigned int a);", "unsigned int", ["unsigned int"]),
    ("int32_t qux(int32_t a, uint64_t b);", "int32_t", ["int32_t", "uint64_t"]),
    ("bool flag(bool a);", "bool", ["bool"]),
    ("float _Complex cadd(float _Complex a, float _Complex b);", "float _Complex", ["float _Complex", "float _Complex"]),
    ("double _Complex dadd(double _Complex a, double _Complex b);", "double _Complex", ["double _Complex", "double _Complex"]),
    ("const char *cstring(char * const s);", "const char *", ["char const *"]),
    ("const char *cstring(const char *s);", "const char *", ["const char *"]),
    ("void arrfunc(int a[]);", "void", ["int []"]),
    ("void arrfunc(int a[10]);", "void", ["int [10]"]),
    ("void arrfunc(const int a[10]);", "void", ["const int [10]"]),
])
def test_parse_func_various_types(decl, ret_type, arg_types):
    func = make_fake_func(decl)
    funcs = parse_func(func)
    assert len(funcs) == 1
    f = funcs[0]
    assert f.ret_t.cname == ret_type
    assert [a.ctype.cname for a in f.args] == arg_types
