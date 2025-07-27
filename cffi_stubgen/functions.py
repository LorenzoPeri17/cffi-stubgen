from __future__ import annotations

from pycparser import CParser, c_ast  # type: ignore

from cffi.commontypes import COMMON_TYPES
from cffi.cparser import _common_type_names  # type: ignore

from dataclasses import dataclass

from typing import Callable, Self


@dataclass(eq=True, slots=True, unsafe_hash=True)
class CType:
    cname: str
    pyname: str

    def __init__(self, cname: str, pyname: str) -> None:
        self.cname = cname
        self.pyname = pyname.replace(" ", "")

    @classmethod
    def from_node(cls, arg: c_ast.Node) -> Self:
        print(type(arg.type))
        match arg:
            case c_ast.TypeDecl():
                arg_cname = " ".join(
                    [q for q in arg.quals] + [a for a in arg.type.names]
                )
                arg_pyname = "".join(  # noqa: E501
                    [q.title() for q in arg.quals] + [a.title() for a in arg.type.names]
                ).replace(" ", "")
                return cls(arg_cname, arg_pyname)
            case c_ast.PtrDecl():
                arg_cname = " ".join(
                    [q for q in arg.type.quals]
                    + [a for a in arg.type.type.names]
                    + [q for q in arg.quals]
                )
                arg_pyname = "".join(
                    [q for q in arg.type.quals]
                    + [a for a in arg.type.type.names]
                    + [q for q in arg.quals]
                ).replace(" ", "")
                return cls(arg_cname + " *", arg_pyname + "_ptr")
            case c_ast.ArrayDecl():
                arg_cname = " ".join(  # noqa: E501
                    [q for q in arg.type.quals] + [a for a in arg.type.type.names]
                )
                arg_pyname = "".join(  # noqa: E501
                    [q for q in arg.type.quals] + [a for a in arg.type.type.names]
                ).replace(" ", "")
                if arg.dim:
                    if isinstance(arg.dim, c_ast.Constant):
                        dim = str(arg.dim.value)
                    elif isinstance(arg.dim, c_ast.ID):
                        dim = str(arg.dim.name)
                    else:
                        dim = ""
                else:
                    dim = ""
                return cls(arg_cname + f" [{dim}]", arg_pyname + f"_arr{dim}")
            case _:
                _ty_arg = []
                _ty = arg
                while True:
                    try:
                        _ty_arg.extend(_ty.quals)
                    except AttributeError:
                        pass
                    try:
                        _ty_arg.extend(_ty.names)
                        break
                    except AttributeError:
                        _ty = _ty.type
                arg_cname = " ".join(_ty_arg)
                arg_pyname = "".join(_ty_arg).replace(" ", "")
                return cls(arg_cname, arg_pyname)


@dataclass(slots=True)
class CFuncArg:
    name: str
    ctype: CType


CVarArg = CFuncArg("VA", CType("...", "VarArg"))


@dataclass(slots=True)
class CFunc:
    name: str
    ret_t: CType
    args: list[CFuncArg]
    doc: str


def _parse_arg(arg: c_ast.Node) -> CFuncArg:
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


def parse_func(
    func: Callable, typedefs: list[str] | None = None, verbose: bool = False
) -> list[CFunc]:

    parser = CParser()

    if typedefs:
        COMMON_TYPES.update({_t: _t for _t in typedefs})

    sig = func.__doc__.splitlines()[0]  # type: ignore

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
            if verbose:
                print(f"Parsing {name}")
            func_t = decl.type
            ret_t = CType.from_node(func_t.type)
            args = []
            for arg in func_t.args:
                carg = _parse_arg(arg.type)
                if carg.name is None:
                    carg.name = f"arg{arg_count}"
                arg_count += 1
                args.append(carg)
            cfunc = CFunc(name, ret_t, args, "")
            funcs.append(cfunc)

    return funcs
