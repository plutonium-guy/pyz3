"""
Project initialization utilities for pyz3.

Provides two modes:
  1. Built-in scaffolding (default) — fast, zero extra dependencies
  2. Cookiecutter template (legacy) — richer template with CI/CD, C examples

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
from pathlib import Path

from pyz3.logging_config import get_logger
from pyz3.scaffold import scaffold_project
from pyz3.security import SecurityValidator

logger = get_logger(__name__)


def init_project(
    path: Path,
    package_name: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    description: str | None = None,
    use_interactive: bool = True,
) -> None:
    """
    Initialize a new pyz3 project using built-in scaffolding.

    Args:
        path: Directory to initialize the project in
        package_name: Name of the package (defaults to directory name)
        author_name: Author name (defaults to git config)
        author_email: Author email (defaults to git config)
        description: Project description
        use_interactive: Ignored (kept for backward compatibility)
    """
    name = package_name or path.name
    desc = description or "A Python extension module written in Zig"

    # Parse "Name <email>" format for author
    if author_name and "<" in author_name:
        parts = author_name.split("<")
        author_name = parts[0].strip()
        if len(parts) > 1 and not author_email:
            author_email = parts[1].rstrip(">").strip()

    project_dir = scaffold_project(
        project_dir=path,
        name=name,
        description=desc,
        author_name=author_name,
        author_email=author_email,
    )

    print(f"\n  Created project at {project_dir}\n")
    print("  Next steps:")
    print(f"    cd {project_dir.name}")
    print('    pip install -e ".[dev]"')
    print("    pyz3 develop")
    print("    pytest")
    print()


# Keep backward compatibility alias
init_project_cookiecutter = init_project


def new_project(name: str, path: Path | None = None) -> None:
    """
    Create a new pyz3 project in a new directory.

    Args:
        name: Name of the project
        path: Parent directory (defaults to current directory)
    """
    if path is None:
        path = Path.cwd()

    is_valid, error, sanitized_name = SecurityValidator.sanitize_package_name(name)
    if not is_valid:
        logger.error(f"Invalid project name: {error}")
        print(f"Error: {error}")
        sys.exit(1)

    assert sanitized_name is not None
    project_path = path / sanitized_name

    if project_path.exists():
        logger.error(f"Directory already exists: {sanitized_name}")
        print(f"Error: Directory '{sanitized_name}' already exists!")
        sys.exit(1)

    init_project(project_path, package_name=sanitized_name)
