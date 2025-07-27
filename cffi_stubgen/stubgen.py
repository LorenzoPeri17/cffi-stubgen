from __future__ import annotations

import os
import inspect
import shutil

from pathlib import Path

from types import ModuleType
from typing import Literal

from .functions import parse_func, CType, CFunc, CVarArg

ffi_stub = """
from cffi import FFI

from typing import (
    Self,
    Any,
    TypeAlias
)

CDATA : TypeAlias = FFI.CData
CTYPE : TypeAlias = FFI.CType

class _FFI_T(FFI):
    def cast(self: Self, cdecl: str | CTYPE, source: Any) -> CDATA: ...

ffi : _FFI_T = ...

"""

lib_stub = """
from cffi import FFI

from typing import (
    Annotated,
    TypeAlias,
    Sequence
)

CDATA : TypeAlias = FFI.CData

"""


def get_functions(
    mod: ModuleType, typedefs: list[str] | None = None, verbose: bool = False
) -> tuple[list[CFunc], list[CType]]:

    funcs: list[CFunc] = []
    ctypes: list[CType] = []

    for name, obj in inspect.getmembers(mod.lib):
        if name.startswith("__"):
            continue
        func = parse_func(obj, typedefs=typedefs, verbose=verbose)
        for _f in func:
            _f.doc = obj.__doc__
            ctypes.append(_f.ret_t)
            for _a in _f.args:
                if _a.ctype == CVarArg.ctype:
                    continue
                ctypes.append(_a.ctype)
        funcs.extend(func)

    ctypes = list(set(ctypes))  # deduplicate

    return funcs, ctypes


def get_stubpath(mod: ModuleType, outdir: str | Path | None = None) -> Path:

    if outdir is None:
        outdir = os.path.dirname(mod.__file__)  # type:ignore
    else:
        if not os.path.isdir(outdir):
            raise FileNotFoundError(
                f"The specified directory {outdir} doe not appear to exist"
            )

    stubpath = Path(outdir) / mod.__name__.split(".")[-1]  # type:ignore

    return stubpath


def clean_stubs(mod: ModuleType, outdir: str | Path | None = None) -> None:
    stubpath = get_stubpath(mod, outdir)
    shutil.rmtree(stubpath)


def make_stubs(
    mod: ModuleType,
    outdir: str | Path | None = None,
    typedefs: list[str] | None = None,
    extension: Literal["pyi", "py"] = "pyi",
    verbose: bool = False,
) -> None:

    stubpath = get_stubpath(mod, outdir)
    stubpath.mkdir(exist_ok=True)

    with open(stubpath / "py.typed", "w"):
        pass

    with open(stubpath / f"__init__.{extension}", "w") as f:
        f.write(ffi_stub)

    libpath = stubpath / "lib"
    libpath.mkdir(exist_ok=True)

    funcs, ctypes = get_functions(mod, typedefs, verbose)

    with open(libpath / f"__init__.{extension}", "w") as f:
        f.write(lib_stub)

        lines = []
        for _t in ctypes:
            line = f"{_t.pyname}: TypeAlias = Annotated[CDATA, '{_t.cname}']\n"
            lines.append(line)

        lines.append("\n")
        f.writelines(lines)

        for func in funcs:
            if verbose:
                print(f"Writing stub for function {func.name}")
            f.write(f"def {func.name}(\n")
            for arg in func.args:
                if arg == CVarArg:
                    f.write("    *args: Sequence[CDATA],\n")
                else:
                    f.write(f"    {arg.name}: {arg.ctype.pyname},\n")
            f.write(f"    ) -> {func.ret_t.pyname}:\n")
            f.write('    """\n')
            f.writelines(
                ["    " + line.strip() + "\n" for line in func.doc.split("\n")]
            )
            f.write('    """\n')
            f.write("    ...\n")

        f.write("\n")
