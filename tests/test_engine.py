from app.core.engine import LogParser

def test_format_to_regex():
    regex = LogParser.format_to_regex("<level>: <message>")
    match = regex.match("INFO: Hello World")

    assert match
    assert match.group("level") == "INFO"
    assert match.group("message") == "Hello World"

def test_best_match():
    parser = LogParser({
        "log_formats": ["<date> <time> <level>: <msg>", "<level>: <msg>", "<asctime> <level>: <msg>"],
        "filters": {},
        "x_axis": "msg",
        "y_axis": "level"
    }, "dummy.log", None)

    match = parser.best_match("ERROR: disk full", ["<level>: <msg>"])
    assert match
    pattern, data = match
    assert pattern == "<level>: <msg>"
    assert data["level"] == "ERROR"
    assert data["msg"] == "disk full"
