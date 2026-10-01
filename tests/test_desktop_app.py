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

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            calls.append(
                ("button", text)
            )
            self.command = command

        def pack(
            self,
            **kwargs,
        ):
            calls.append(
                ("pack",)
            )


    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
        ):
            self.text = text

        def config(
            self,
            *,
            text,
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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
            **kwargs,
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

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
    )

    monkeypatch.setattr(
        desktop_app,
        "select_mesbg_json_file",
        lambda: r"C:\lists\my_army.json",
    )

    monkeypatch.setattr(
        desktop_app,
        "run_analysis",
        lambda file_path: {
            "army_name": "Test Army",
            "total_points": 700,
            "points_limit": 700,
            "is_legal": True,
            "legality_issues": (),
            "metrics": (),
            "strengths": (),
            "weaknesses": (),
            "scenarios": (),
            "evidence": (),
        },
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

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass
    
    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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
            "army_name": "Test Army",
            "total_points": 700,
            "points_limit": 700,
            "is_legal": True,
            "legality_issues": (),
            "metrics": (),
            "strengths": (),
            "weaknesses": (),
            "scenarios": (),
            "evidence": (),
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

def test_successful_analysis_displays_structured_core_analysis(
    monkeypatch,
):
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def mainloop(self):
            pass

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass
    
    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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
            "army_name": "Army of Lake-town",
            "total_points": 700,
            "points_limit": 700,
            "is_legal": True,
            "legality_issues": (),
            "metrics": (
                {
                    "metric": "Board Presence",
                    "rating": "Strong",
                    "value": 0.68,
                },
                {
                    "metric": "Shooting",
                    "rating": "Exceptional",
                    "value": 0.81,
                },
            ),
            "strengths": (
                {
                    "metric": "Board Presence",
                    "rating": "Strong",
                    "value": 0.68,
                },
            ),
            "weaknesses": (
                {
                    "metric": "Magic",
                    "rating": "Weak",
                    "value": 0.12,
                },
            ),
            "scenarios": (),
            "evidence": (),
        },
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    label_texts = tuple(
        label.text
        for label in captured["labels"]
    )

    assert "Army Summary" in label_texts

    assert any(
        (
            "Army of Lake-town" in text
            and "700 / 700 pts" in text
            and "LEGAL" in text
        )
        for text in label_texts
    )

    assert "Capability Analysis" in label_texts

    assert any(
        (
            "Board Presence" in text
            and "Shooting" in text
        )
        for text in label_texts
    )

    assert "Key Strengths" in label_texts

    assert any(
        "Board Presence" in text
        for text in label_texts
    )

    assert "Key Weaknesses" in label_texts

    assert any(
        "Magic" in text
        for text in label_texts
    )

def test_successful_analysis_displays_scenario_analysis(
    monkeypatch,
):
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def mainloop(self):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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
            "army_name": "Test Army",
            "total_points": 700,
            "points_limit": 700,
            "is_legal": True,
            "legality_issues": (),
            "metrics": (),
            "strengths": (),
            "weaknesses": (),
            "scenarios": (
                {
                    "scenario_id": "HOLD_GROUND",
                    "name": "Hold Ground",
                    "pool": "matched_play",
                    "score": 0.684,
                    "demands": (
                        {
                            "dimension": "Board Control",
                            "capability": 0.72,
                            "intensity": 0.80,
                        },
                    ),
                },
            ),
            "evidence": (),
        },
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    label_texts = tuple(
        label.text
        for label in captured["labels"]
    )

    assert "Scenario Analysis" in label_texts

    assert any(
        "TOP 5 SCENARIOS" in text
        and "BOTTOM 5 SCENARIOS" in text
        and "ALL SCENARIOS" in text
        and "Hold Ground" in text
        and "Matched Play" in text
        and "0.684" in text
        and "Board Control" in text
        for text in label_texts
    )

