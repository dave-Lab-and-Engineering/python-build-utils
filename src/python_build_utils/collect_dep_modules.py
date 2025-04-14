import json
import subprocess
import sys

import click

from . import __version__


@click.command(name="collect-dep-modules")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option("--package", help="Name of the python package to collect all dependencies")
@click.option(
    "--output", "-o", type=click.Path(writable=True), help="Optional output file to write the dependencies list"
)
def collect_dependencies(package: str, output: str | None) -> None:
    """Collect all the dependencies of a given package using pipdeptree."""
    if not package:
        click.echo("Please provide a package name using --package.")
        return

    click.echo(f"Collecting dependencies for '{package}'...")

    dep_tree = get_dependency_tree()
    package_node = find_package_node(dep_tree, package)

    if not package_node:
        click.echo(f"Package '{package}' not found in the environment.")
        return

    dependencies = collect_dependency_names(package_node["dependencies"])

    click.echo(f"Dependencies for {package}:")
    if not dependencies:
        click.echo(" (No dependencies found)")
    else:
        for dep in dependencies:
            click.echo(f"- {dep}")

    if output:
        with open(output, "w") as f:
            f.write("\n".join(dependencies))
        click.echo(f"Dependencies written to {output}")


def run_safe_subprocess(command: list) -> str:
    """Runs a subprocess safely and returns the output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)  # nosec B603
    except subprocess.CalledProcessError as e:
        click.echo("Subprocess failed.")
        click.echo(e)
        sys.exit(1)
    else:
        return result.stdout  # return moved to else block


def get_dependency_tree() -> list:
    """Run pipdeptree and return the dependency tree as JSON."""
    command = [sys.executable, "-m", "pipdeptree", "--json-tree"]

    if any(arg.startswith("-") and not arg.startswith("--") for arg in command[1:]):
        click.echo("Unsafe short option detected.")
        sys.exit(1)

    stdout = run_safe_subprocess(command)
    return json.loads(stdout)


def find_package_node(dep_tree: list, package: str) -> dict | None:
    """Find the package node in the dependency tree."""
    return next((pkg for pkg in dep_tree if pkg["key"].lower() == package.lower()), None)


def collect_dependency_names(dependencies: list, collected=None) -> list:
    """Recursively collect dependency names."""
    if collected is None:
        collected = []

    for dep in dependencies:
        dep_name = dep["package_name"]
        if dep_name not in collected:
            collected.append(dep_name)
            collect_dependency_names(dep.get("dependencies", []), collected)

    return collected
