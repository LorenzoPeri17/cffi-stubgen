from cffi import FFI # type: ignore

import os
CSRC_FOLDER = os.path.join(os.pardir, 'csrc')

import sys
sys.path.append('.')

ffi_builder = FFI()

# Add the cdefs
with open(os.path.join(CSRC_FOLDER, "example.h")) as f:
    lines = f.readlines()
    lines_rem = [line for line in lines if "#" not in line]
    ffi_builder.cdef("".join(lines_rem))
        
ffi_builder.set_source(
    module_name="_example", # This is the module name that cffi-stubgen needs
    source=
    """
    #include "example.h"
    """,
    sources = [os.path.join(CSRC_FOLDER, "example.c")],
    include_dirs=[CSRC_FOLDER]
)

if __name__ == "__main__":
    ffi_builder.compile(verbose=True)
    