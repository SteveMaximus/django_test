import pytest
from unittest.mock import patch
import os
from main import main
from funcs import remove_None_string, get_endpoint, get_logging_level, handler, report, complete_reports
from io import StringIO
import logging  # Import the logging module

def test_remove_None_string():
    assert remove_None_string(["a", "", "b"]) == ["a", "b"]
    assert remove_None_string(["", "", ""]) == []
    assert remove_None_string(["a", "b", "c"]) == ["a", "b", "c"]

def test_get_endpoint():
    assert get_endpoint("GET /api/users HTTP/1.1") == "/api/users"
    assert get_endpoint("No endpoint here") is None
    assert get_endpoint("GET /test?param=value HTTP/1.1") == "/test"  # Regex now ignores query params
    assert get_endpoint("GET /test   HTTP/1.1") == "/test"
    assert get_endpoint("GET /test/subpath HTTP/1.1") == "/test/subpath" #Subpaths
    assert get_endpoint("GET / HTTP/1.1") == "/"  # Root endpoint
    assert get_endpoint("GET /api/users  param=value HTTP/1.1") == "/api/users"

def test_get_logging_level():
    assert get_logging_level("INFO django.request blabla") == "INFO"
    assert get_logging_level("No logging level here") is None
    assert get_logging_level("Some INFO django.request.middleware blabla") == "Some"  # Multiple words

def test_handler_success(tmpdir):
    log_file = tmpdir.join("test.log")
    log_file.write("GET /api/users INFO django.request\nGET /api/users DEBUG django.request\n")
    total_requests, endpoint_data = handler([str(log_file)])
    assert total_requests == 2
    assert endpoint_data == {"/api/users": {"DEBUG": 1, "INFO": 1, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}}

def test_handler_empty_file_list():
    assert handler([]) == (0, {})

def test_handler_file_not_found():
    with pytest.raises(FileNotFoundError):
        handler(["non_existent_file.log"])  # Test exception raised

def test_handler_no_django_request(tmpdir):
    log_file = tmpdir.join("test.log")
    log_file.write("GET /api/users HTTP/1.1\n")
    total_requests, endpoint_data = handler([str(log_file)])
    assert total_requests == 0
    assert endpoint_data == {}

def test_report_handler(tmpdir):
    log_file = tmpdir.join("test.log")
    log_file.write("GET /api/users INFO django.request\n")
    assert report("handler", [str(log_file)]) == (1, {'/api/users': {'DEBUG': 0, 'INFO': 1, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}})

def test_report_default(caplog):
    with caplog.at_level(logging.WARNING):
        assert report("unknown", ["file1.log"]) == []
        assert "Unknown report type: unknown" in caplog.text

def test_complete_reports_handler(tmpdir):
    log_file = tmpdir.join("test.log")
    log_file.write("GET /api/users INFO django.request\n")
    result = complete_reports(f"{str(log_file)} --report handler")
    assert result == (1, {'/api/users': {'DEBUG': 0, 'INFO': 1, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}})

def test_complete_reports_no_report_type():
    assert complete_reports("file1.log") == (0, {})

def test_complete_reports_empty_input():
    assert complete_reports("") == (0, {})

def test_complete_reports_mixed_logs(tmpdir):
    log_file = tmpdir.join("test.log")
    log_file.write("GET /endpoint1 INFO django.request\nPOST /endpoint2 DEBUG django.request\nGET /endpoint1 WARNING django.request\n")
    result = complete_reports(f"{str(log_file)} --report handler")
    assert result == (3, {'/endpoint1': {'DEBUG': 0, 'INFO': 1, 'WARNING': 1, 'ERROR': 0, 'CRITICAL': 0}, '/endpoint2': {'DEBUG': 1, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}})

def test_main_success(tmpdir, capsys):
    log_file = tmpdir.join("test.log")
    log_file.write("GET /api/users INFO django.request\n")
    with patch("builtins.input", return_value=f"{str(log_file)} --report handler"):
        main()
    captured = capsys.readouterr()
    assert "Total requests: 1" in captured.out
    assert "/api/users" in captured.out

