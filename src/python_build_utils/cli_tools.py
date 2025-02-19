import click

from . import remove_tarballs, rename_wheel_files


@click.group()
def cli():
    """A collection of CLI tools for Python build utilities."""
    return


cli.add_command(rename_wheel_files)
cli.add_command(remove_tarballs)

if __name__ == "__main__":
    cli()
