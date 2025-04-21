import subprocess


def test_main_script(tmp_path):
    log_file = "samples/app1.log"

    output = tmp_path / "report.txt"

    result = subprocess.run([
        "python", "-m", "main",
        log_file,
        "-r", "handlers",
        "-o", str(output)
    ], capture_output=True, text=True)

    print(result.stdout)
    print(result.stderr)

    assert result.returncode == 0
    assert output.exists()
    assert "Total requests: 60\nHANDLER" in output.read_text()
