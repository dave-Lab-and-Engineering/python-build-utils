import glob
import sys
import sysconfig

import click


@click.command()
@click.option("--dist_dir", default="dist", help="Directory containing wheel files. Default is 'dist'")
@click.option("--python_version_tag", help="Explicitly specify the python version tag. Default is cp{major}{minor}")
@click.option("--platform_tag", help="Explicitly specify the platform tag. Default is sysconfig.get_platform()")
@click.option(
    "--wheel_tag",
    help="Explicitly specify the total wheel tag. "
    "Default is {python_version_tag}-{python_version_tag}-{platform_tag}",
)
def rename_wheel_files(dist_dir, python_version_tag, platform_tag, wheel_tag):
    if wheel_tag:
        build_version_tag = wheel_tag
    else:
        if not python_version_tag:
            python_version_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
        if not platform_tag:
            platform_tag = sysconfig.get_platform().replace("-", "_")
        build_version_tag = f"{python_version_tag}-{python_version_tag}-{platform_tag}"

    dist_dir = dist_dir.rstrip("/")

    for wheel_file in glob.glob(f"{dist_dir}/*py3-none-any.whl"):
        new_file = wheel_file.replace("py3-none-any.whl", f"{build_version_tag}.whl")
        try:
            click.echo(f"Trying to rename {wheel_file} -> {new_file}")
        except FileExistsError as e:
            click.echo(f"{e}")
        else:
            click.echo(f"Renamed {wheel_file} -> {new_file}")
    else:
        click.echo(f"No wheel files found in {dist_dir}")


def main():
    rename_wheel_files()


if __name__ == "__main__":
    main()
