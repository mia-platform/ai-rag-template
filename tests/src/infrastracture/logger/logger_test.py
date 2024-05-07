import os
from unittest.mock import patch

import pytest

from src.infrastracture.logger import get_logger

@pytest.mark.parametrize("log_level,log_method", [
    ('DEBUG', 'debug'),
    ('INFO', 'info'),
    ('WARNING', 'warning'),
    ('ERROR', 'error'),
    ('CRITICAL', 'critical'),
])
@patch('socket.gethostname')
@patch('os.getpid')
@patch('time.time')
#pylint: disable=R0913
def test_get_logger(mock_time, mock_getpid, mock_gethostname, capfd, snapshot, log_level, log_method):
    snapshot.snapshot_dir = os.path.join(os.path.dirname(__file__), 'snapshots')
    # Arrange
    os.environ['LOG_LEVEL'] = log_level
    mock_time.return_value = 1628000000.0
    mock_getpid.return_value = 1234
    mock_gethostname.return_value = 'mocked_hostname'

    # Act
    logger_instance = get_logger()
    getattr(logger_instance, log_method)('Test log message')

    # Assert
    out, _ = capfd.readouterr()
    snapshot.assert_match(out, f'logger_output_{log_level}')
