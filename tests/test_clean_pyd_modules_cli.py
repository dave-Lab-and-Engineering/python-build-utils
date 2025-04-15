from unittest.mock import patch

from python_build_utils.clean_pyd_modules import clean_by_extensions


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_no_matching_regex(mock_echo, mock_src_packages):
    """Test when no files match the provided regex."""
    # Create mock files
    file1 = mock_src_packages / "module1.pyd"
    file2 = mock_src_packages / "module2.pyd"
    file1.touch()
    file2.touch()

    clean_by_extensions(src_path=mock_src_packages, regex="non_matching_pattern", extension="*.pyd")

    mock_echo.assert_called_with(f"No *.pyd files with 'non_matching_pattern' filter found in {mock_src_packages}.")
    assert file1.exists()
    assert file2.exists()


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_no_files_with_extension(mock_echo, mock_src_packages):
    """Test when no files with the specified extension exist."""
    # Create mock files with different extensions
    file1 = mock_src_packages / "module1.txt"
    file2 = mock_src_packages / "module2.log"
    file1.touch()
    file2.touch()

    clean_by_extensions(src_path=mock_src_packages, regex=None, extension="*.pyd")

    mock_echo.assert_called_with(f"No *.pyd files found in {mock_src_packages}.")
    assert file1.exists()
    assert file2.exists()


@patch("python_build_utils.clean_pyd_modules.click.echo")
def test_clean_by_extensions_partial_regex_match(mock_echo, mock_src_packages):
    """Test when some files match the regex and others do not."""
    # Create mock files
    file1 = mock_src_packages / "module1.pyd"
    file2 = mock_src_packages / "test_module.pyd"
    file3 = mock_src_packages / "another_test_module.pyd"
    file1.touch()
    file2.touch()
    file3.touch()

    clean_by_extensions(src_path=mock_src_packages, regex="test", extension="*.pyd")

    mock_echo.assert_any_call(f"Removing {file2}")
    mock_echo.assert_any_call(f"Removing {file3}")
    assert file1.exists()
    assert not file2.exists()
    assert not file3.exists()
