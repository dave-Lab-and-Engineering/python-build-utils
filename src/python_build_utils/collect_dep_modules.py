import json
import subprocess

import click

from . import __version__


@click.command(name="collect-dep-modules")
@click.version_option(__version__, "--version", "-v", message="%(version)s", help="Show the version and exit.")
@click.option("--package", help="Name of the python package to collect all dependencies")
def collect_dependencies(package: str) -> None:
    """Collect all the dependencies of a given package using pipdeptree."""

    if not package:
        click.echo("Please provide a package name using --package.")
        return

    click.echo(f"Collecting dependencies for '{package}'...")

    try:
        # Run pipdeptree as subprocess to get JSON dependency tree
        result = subprocess.run(["pipdeptree", "--json-tree"], capture_output=True, text=True, check=True)

        dep_tree = json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        click.echo("Failed to run pipdeptree.")
        click.echo(e)
        return

    # Find the package in the tree
    package_node = next((pkg for pkg in dep_tree if pkg["key"].lower() == package.lower()), None)

    if not package_node:
        click.echo(f"Package '{package}' not found in the environment.")
        return

    click.echo(f"Dependencies for {package}:")
    if not package_node["dependencies"]:
        click.echo(" (No dependencies found)")
        return

    def print_deps(deps, level=1):
        for dep in deps:
            dep_name = dep["key"]
            dep_version = dep["installed_version"]
            click.echo("  " * level + f"- {dep_name} ({dep_version})")
            print_deps(dep.get("dependencies", []), level + 1)

    print_deps(package_node["dependencies"])
