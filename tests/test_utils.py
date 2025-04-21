import pytest

from app.utils import parse_templates_file, merge_tables, print_table
from collections import defaultdict


@pytest.fixture
def valid_template(tmp_path):
    path = tmp_path / "templates.json"
    path.write_text("""
    {
        "report1": {
            "log_formats": ["<level> - <msg>"],
            "filters": {},
            "x_axis": "level",
            "y_axis": "msg",
            "total": "lines"
        }
    }
    """)
    return str(path)

def test_parse_templates_valid_file_name(valid_template):
    template = parse_templates_file(valid_template, "report1")
    assert isinstance(template, dict)
    assert template["x_axis"] == "level"
    assert template["y_axis"] == "msg"

def test_parse_templates_invalid_file_name(valid_template):
    template = parse_templates_file(valid_template, "unknown")
    assert template == {}

def test_merge_tables():
    t1 = defaultdict(lambda: defaultdict(int), {"A": {"INFO": 2}})
    t2 = defaultdict(lambda: defaultdict(int), {"A": {"INFO": 3}, "B": {"ERROR": 1}})
    merged = merge_tables(t1, t2)
    assert merged["A"]["INFO"] == 5
    assert merged["B"]["ERROR"] == 1

def test_print_table(capsys):
    data = defaultdict(lambda: defaultdict(int), {
        "url1": {"INFO": 2, "ERROR": 1},
        "url2": {"INFO": 1}
    })
    template = {
        "x_axis": "level",
        "y_axis": "url",
        "total": "lines"
    }
    print_table(data, template, )
    out = capsys.readouterr().out
    assert "INFO" in out
    assert "ERROR" in out
    assert "url1" in out
    assert "url2" in out
    assert "3" in out
