import sys
import importlib
import importlib.util
import pathlib
import subprocess

import pytest #type: ignore

EXAMPLE_MOD = "example_module._example"
EXAMPLE_STUB = "_example"

def _find_example_module():
    # Try to import from the venv site-packages
    try:
        spec = importlib.util.find_spec(EXAMPLE_MOD)
        if not spec or not spec.origin:
            pytest.skip("example_module._example not found in environment")
        return spec
    except ModuleNotFoundError:
        pytest.skip("example_module._example not found in environment")

def _stub_path(tmpdir):
    # Where the stubs should be generated
    return pathlib.Path(tmpdir) / EXAMPLE_STUB

def test_cli_stubgen_basic(tmp_path):
    spec = _find_example_module()
    # Run the CLI as a module
    result = subprocess.run([
        sys.executable, "-m", "cffi_stubgen",
        "-o", str(tmp_path),
        EXAMPLE_MOD
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"Stubgen failed: {result.stderr}"
    stubdir = _stub_path(tmp_path)
    assert (stubdir / "__init__.pyi").exists(), "Stub __init__.pyi not generated"
    assert (stubdir / "py.typed").exists(), "py.typed not generated"
    libdir = stubdir / "lib"
    assert (libdir / "__init__.pyi").exists(), "lib/__init__.pyi not generated"

def test_cli_stubgen_dry_run(tmp_path):
    spec = _find_example_module()
    result = subprocess.run([
        sys.executable, "-m", "cffi_stubgen",
        "--dry-run",
        EXAMPLE_MOD
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"Dry run failed: {result.stderr}"
    # Should not generate any files
    stubdir = _stub_path(tmp_path)
    assert not stubdir.exists(), "Stub directory should not be created in dry run"

def test_cli_stubgen_no_cleanup(tmp_path):
    # Simulate failure by passing a non-existent module
    result = subprocess.run([
        sys.executable, "-m", "cffi_stubgen",
        "--no-cleanup",
        "not_a_real_module"
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert "does not exist" in result.stderr
