from setuptools import setup # type: ignore

if __name__ == "__main__":
    setup(
        zip_safe=False,
        ext_package="test_module",
        cffi_modules=["test_module/_build.py:ffi_builder"],
    )