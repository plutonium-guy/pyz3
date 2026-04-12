import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestInitCommand:
    def test_init_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "pyz3", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "init" in result.stdout

    def test_init_in_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pyz3",
                    "init",
                    "-n",
                    "test_package",
                    "--no-interactive",
                ],
                cwd=tmppath,
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0, f"Init failed. Output: {result.stdout}\nError: {result.stderr}"

            # Scaffold creates files in cwd with package name
            assert (tmppath / "pyproject.toml").exists(), "pyproject.toml not created"
            assert (tmppath / "src").exists(), "src/ not created"
            assert (tmppath / "test").exists(), "test/ not created"

            # Verify pyproject.toml content
            pyproject = (tmppath / "pyproject.toml").read_text()
            assert "test_package" in pyproject
            assert "hatchling" in pyproject

    def test_new_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pyz3",
                    "new",
                    "my_test_project",
                    "-p",
                    str(tmppath),
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0, f"New failed. Output: {result.stdout}\nError: {result.stderr}"

            project_path = tmppath / "my_test_project"
            assert project_path.exists(), "Project directory not created"
            assert (project_path / "pyproject.toml").exists(), "pyproject.toml not created"
            assert (project_path / "src" / "my_test_project.zig").exists(), "Zig source not created"
            assert (project_path / "test" / "test_my_test_project.py").exists(), "Test file not created"
            assert (project_path / "my_test_project" / "__init__.py").exists(), "Package __init__.py not created"
            assert (project_path / "build.zig.zon").exists(), "build.zig.zon not created"
            assert (project_path / ".gitignore").exists(), ".gitignore not created"

    def test_new_duplicate_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create first
            subprocess.run(
                [sys.executable, "-m", "pyz3", "new", "dupe_test", "-p", str(tmppath)],
                capture_output=True,
                text=True,
            )

            # Try again — should fail
            result = subprocess.run(
                [sys.executable, "-m", "pyz3", "new", "dupe_test", "-p", str(tmppath)],
                capture_output=True,
                text=True,
            )
            assert result.returncode != 0

    def test_new_generated_zig_uses_correct_api(self):
        """Verify the generated Zig code uses correct pyz3 API."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            subprocess.run(
                [sys.executable, "-m", "pyz3", "new", "api_check", "-p", str(tmppath)],
                capture_output=True,
                text=True,
                check=True,
            )

            zig_src = (tmppath / "api_check" / "src" / "api_check.zig").read_text()
            assert "py.PyString.createFmt" in zig_src, "Should use PyString.createFmt"
            assert "py.rootmodule" in zig_src, "Should have rootmodule"
            assert "py.class" in zig_src, "Should have class definition"
            assert "PyObject.fromSlice" not in zig_src, "Should NOT use non-existent fromSlice"


class TestRunCommand:
    def test_run_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "pyz3", "run", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "run" in result.stdout


class TestDeployCommand:
    def test_deploy_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "pyz3", "deploy", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "deploy" in result.stdout

    def test_deploy_without_dist_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pyz3",
                    "deploy",
                    "--dist-dir",
                    f"{tmpdir}/nonexistent",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode != 0
            combined = result.stdout + result.stderr
            assert "does not exist" in combined or "twine" in combined

    def test_deploy_empty_dist_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pyz3",
                    "deploy",
                    "--dist-dir",
                    tmpdir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode != 0
            combined = result.stdout + result.stderr
            assert "No wheel" in combined or "No distribution" in combined or "twine" in combined


class TestCheckCommand:
    def test_check_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "pyz3", "check", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "check" in result.stdout

    def test_check_without_dist_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pyz3",
                    "check",
                    "--dist-dir",
                    f"{tmpdir}/nonexistent",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode != 0 or "twine" in (result.stdout + result.stderr)


class TestTemplateIntegration:
    def test_scaffold_generates_valid_project(self):
        """Test that scaffold_project creates all required files."""
        from pyz3.scaffold import scaffold_project

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "scaffold_test"
            scaffold_project(
                project_dir=project_dir,
                name="scaffold_test",
                description="Test",
                author_name="Test",
                author_email="test@test.com",
            )

            required_files = [
                "pyproject.toml",
                "build_hook.py",
                "build.zig.zon",
                "README.md",
                ".gitignore",
                "src/scaffold_test.zig",
                "test/test_scaffold_test.py",
                "test/__init__.py",
                "scaffold_test/__init__.py",
            ]

            for f in required_files:
                assert (project_dir / f).exists(), f"Missing: {f}"

    def test_legacy_template_exists(self):
        """Legacy cookiecutter template still present for reference."""
        from pyz3 import init

        pyz3_package = Path(init.__file__).parent
        template_path = pyz3_package / "pyZ3-template"
        assert template_path.exists(), f"Template directory not found at {template_path}"
