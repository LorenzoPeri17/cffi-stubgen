[![Build Status](https://github.com/LorenzoPeri17/cffi-stubgen/actions/workflows/tests.yaml/badge.svg)](https://github.com/<user>/<repo>/actions)
[![PyPI version](https://img.shields.io/pypi/v/cffi-stubgen.svg)](https://pypi.org/project/cffi-stubgen/)
[![License](https://img.shields.io/pypi/l/cffi-stubgen.svg)](https://github.com/LorenzoPeri17/cffi-stubgen/blob/main/LICENSE)
[![Python versions](https://img.shields.io/pypi/pyversions/cffi-stubgen.svg)](https://pypi.org/project/cffi-stubgen/)

# `cffi-stubgen`

`cffi-stubgen` is a tool for automatically generating [PEP 561](https://www.python.org/dev/peps/pep-0561/) type stubs (`.pyi` files) for Python modules built with [cffi](https://cffi.readthedocs.io/). This makes it easy to add type hints to your CFFI-based extensions, unlocking the full power of static type checking and IDE features.

## Why generate stubs?

- **Type checking:** Use tools like `mypy` to catch bugs before runtime.
- **IDE support:** Get autocompletion, inline documentation, and better navigation in editors like VS Code and PyCharm.
- **Documentation:** Stubs make your API clearer for users and contributors.

## How does it work?

`cffi-stubgen` inspects the compiled CFFI module (not your Python source!) and generates stubs for all the functions and types exposed via CFFI. You simply point it at the built module, and it does the rest.

## Quick Example

Suppose you have a CFFI module built in `example_module._example`. After installing your package, just run:

```sh
cffi-stubgen example_module._example
```

This will generate `.pyi` stubs for your module, ready for type checking and IDE use.

For a full walkthrough, see the [example/README.md](https://github.com/LorenzoPeri17/cffi-stubgen/tree/main/example) in this repository.

It will show you how `cffi-stubgen` can make `mypy` (and your IDE) aware of the arguments of

``` C
int add(int a, int b);
```

![VSCode Autocomplete Example](https://github.com/LorenzoPeri17/cffi-stubgen/blob/main/example/assets/vscode.png)

## Command Line Options

`cffi-stubgen` provides several options to customize stub generation:

- `-o`, `--output-dir`: Set the output directory for stubs (default: same as module).
- `-t`, `--typedefs`: Additional C types to define (space-separated).
- `--dry-run`: Parse the module and report errors, but don’t write stubs.
- `--no-cleanup`: If stub generation fails, do not remove incomplete stubs.
- `--verbose`: Print detailed information during stub generation.
- `--stub-extension`: Choose the file extension for stubs (`pyi` [default] or `py`).
- `MODULE_NAME`: The fully qualified name of your cffi module (e.g., `example_module._example`).

## Learn More

See the [example](https://github.com/LorenzoPeri17/cffi-stubgen/tree/main/example) for a hands-on guide!
