from desktop_analysis_adapter import run_analysis

def test_desktop_adapter_builds_view_model_from_analysis_result(
    monkeypatch,
):
    captured = {}

    raw_result = {
        "analysis": "RAW_RESULT",
    }

    expected_view_model = {
        "army_name": "Test Army",
    }

    def fake_run_analysis_workflow(
        file_path,
        *,
        print_report=True,
    ):
        captured["file_path"] = file_path
        captured["print_report"] = print_report
        return raw_result

    def fake_build_desktop_analysis_view_model(
        result,
    ):
        captured["view_model_input"] = result
        return expected_view_model

    monkeypatch.setattr(
        "desktop_analysis_adapter.run_analysis_workflow",
        fake_run_analysis_workflow,
    )

    monkeypatch.setattr(
        "desktop_analysis_adapter.build_desktop_analysis_view_model",
        fake_build_desktop_analysis_view_model,
    )

    result = run_analysis("test_army.json")

    assert captured["file_path"] == "test_army.json"
    assert captured["print_report"] is False
    assert captured["view_model_input"] is raw_result
    assert result is expected_view_model

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

    raw_result = {
        "analysis": "TEST_RESULT",
    }

    expected_view_model = {
        "army_name": "Test Army",
    }

    def fake_run_analysis_workflow(
        file_path,
        *,
        print_report=True,
    ):
        captured["file_path"] = file_path
        captured["print_report"] = print_report
        return raw_result

    monkeypatch.setattr(
        "desktop_analysis_adapter.run_analysis_workflow",
        fake_run_analysis_workflow,
    )

    monkeypatch.setattr(
        "desktop_analysis_adapter.build_desktop_analysis_view_model",
        lambda result: expected_view_model,
    )

    result = run_analysis("test_army.json")

    assert captured["file_path"] == "test_army.json"
    assert captured["print_report"] is False
    assert result is expected_view_model