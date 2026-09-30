import desktop_app


def test_select_button_calls_existing_file_selector(
    monkeypatch,
):
    calls = []

    class FakeRoot:
        def title(self, value):
            calls.append(
                ("title", value)
            )

        def mainloop(self):
            calls.append(
                ("mainloop",)
            )

    class FakeButton:
        def __init__(
            self,
            root,
            *,
            text,
            command,
        ):
            calls.append(
                ("button", text)
            )
            self.command = command

        def pack(self):
            calls.append(
                ("pack",)
            )

    class FakeLabel:
        def __init__(
            self,
            root,
            *,
            text,
        ):
            pass

        def config(
            self,
            *,
            text,
        ):
            pass

        def pack(self):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Button",
        FakeButton,
    )

    monkeypatch.setattr(
        desktop_app,
        "Label",
        FakeLabel,
    )

    monkeypatch.setattr(
        desktop_app,
        "select_mesbg_json_file",
        lambda: calls.append(
            ("select_file",)
        ),
    )

    desktop_app.launch_desktop_app()

    button = next(
        call
        for call in calls
        if call[0] == "button"
    )

    # Retrieve the created button from the patched class
    # by launching a second instance with a captured command.
    captured = {}

    class CapturingButton(FakeButton):
        def __init__(
            self,
            root,
            *,
            text,
            command,
        ):
            super().__init__(
                root,
                text=text,
                command=command,
            )
            captured["command"] = command

    monkeypatch.setattr(
        desktop_app,
        "Button",
        CapturingButton,
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    assert (
        "select_file",
    ) in calls

def test_selected_file_is_passed_to_desktop_analysis_adapter(
    monkeypatch,
):
    calls = []
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def mainloop(self):
            pass

    class FakeButton:
        def __init__(
            self,
            root,
            *,
            text,
            command,
        ):
            captured["command"] = command

        def pack(self):
            pass

    class FakeLabel:
        def __init__(
            self,
            root,
            *,
            text,
        ):
            pass

        def config(
            self,
            *,
            text,
        ):
            pass

        def pack(self):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Button",
        FakeButton,
    )

    monkeypatch.setattr(
        desktop_app,
        "Label",
        FakeLabel,
    )

    monkeypatch.setattr(
        desktop_app,
        "select_mesbg_json_file",
        lambda: "army.json",
    )

    monkeypatch.setattr(
        desktop_app,
        "run_analysis",
        lambda file_path: calls.append(
            ("run_analysis", file_path)
        ),
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    assert calls == [
        (
            "run_analysis",
            "army.json",
        )
    ]

def test_cancelled_file_selection_does_not_run_analysis(
    monkeypatch,
):
    calls = []
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def mainloop(self):
            pass

    class FakeButton:
        def __init__(
            self,
            root,
            *,
            text,
            command,
        ):
            captured["command"] = command

        def pack(self):
            pass

    class FakeLabel:
        def __init__(
            self,
            root,
            *,
            text,
        ):
            pass

        def config(
            self,
            *,
            text,
        ):
            pass

        def pack(self):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Button",
        FakeButton,
    )

    monkeypatch.setattr(
        desktop_app,
        "Label",
        FakeLabel,
    )

    monkeypatch.setattr(
        desktop_app,
        "select_mesbg_json_file",
        lambda: None,
    )

    monkeypatch.setattr(
        desktop_app,
        "run_analysis",
        lambda file_path: calls.append(
            ("run_analysis", file_path)
        ),
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    assert calls == []

def test_selected_file_name_is_displayed(
    monkeypatch,
):
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def mainloop(self):
            pass

    class FakeButton:
        def __init__(
            self,
            root,
            *,
            text,
            command,
        ):
            captured["command"] = command

        def pack(self):
            pass

    class FakeLabel:
        def __init__(
            self,
            root,
            *,
            text,
        ):
            self.text = text

            captured.setdefault(
                "labels",
                [],
            ).append(self)

        def config(
            self,
            *,
            text,
        ):
            self.text = text

        def pack(self):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Button",
        FakeButton,
    )

    monkeypatch.setattr(
        desktop_app,
        "Label",
        FakeLabel,
    )

    monkeypatch.setattr(
        desktop_app,
        "select_mesbg_json_file",
        lambda: r"C:\lists\my_army.json",
    )

    monkeypatch.setattr(
        desktop_app,
        "run_analysis",
        lambda file_path: {},
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    assert any(
        label.text == "Selected: my_army.json"
        for label in captured["labels"]
    )

def test_failed_analysis_displays_error_message(
    monkeypatch,
):
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def mainloop(self):
            pass

    class FakeButton:
        def __init__(
            self,
            root,
            *,
            text,
            command,
        ):
            captured["command"] = command

        def pack(self):
            pass

    class FakeLabel:
        def __init__(
            self,
            root,
            *,
            text,
        ):
            captured.setdefault(
                "labels",
                [],
            ).append(self)
            self.text = text

        def config(
            self,
            *,
            text,
        ):
            self.text = text

        def pack(self):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Button",
        FakeButton,
    )

    monkeypatch.setattr(
        desktop_app,
        "Label",
        FakeLabel,
    )

    monkeypatch.setattr(
        desktop_app,
        "select_mesbg_json_file",
        lambda: "invalid_army.json",
    )

    monkeypatch.setattr(
        desktop_app,
        "run_analysis",
        lambda file_path: None,
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    assert any(
        label.text == "Unable to analyse selected file."
        for label in captured["labels"]
    )

def test_successful_analysis_displays_completion_message(
    monkeypatch,
):
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def mainloop(self):
            pass

    class FakeButton:
        def __init__(
            self,
            root,
            *,
            text,
            command,
        ):
            captured["command"] = command

        def pack(self):
            pass

    class FakeLabel:
        def __init__(
            self,
            root,
            *,
            text,
        ):
            captured.setdefault(
                "labels",
                [],
            ).append(self)
            self.text = text

        def config(
            self,
            *,
            text,
        ):
            self.text = text

        def pack(self):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Button",
        FakeButton,
    )

    monkeypatch.setattr(
        desktop_app,
        "Label",
        FakeLabel,
    )

    monkeypatch.setattr(
        desktop_app,
        "select_mesbg_json_file",
        lambda: "army.json",
    )

    monkeypatch.setattr(
        desktop_app,
        "run_analysis",
        lambda file_path: {
            "analysis": "TEST_RESULT",
        },
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    assert any(
        label.text
        == "Analysis complete."
        for label in captured["labels"]
    )

def test_desktop_app_main_launches_desktop_app(
    monkeypatch,
):
    calls = []

    monkeypatch.setattr(
        desktop_app,
        "launch_desktop_app",
        lambda: calls.append("launch"),
    )

    desktop_app.main()

    assert calls == ["launch"]
