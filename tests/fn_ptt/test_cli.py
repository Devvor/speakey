from unittest.mock import patch
from click.testing import CliRunner
from src.cli import main


@patch("src.fn_ptt.manager.FnPttManager")
def test_start_when_already_running(MockManager):
    MockManager.return_value.is_running.return_value = True
    MockManager.return_value.get_status.return_value = {"running": True, "pid": 99}
    result = CliRunner().invoke(main, ["fn-ptt", "start"])
    assert "already running" in result.output


@patch("src.fn_ptt.manager.FnPttManager")
def test_start_success(MockManager):
    MockManager.return_value.is_running.return_value = False
    MockManager.return_value.start.return_value = True
    result = CliRunner().invoke(main, ["fn-ptt", "start"])
    assert "started" in result.output.lower()


@patch("src.fn_ptt.manager.FnPttManager")
def test_stop_when_not_running(MockManager):
    MockManager.return_value.is_running.return_value = False
    result = CliRunner().invoke(main, ["fn-ptt", "stop"])
    assert "not running" in result.output.lower()


@patch("src.fn_ptt.manager.FnPttManager")
def test_stop_success(MockManager):
    MockManager.return_value.is_running.return_value = True
    MockManager.return_value.stop.return_value = True
    result = CliRunner().invoke(main, ["fn-ptt", "stop"])
    assert "stopped" in result.output.lower()


@patch("src.fn_ptt.manager.FnPttManager")
def test_status_not_running(MockManager):
    MockManager.return_value.get_status.return_value = {"running": False}
    result = CliRunner().invoke(main, ["fn-ptt", "status"])
    assert "not running" in result.output.lower()


@patch("src.fn_ptt.manager.FnPttManager")
def test_status_running(MockManager):
    MockManager.return_value.get_status.return_value = {"running": True, "pid": 42}
    result = CliRunner().invoke(main, ["fn-ptt", "status"])
    assert "42" in result.output
