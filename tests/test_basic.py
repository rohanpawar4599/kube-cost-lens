from collector import parse_cpu, parse_memory

def test_millicores():
    assert parse_cpu("250m") == 0.25

def test_whole_cores():
    assert parse_cpu("2") == 2.0

def test_mebibytes():
    assert parse_memory("512Mi") == 512.0

def test_gibibytes():
    assert parse_memory("1Gi") == 1024.0
