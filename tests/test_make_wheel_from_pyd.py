
from python_build_utils.pyd2wheel import pyd2wheel

def test_make_wheel(tmpdir):

    # create a simple pyd file to test
    #
    # the name should follow the python conventions for naming
    #
    # name ["-" version ["-py" pyver ["-" required_platform]]] "." ext
    #
    # ref: https://setuptools.pypa.io/en/latest/deprecated/python_eggs.html
    #
    # example: DAVEcore.cp311-win_amd64.pyd

    filename = 'dummy-0.1.0-py311-win_amd64.pyd'

    pyd = tmpdir / filename

    with open(pyd, 'w') as f:
        f.write('print("hello")')

    # create a wheel from the pyd file
    # the wheel should be created in the same directory as the pyd file

    result = pyd2wheel(pyd_file = pyd)

    assert result.exists()


def test_make_wheel_format2(tmpdir):

    # create a simple pyd file to test
    # different name convention

    filename = 'DAVEcore.cp310-win_amd64.pyd'

    pyd = tmpdir / filename


    with open(pyd, 'w') as f:
        f.write('print("hello")')

    # create a wheel from the pyd file
    # the wheel should be created in the same directory as the pyd file

    result = pyd2wheel(pyd_file = pyd, version = '1.2.3')

    assert result.exists()

if __name__ == '__main__':
    filename = r"C:\data\vf\DAVEcore\x64\Release\DAVEcore.cp311-win_amd64.pyd"
    pyd2wheel(pyd_file = filename, version = '2025.1.0')