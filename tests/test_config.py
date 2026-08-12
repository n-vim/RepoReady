from pathlib import Path

import pytest

from repoready.config import CONFIG_FILE_NAME, load_config, write_default_config
from repoready.exceptions import ConfigError
from repoready.models import ProjectProfile, SetupLevel


def test_load_default_config_when_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path)
    assert config.profile is ProjectProfile.AUTO


def test_write_and_load_config(tmp_path: Path) -> None:
    write_default_config(tmp_path)
    config = load_config(tmp_path)
    assert config.level is SetupLevel.STANDARD


def test_load_custom_config(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILE_NAME).write_text("profile: python\nlevel: strict\n", encoding="utf-8")
    config = load_config(tmp_path)
    assert config.profile is ProjectProfile.PYTHON
    assert config.level is SetupLevel.STRICT


def test_invalid_config_raises(tmp_path: Path) -> None:
    (tmp_path / CONFIG_FILE_NAME).write_text("[", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(tmp_path)
