"""
Automatically generate markdown documentation for all filler modules
via mkdocstrings.
"""

import logging
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path
from string import Template

logger = logging.getLogger("mkdocs")


def get_script_relative_path():  # noqa: D103
    script_path = os.path.abspath(__file__)
    current_directory = os.getcwd()
    return os.path.relpath(script_path, current_directory)


if os.environ.get("CI") != "true":  # always generate in ci/cd
    enabled_env_var_name = "SPEC_TESTS_AUTO_GENERATE_FILES"
    script_name = get_script_relative_path()
    if os.environ.get(enabled_env_var_name) != "true":
        logger.warning(
            f"{script_name}: skipping automatic generation of " "filler doc"
        )
        logger.info(
            f"{script_name}: set env var {enabled_env_var_name} "
            "to 'true' and re-run `mkdocs serve` or `mkdocs build` to "
            "generate filler doc"
        )
        sys.exit(0)
    else:
        logger.info(f"{script_name}: generating filler doc")
        logger.info(
            f"{script_name}: set env var {enabled_env_var_name} "
            "to 'false' and re-run `mkdocs serve` or `mkdocs build` to "
            "disable filler doc generation"
        )


# mkdocstrings filter doc:
# https://mkdocstrings.github.io/python/usage/configuration/members/#filters
MARKDOWN_TEMPLATE = Template(
    textwrap.dedent(
        """
        # $title

        !!! example "Generate fixtures for these test cases with:"
            ```console
            pytest -v $pytest_test_path
            ```

        ::: $package_name
            options:
              filters: ["!^_[^_]", "![A-Z]{2,}", "!pytestmark"]
        """
    )
)


def create_top_level_readme():  # noqa: D103
    with open(target_dir / "README", "w") as f:
        f.write(
            "Warning: The entire file and directory structure within and below "
            "this directory is automatically generated by "
            f"{get_script_relative_path()}.\n"
            "- Don't manually add files to this directory.\n"
            "- Don't edit files in this directory.\n"
        )


def create_fillers_pages_file():
    """
    Write a .pages file to be used by the mkdocs-awesome-pages-plugin
    so that the material tabs bar links to index.md and the "first"
    test module.
    """
    with open(target_dir / ".pages", "w") as f:
        f.write("nav:\n" "  - Home: index.md\n" "  - ...")


def apply_name_filters(input_string: str):  # noqa: D103
    regexes = [
        (r"vm", "VM"),
        (r"eips", "EIPS"),
        (r"eip([1-9]{1,5})", r"EIP-\1"),
    ]

    for pattern, replacement in regexes:
        input_string = re.sub(
            pattern, replacement, input_string, flags=re.IGNORECASE
        )

    return input_string


source_directory = "fillers"
target_dir = Path("docs") / "_auto_gen_fillers"

if os.path.exists(target_dir):
    shutil.rmtree(target_dir)
os.makedirs(target_dir)

create_top_level_readme()
create_fillers_pages_file()

for root, _, files in os.walk(source_directory):
    if "__pycache__" in root:
        continue
    root_filtered = apply_name_filters(root)
    relative_filler_path = Path(root_filtered).relative_to("fillers")
    output_directory = target_dir / relative_filler_path
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for file in files:
        if file == "conftest.py":
            continue
        if file == "__init__.py":
            output_file_path = output_directory / "index.md"
            package_name = root.replace(os.sep, ".")
            pytest_test_path = root
            markdown_title = os.path.basename(root)

        elif file.endswith(".py"):
            file_no_ext = os.path.splitext(file)[0]
            output_file_path = output_directory / f"{file_no_ext}.md"
            package_name = os.path.join(root, file_no_ext).replace(os.sep, ".")
            pytest_test_path = os.path.join(root, file)
            markdown_title = file_no_ext

        elif file.endswith(".md"):
            source = Path(root) / file
            if file == "README.md":
                # We already write an index.md that contains the docstrings
                # from the __init__.py. Both and index and a readme are not
                # supported by the awesome-pages plugin.
                target = output_directory / "test_cases.md"
            else:
                target = output_directory
            shutil.copy(source, target)

        markdown_title = apply_name_filters(markdown_title)

        with open(output_file_path, "w") as f:
            f.write(
                MARKDOWN_TEMPLATE.substitute(
                    title=markdown_title,
                    package_name=package_name,
                    pytest_test_path=pytest_test_path,
                )
            )
