from __future__ import annotations

from pycparser import (
    CParser, 
    c_ast
)

from cffi.commontypes import COMMON_TYPES
from cffi.cparser import _common_type_names

from dataclasses import dataclass

from typing import (
    Callable,
    Self
)

@dataclass(eq=True, slots=True)
class CType:
    cname: str
    pyname: str
    
    def __init__(self, cname: str, pyname: str)->None:
        self.cname = cname
        self.pyname = pyname.replace(" ", "")
    
    @classmethod
    def from_node(cls, arg:c_ast.Node) -> Self:
        arg_cname = " ".join([q for q in arg.quals]+[a for a in arg.type.names])
        arg_pyname = "".join([q.title() for q in arg.quals]+[a.title() for a in arg.type.names]).replace(" ", "")
        match arg.type:
            case c_ast.TypeDecl:
                return cls(arg_cname, arg_pyname)
            case c_ast.PtrDecl:
                return cls(arg_cname + " *", arg_pyname+"_ptr")
            case c_ast.ArrayDecl:
                return cls(arg_cname + " []", arg_pyname+"_arr")
            case _:
                raise cls(arg_cname, arg_pyname)

@dataclass(slots=True)
class CFuncArg:
    name: str
    ctype: CType
    
CVarArg =CFuncArg("VA", CType("...", "VarArg"))

@dataclass(slots=True)
class CFunc:
    name: str
    ret_t: CType
    args : list[CFuncArg]
    doc: str
    
def _parse_arg(arg : c_ast.Node) -> CFuncArg:
    match arg:
        case c_ast.EllipsisParam:
            return CVarArg
        case _:
            try:
                argname = arg.name
            except Exception:
                argname = None
            arg_t = CType.from_node(arg)
            return CFuncArg(argname, arg_t)
                

def parse_func(func: Callable, typedefs: list[str] | None = None) -> list[CFunc]:

    parser = CParser()
    
    if typedefs:
        COMMON_TYPES.update({_t:_t for _t in typedefs})
    
    sig = func.__doc__.splitlines()[0]
    
    clines = []
    for _t in _common_type_names(sig):
        # The parser will break unless all types are defined with a typedef
        # However, it does not matter what the typedef defines them as
        # For the purpose of generating the stub
        clines.append(f"typedef int {_t};")
    clines.append(sig)
    
    parse_res = parser.parse("\n".join(clines))
    
    funcs = []
    for decl in parse_res:
        if isinstance(decl, c_ast.Decl):
            arg_count = 0
            name = decl.name
            func_t = decl.type
            ret_t = CType.from_node(func.type)
            args = []
            for arg in func_t.args:
                carg = _parse_arg(arg)
                if carg.name is None:
                    carg.name = f"arg{arg_count}"
                arg_count +=1
                args.append(carg)
            func = CFunc(name, ret_t, args)
            funcs.append(func)
    
    
    