def test_successful_analysis_displays_evidence_and_confidence(
    monkeypatch,
):
    captured = {}

    class FakeRoot:
        def title(self, value):
            pass

        def geometry(self, value):
            pass

        def minsize(
            self,
            width,
            height,
        ):
            pass

        def mainloop(self):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

    class FakeFrame:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def pack_propagate(
            self,
            flag,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeButton:
        def __init__(
            self,
            master,
            *,
            text,
            command,
            **kwargs,
        ):
            captured["command"] = command

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeLabel:
        def __init__(
            self,
            master,
            *,
            text,
            **kwargs,
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
            **kwargs,
        ):
            self.text = text

        def pack(
            self,
            **kwargs,
        ):
            pass

    class FakeCanvas:
        def __init__(
            self,
            master,
            **kwargs,
        ):
            pass

        def configure(
            self,
            **kwargs,
        ):
            pass

        def create_window(
            self,
            *args,
            **kwargs,
        ):
            return 1

        def itemconfigure(
            self,
            *args,
            **kwargs,
        ):
            pass

        def bbox(
            self,
            value,
        ):
            return (
                0,
                0,
                800,
                1200,
            )

        def bind(
            self,
            event,
            callback,
        ):
            pass

        def yview(
            self,
            *args,
        ):
            pass

        def bind_all(
            self,
            event,
            callback,
        ):
            pass

        def yview_scroll(
            self,
            amount,
            units,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass


    class FakeScrollbar:
        def __init__(
            self,
            master,
            *,
            orient,
            command,
            **kwargs,
        ):
            pass

        def set(
            self,
            *args,
        ):
            pass

        def pack(
            self,
            **kwargs,
        ):
            pass

    monkeypatch.setattr(
        desktop_app,
        "Tk",
        lambda: FakeRoot(),
    )

    monkeypatch.setattr(
        desktop_app,
        "Frame",
        FakeFrame,
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
        "Canvas",
        FakeCanvas,
    )

    monkeypatch.setattr(
        desktop_app,
        "Scrollbar",
        FakeScrollbar,
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
            "army_name": "Test Army",
            "total_points": 700,
            "points_limit": 700,
            "is_legal": True,
            "legality_issues": (),
            "metrics": (),
            "strengths": (),
            "weaknesses": (),
            "scenarios": (),
            "evidence": (
                {
                    "mechanic": "Ranged Wargear Weighting",
                    "status": "PROVISIONAL",
                    "reason": (
                        "Weighting has not been independently validated."
                    ),
                    "provenance": "dev073_calibration",
                },
            ),
        },
    )

    desktop_app.launch_desktop_app()

    captured["command"]()

    label_texts = tuple(
        label.text
        for label in captured["labels"]
    )

    assert "Evidence & Confidence" in label_texts

    assert any(
        (
            "Ranged Wargear Weighting" in text
            and "PROVISIONAL" in text
            and "Weighting has not been independently validated."
            in text
            and "dev073_calibration" in text
        )
        for text in label_texts
    )


def test_build_army_summary_displays_extended_army_details():
    summary = desktop_app.build_army_summary(
        {
            "army_name": "Army of Lake-town",
            "total_points": 240,
            "points_limit": 240,
            "is_legal": True,
            "model_count": 14,
            "might": 5,
            "will": 3,
            "fate": 3,
            "key_models": (
                {
                    "name": "Bard the Bowman",
                    "quantity": 1,
                    "points": 75,
                },
                {
                    "name": "Lake-town Guard",
                    "quantity": 6,
                    "points": 60,
                },
            ),
        }
    )

    assert "Army of Lake-town" in summary
    assert "240 / 240 pts" in summary
    assert "Models: 14" in summary
    assert "Might / Will / Fate: 5 / 3 / 3" in summary
    assert "Key Models" in summary
    assert "Bard the Bowman: 75 pts" in summary
    assert "Lake-town Guard (6): 60 pts" in summary


def test_capability_summary_displays_rating_bars():
    summary = desktop_app.build_capability_analysis_summary(
        {
            "metrics": (
                {
                    "metric": "Offence",
                    "rating": "Strong",
                    "value": 3.18,
                },
                {
                    "metric": "Shooting",
                    "rating": "Very Weak",
                    "value": 0.36,
                },
            )
        }
    )

    assert "Offence" in summary
    assert "████████░░" in summary
    assert "Strong (3.18)" in summary
    assert "Shooting" in summary
    assert "██░░░░░░░░" in summary
    assert "Very Weak (0.36)" in summary

