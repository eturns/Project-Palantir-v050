from desktop_analysis_adapter import run_analysis

def test_desktop_adapter_calls_existing_analysis_workflow(
    monkeypatch,
):
    captured = {}
    expected_result = {"analysis": "TEST_RESULT"}

    def fake_run_analysis_workflow(
        file_path,
        *,
        print_report=True,
    ):
        captured["file_path"] = file_path
        return expected_result

    monkeypatch.setattr(
        "desktop_analysis_adapter.run_analysis_workflow",
        fake_run_analysis_workflow,
    )

    result = run_analysis("test_army.json")

    assert captured["file_path"] == "test_army.json"
    assert result is expected_result

def test_desktop_adapter_returns_none_when_import_fails(
    monkeypatch,
):
    def fake_run_analysis_workflow(
        file_path,
        *,
        print_report=True,
    ):
        return None

    monkeypatch.setattr(
        "desktop_analysis_adapter.run_analysis_workflow",
        fake_run_analysis_workflow,
    )

    result = run_analysis("invalid_army.json")

    assert result is None

def test_desktop_adapter_uses_non_console_workflow(
    monkeypatch,
):
    captured = {}

    def fake_run_analysis_workflow(
        file_path,
        *,
        print_report=True,
    ):
        captured["file_path"] = file_path
        captured["print_report"] = print_report
        return {"analysis": "TEST_RESULT"}

    monkeypatch.setattr(
        "desktop_analysis_adapter.run_analysis_workflow",
        fake_run_analysis_workflow,
    )

    result = run_analysis("test_army.json")

    assert captured["file_path"] == "test_army.json"
    assert captured["print_report"] is False
    assert result == {"analysis": "TEST_RESULT"}
    