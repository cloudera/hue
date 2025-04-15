"""
Rewrites absolute paths in `.pth` files inside a Python virtualenv to be relative.

Used to ensure that Hue's virtual environments are relocatable across systems.
Complements `virtualenv-make-relocatable` for robust deployment support.
"""

import os
import site
import shutil
from pathlib import Path


def relocate_pth_with_relative_paths(site_packages: str, make_backup: bool = True) -> None:
    """
    Converts absolute paths in .pth files to relative paths, relative to the site-packages directory.
    Only modifies paths that:
      - Exist on the filesystem.
      - Are not already within the site-packages directory.
    Ignores empty lines and lines starting with 'import'.

    Parameters:
        site_packages (str): Path to the site-packages directory.
        make_backup (bool): Whether to save a backup copy of each modified .pth file.
    """
    site_packages = Path(site_packages).resolve()
    pth_files = site_packages.glob("*.pth")

    for pth_file in pth_files:
        updated_lines = []
        modified = False

        with pth_file.open("r") as f:
            for line in f:
                stripped = line.strip()

                # Preserve empty lines and import statements
                if not stripped or stripped.startswith("import"):
                    updated_lines.append(line.rstrip())
                    continue

                path = Path(stripped)
                if path.is_absolute() and path.exists():
                    # Only convert if path is outside site-packages
                    if site_packages not in path.parents:
                        try:
                            # Compute relative path to site-packages
                            relative_path = os.path.relpath(path, site_packages)
                            updated_lines.append(relative_path)
                            modified = True
                        except Exception as e:
                            print(f"️Failed to compute relative path for: {path}\n   Error: {e}")
                            updated_lines.append(stripped)  # fallback: keep original
                    else:
                        updated_lines.append(stripped)
                else:
                    updated_lines.append(stripped)

        if modified:
            if make_backup:
                backup_path = pth_file.with_suffix(pth_file.suffix + ".bak")
                shutil.copy(pth_file, backup_path)

            with pth_file.open("w") as f:
                f.write("\n".join(updated_lines) + "\n")

            print(f"Rewritten with relative paths: {pth_file.name}")
        else:
            print(f"No changes needed: {pth_file.name}")


if __name__ == "__main__":
    site_packages_dir = site.getsitepackages()[0]
    relocate_pth_with_relative_paths(site_packages_dir)
