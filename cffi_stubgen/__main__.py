from __future__ import annotations

from . import (
    make_stubs,
    get_functions,
    clean_stubs,
    get_stubpath,
)

import importlib

from argparse import ArgumentParser
import sys

def get_arg_parser() -> ArgumentParser:
    
    parser = ArgumentParser(
        prog="cffi-stubgen", description="Generates stubs for specified CFFI module"
    )
    
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="outdir",
        help="The root directory for output stubs (default is same as module)",
        default=None
    )

    parser.add_argument(
        "-t",
        "--typedefs",
        dest="typedefs",
        type=str,
        help="Additional C types that should be defined",
        default=""
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Don't write stubs. Parse module and report errors",
    )
    
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        dest="no_cleanup",
        help="If stubgen fails, do not clean up the incomplete stubs",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Print information during stubgen",
    )

    parser.add_argument(
        "--stub-extension",
        type=str,
        default="pyi",
        dest="extension",
        choices=["pyi", "py"],
        help="The file extension of the generated stubs. "
        "Must be 'pyi' (default) or 'py'",
    )
    
    parser.add_argument(
        "module_name",
        metavar="MODULE_NAME",
        type=str,
        help="module name of the cffi module",
    )
    
    return parser
        
def main() -> int:
    
    cli_parser = get_arg_parser()
    
    args = cli_parser.parse_args(sys.argv[1:])
    
    outdir = args.outdir
    typedefs = args.typedefs.split(" ")
    extension = args.extension
    verbose = args.verbose
    
    module_name = args.module_name
    if not module_name:
        print(
            f"Hey! You gave me an empty module name!",
            file=sys.stderr
        )
        return 1
    try:
        mod = importlib.import_module(module_name)
        if verbose:
            print(f"Found module {module_name}")
    except ImportError as err:
        print(
            f"Hey! It seems that the module {module_name} does not exist. "
            "Have you given me the fully qualified name, like you would type in an import statement?\n"
            "Here is the raised error:\n",
            f"{err}",
            file=sys.stderr
        )
        return 1
    
    if args.dry_run:
        try:
            get_functions(mod, typedefs, verbose)
            if verbose:
                print(f"Dry run completed successfully for module {module_name}")
        except Exception as err:
            print(
                f"Dry run of module {module_name} failed. Here is the cause:\n"
                f"{err}",
                file=sys.stderr
            )
            return 1
    else:
        try:
            make_stubs(mod, outdir, typedefs, extension, verbose)
            if verbose:
                stubpath = get_stubpath(mod, outdir)
                print(f"Stubs for module {module_name} generated at {stubpath}")
        except Exception as err:
            if not args.no_cleanup:
                clean_stubs(mod, outdir)
                print(
                    f"Stub generation of module {module_name} failed. Incomplete stubs have been removed."
                    "Here is the cause for the Exception:\n"
                    f"{err}",
                    file=sys.stderr
                )
            else:
                stubpath = get_stubpath(mod, outdir)
                print(
                    f"Stub generation of module {module_name} failed. "
                    f"--no-cleanup was specified. Incomplete stubs can be found at {stubpath}. "
                    "Here is the cause for the Exception:\n"
                    f"{err}",
                    file=sys.stderr
                )
            return 1
    return 0
        
if __name__ == "__main__":
    sys.exit(main())