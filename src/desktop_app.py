from pathlib import Path
from tkinter import (
    BOTH,
    LEFT,
    RIGHT,
    VERTICAL,
    X,
    Y,
    Button,
    Canvas,
    Frame,
    Label,
    Scrollbar,
    Tk,
)

from desktop_analysis_adapter import run_analysis
from file_selection import select_mesbg_json_file


APP_BG = "#f3f5f8"
PANEL_BG = "#ffffff"
SIDEBAR_BG = "#e9eef5"
HEADER_BG = "#eef2f7"
BORDER = "#d4dbe5"
TEXT = "#1f2d3d"
MUTED = "#64748b"
ACCENT = "#2f80ed"
SUCCESS = "#2e8b57"
ERROR = "#b42318"

CAPABILITY_COLOURS = {
    "Exceptional": "#198754",
    "Strong": "#2e8b57",
    "Average": "#b7791f",
    "Weak": "#d97706",
    "Very Weak": "#b42318",
}


def build_army_summary(
    view_model: dict,
) -> str:
    legality = (
        "LEGAL"
        if view_model["is_legal"]
        else "ISSUES FOUND"
    )

    lines = [
        view_model["army_name"],
        "",
        (
            f'{view_model["total_points"]} / '
            f'{view_model["points_limit"]} pts'
        ),
        f"Legality: {legality}",
    ]

    model_count = view_model.get("model_count")
    might = view_model.get("might")
    will = view_model.get("will")
    fate = view_model.get("fate")

    if model_count is not None:
        lines.append(f"Models: {model_count}")

    if (
        might is not None
        and will is not None
        and fate is not None
    ):
        lines.append(
            f"Might / Will / Fate: {might} / {will} / {fate}"
        )

    key_models = view_model.get("key_models", ())

    if key_models:
        lines.extend(
            [
                "",
                "Key Models",
            ]
        )

        for model in key_models:
            quantity = model["quantity"]
            name = model["name"]
            points = model["points"]

            if quantity > 1:
                display_name = f"{name} ({quantity})"
            else:
                display_name = name

            lines.append(
                f"{display_name}: {points} pts"
            )

    return "\n".join(lines)


def _capability_bar(
    rating: str,
) -> str:
    filled_by_rating = {
        "Very Weak": 4,
        "Weak": 8,
        "Average": 12,
        "Strong": 16,
        "Exceptional": 20,
    }

    filled = filled_by_rating.get(
        rating,
        0,
    )

    return (
        "█" * filled
        + "░" * (20 - filled)
    )


def build_capability_analysis_summary(
    view_model: dict,
) -> str:
    lines = []
    metrics = view_model["metrics"]

    if not metrics:
        lines.append(
            "No capability metrics available."
        )
    else:
        for metric in metrics:
            bar = _capability_bar(
                metric["rating"]
            )

            lines.append(
                (
                    f'{metric["metric"]:<14} '
                    f'{bar}  '
                    f'{metric["rating"]} '
                    f'({metric["value"]:.2f})'
                )
            )

    return "\n".join(lines)



def _capability_colour(
    line: str,
) -> str:
    for rating in (
        "Very Weak",
        "Exceptional",
        "Strong",
        "Average",
        "Weak",
    ):
        if f" {rating} " in line:
            return CAPABILITY_COLOURS[rating]

    return TEXT


class CapabilityDisplay:
    """Tkinter display that preserves aligned capability rows with conditional colour."""

    def __init__(
        self,
        parent,
    ) -> None:
        self._frame = Frame(
            parent,
            bg=PANEL_BG,
        )
        self._rows = []

    def pack(
        self,
        *args,
        **kwargs,
    ) -> None:
        self._frame.pack(
            *args,
            **kwargs,
        )

    def config(
        self,
        **kwargs,
    ) -> None:
        if "text" not in kwargs:
            configure = getattr(
                self._frame,
                "configure",
                None,
            )
            if callable(configure):
                configure(**kwargs)
            return

        for row in self._rows:
            destroy = getattr(
                row,
                "destroy",
                None,
            )
            if callable(destroy):
                destroy()

        self._rows = []

        display_text = kwargs["text"]

        if not display_text:
            return

        for line in display_text.splitlines():
            row = Frame(
                self._frame,
                bg=PANEL_BG,
            )
            row.pack(
                anchor="w",
                fill=X,
            )
            self._rows.append(row)

            block_positions = [
                position
                for position in (
                    line.find("█"),
                    line.find("░"),
                )
                if position >= 0
            ]

            if not block_positions:
                Label(
                    row,
                    text=line,
                    bg=PANEL_BG,
                    fg=TEXT,
                    justify=LEFT,
                    anchor="w",
                    font=("Consolas", 10),
                ).pack(
                    side=LEFT,
                    anchor="w",
                )
                continue

            bar_start = min(
                block_positions
            )
            prefix = line[:bar_start]
            capability = line[bar_start:]

            Label(
                row,
                text=prefix,
                bg=PANEL_BG,
                fg=TEXT,
                justify=LEFT,
                anchor="w",
                font=("Consolas", 10),
            ).pack(
                side=LEFT,
                anchor="w",
            )

            Label(
                row,
                text=capability,
                bg=PANEL_BG,
                fg=_capability_colour(
                    line
                ),
                justify=LEFT,
                anchor="w",
                font=("Consolas", 10),
            ).pack(
                side=LEFT,
                anchor="w",
            )

    configure = config


def build_strengths_summary(
    view_model: dict,
) -> str:
    lines = []

    if view_model["strengths"]:
        for strength in view_model["strengths"]:
            lines.append(
                (
                    f'• {strength["metric"]}: '
                    f'{strength["rating"]} '
                    f'({strength["value"]:.2f})'
                )
            )
    else:
        lines.append("• None")

    return "\n".join(lines)


def build_weaknesses_summary(
    view_model: dict,
) -> str:
    lines = []

    if view_model["weaknesses"]:
        for weakness in view_model["weaknesses"]:
            lines.append(
                (
                    f'• {weakness["metric"]}: '
                    f'{weakness["rating"]} '
                    f'({weakness["value"]:.2f})'
                )
            )
    else:
        lines.append("• None")

    return "\n".join(lines)


def _scenario_demands_text(
    scenario: dict,
) -> str:
    if not scenario["demands"]:
        return "None"

    return ", ".join(
        demand["dimension"]
        for demand in scenario["demands"]
    )


def _compact_scenario_demands_text(
    scenario: dict,
) -> str:
    demands = tuple(
        demand["dimension"]
        for demand in scenario["demands"]
    )

    if not demands:
        return "None"

    if len(demands) <= 2:
        return ", ".join(demands)

    return (
        f"{demands[0]}, {demands[1]} "
        f"+{len(demands) - 2}"
    )


def _scenario_table(
    scenarios,
    *,
    include_pool: bool = True,
    compact_demands: bool = False,
) -> list[str]:
    if include_pool:
        lines = [
            (
                f'{"Scenario":<28} '
                f'{"Pool":<22} '
                f'{"Score":>5}  '
                f'Key Demand(s)'
            ),
            "-" * 82,
        ]
    else:
        lines = [
            (
                f'{"Scenario":<28} '
                f'{"Score":>5}  '
                f'Key Demand(s)'
            ),
            "-" * 58,
        ]

    for scenario in scenarios:
        demands_text = (
            _compact_scenario_demands_text(
                scenario
            )
            if compact_demands
            else _scenario_demands_text(
                scenario
            )
        )

        if include_pool:
            pool = (
                scenario["pool"]
                .replace("_", " ")
                .title()
            )

            lines.append(
                (
                    f'{scenario["name"][:28]:<28} '
                    f'{pool[:22]:<22} '
                    f'{scenario["score"]:>5.3f}  '
                    f'{demands_text}'
                )
            )
        else:
            lines.append(
                (
                    f'{scenario["name"][:28]:<28} '
                    f'{scenario["score"]:>5.3f}  '
                    f'{demands_text}'
                )
            )

    return lines


def _side_by_side_scenario_tables(
    left_title: str,
    left_scenarios,
    right_title: str,
    right_scenarios,
) -> list[str]:
    left_lines = [
        left_title,
        "",
        *_scenario_table(
            left_scenarios,
            include_pool=False,
            compact_demands=True,
        ),
    ]

    right_lines = [
        right_title,
        "",
        *_scenario_table(
            right_scenarios,
            include_pool=False,
            compact_demands=True,
        ),
    ]

    left_width = max(
        len(line)
        for line in left_lines
    )

    row_count = max(
        len(left_lines),
        len(right_lines),
    )

    lines = []

    for row_index in range(row_count):
        left_line = (
            left_lines[row_index]
            if row_index < len(left_lines)
            else ""
        )

        right_line = (
            right_lines[row_index]
            if row_index < len(right_lines)
            else ""
        )

        lines.append(
            f"{left_line:<{left_width}}    {right_line}"
        )

    return lines


def build_scenario_analysis_summary(
    view_model: dict,
) -> str:
    scenarios = tuple(
        view_model["scenarios"]
    )

    if not scenarios:
        return "No scenario analysis available."

    highest = tuple(
        sorted(
            scenarios,
            key=lambda scenario: scenario["score"],
            reverse=True,
        )
    )

    lowest = tuple(
        sorted(
            scenarios,
            key=lambda scenario: scenario["score"],
        )
    )

    lines = [
        *_side_by_side_scenario_tables(
            "TOP 5 SCENARIOS",
            highest[:5],
            "BOTTOM 5 SCENARIOS",
            lowest[:5],
        ),
        "",
        "",
        "ALL SCENARIOS",
        "",
        *_scenario_table(highest),
    ]

    return "\n".join(lines)


def build_evidence_summary(
    view_model: dict,
) -> str:
    evidence_records = view_model["evidence"]

    if not evidence_records:
        return "No evidence limitations recorded."

    lines = []

    for evidence in evidence_records:
        lines.append(
            (
                f'{evidence["mechanic"]}: '
                f'{evidence["status"]}'
            )
        )

        lines.append(
            f'    Reason: {evidence["reason"]}'
        )

        lines.append(
            f'    Source: {evidence["provenance"]}'
        )

        lines.append("")

    return "\n".join(lines).rstrip()


def select_and_run_analysis(
    selected_file_label,
    status_label,
    army_summary_label,
    capability_label,
    strengths_label,
    weaknesses_label,
    scenario_label,
    evidence_label,
) -> None:
    file_path = select_mesbg_json_file()

    if file_path is None:
        return

    selected_file_label.config(
        text=f"Selected: {Path(file_path).name}"
    )

    try:
        result = run_analysis(
            file_path,
        )
    except Exception:
        status_label.config(
            text="Unable to analyse selected file.",
            fg=ERROR,
        )
        army_summary_label.config(text="")
        capability_label.config(text="")
        strengths_label.config(text="")
        weaknesses_label.config(text="")
        scenario_label.config(text="")
        evidence_label.config(text="")
        return

    if result is None:
        status_label.config(
            text="Unable to analyse selected file.",
            fg=ERROR,
        )
        army_summary_label.config(text="")
        capability_label.config(text="")
        strengths_label.config(text="")
        weaknesses_label.config(text="")
        scenario_label.config(text="")
        evidence_label.config(text="")
        return

    status_label.config(
        text="Analysis complete.",
        fg=SUCCESS,
    )

    army_summary_label.config(
        text=build_army_summary(
            result,
        )
    )

    capability_label.config(
        text=build_capability_analysis_summary(
            result,
        )
    )

    strengths_label.config(
        text=build_strengths_summary(
            result,
        )
    )

    weaknesses_label.config(
        text=build_weaknesses_summary(
            result,
        )
    )

    scenario_label.config(
        text=build_scenario_analysis_summary(
            result,
        )
    )

    evidence_label.config(
        text=build_evidence_summary(
            result,
        )
    )


def _panel(
    parent,
    padx=12,
    pady=12,
):
    return Frame(
        parent,
        bg=PANEL_BG,
        bd=1,
        relief="solid",
        padx=padx,
        pady=pady,
    )


def _section_title(
    parent,
    text,
):
    label = Label(
        parent,
        text=text,
        bg=PANEL_BG,
        fg=TEXT,
        font=(
            "TkDefaultFont",
            11,
            "bold",
        ),
        anchor="w",
    )
    label.pack(
        fill=X,
    )
    return label


def launch_desktop_app() -> None:
    root = Tk()
    root.title("Project Palantír")
    root.geometry("900x600")
    root.minsize(
        760,
        520,
    )

    try:
        root.state("zoomed")
    except Exception:
        pass
    root.configure(
        bg=APP_BG,
    )

    # ----------------------------------------------------------
    # Fixed left navigation
    # ----------------------------------------------------------

    sidebar = Frame(
        root,
        bg=SIDEBAR_BG,
        width=150,
        padx=12,
        pady=14,
    )
    sidebar.pack(
        side=LEFT,
        fill=Y,
    )
    sidebar.pack_propagate(False)

    Label(
        sidebar,
        text="Project Palantír",
        bg=SIDEBAR_BG,
        fg=TEXT,
        font=(
            "TkDefaultFont",
            11,
            "bold",
        ),
        anchor="w",
    ).pack(
        fill=X,
        pady=(0, 2),
    )

    Label(
        sidebar,
        text="MESBG Army Analysis",
        bg=SIDEBAR_BG,
        fg=MUTED,
        anchor="w",
    ).pack(
        fill=X,
        pady=(0, 18),
    )

    Label(
        sidebar,
        text="▣  Analyse Army",
        bg="#dbe9fb",
        fg=TEXT,
        anchor="w",
        padx=8,
        pady=8,
    ).pack(
        fill=X,
        pady=(0, 6),
    )

    Label(
        sidebar,
        text="◷  Recent Files",
        bg=SIDEBAR_BG,
        fg=MUTED,
        anchor="w",
        padx=8,
        pady=8,
    ).pack(
        fill=X,
    )

    Label(
        sidebar,
        text="?  Help",
        bg=SIDEBAR_BG,
        fg=MUTED,
        anchor="w",
        padx=8,
        pady=8,
    ).pack(
        fill=X,
    )

    Label(
        sidebar,
        text="v0.8.0-dev",
        bg=SIDEBAR_BG,
        fg=MUTED,
        anchor="w",
    ).pack(
        side="bottom",
        fill=X,
    )

    # ----------------------------------------------------------
    # Main application area
    # ----------------------------------------------------------

    main_area = Frame(
        root,
        bg=APP_BG,
    )
    main_area.pack(
        side=LEFT,
        fill=BOTH,
        expand=True,
    )

    header_frame = Frame(
        main_area,
        bg=HEADER_BG,
        padx=14,
        pady=10,
    )
    header_frame.pack(
        fill=X,
    )

    Label(
        header_frame,
        text="Analyse Army",
        bg=HEADER_BG,
        fg=TEXT,
        font=(
            "TkDefaultFont",
            12,
            "bold",
        ),
        anchor="w",
    ).pack(
        side=LEFT,
    )

    status_label = Label(
        header_frame,
        text="Ready",
        bg=HEADER_BG,
        fg=MUTED,
        anchor="e",
    )
    status_label.pack(
        side=RIGHT,
    )

    load_frame = Frame(
        main_area,
        bg=APP_BG,
        padx=14,
        pady=10,
    )
    load_frame.pack(
        fill=X,
    )

    Label(
        load_frame,
        text="1. Load Army List",
        bg=APP_BG,
        fg=TEXT,
        font=(
            "TkDefaultFont",
            11,
            "bold",
        ),
        anchor="w",
    ).pack(
        fill=X,
        pady=(0, 6),
    )

    file_row = Frame(
        load_frame,
        bg=APP_BG,
    )
    file_row.pack(
        fill=X,
    )

    selected_file_label = Label(
        file_row,
        text="No file selected",
        bg=PANEL_BG,
        fg=MUTED,
        bd=1,
        relief="solid",
        padx=10,
        pady=7,
        anchor="w",
    )
    selected_file_label.pack(
        side=LEFT,
        fill=X,
        expand=True,
        padx=(0, 8),
    )

    # ----------------------------------------------------------
    # Scrollable dashboard
    # ----------------------------------------------------------

    scroll_container = Frame(
        main_area,
        bg=APP_BG,
    )
    scroll_container.pack(
        fill=BOTH,
        expand=True,
    )

    canvas = Canvas(
        scroll_container,
        bg=APP_BG,
        highlightthickness=0,
    )

    scrollbar = Scrollbar(
        scroll_container,
        orient=VERTICAL,
        command=canvas.yview,
    )

    canvas.configure(
        yscrollcommand=scrollbar.set,
    )

    scrollbar.pack(
        side=RIGHT,
        fill="y",
    )

    canvas.pack(
        side=LEFT,
        fill=BOTH,
        expand=True,
    )

    content_frame = Frame(
        canvas,
        bg=APP_BG,
        padx=14,
        pady=4,
    )

    content_window = canvas.create_window(
        (0, 0),
        window=content_frame,
        anchor="nw",
    )

    def update_scroll_region(
        event,
    ):
        canvas.configure(
            scrollregion=canvas.bbox(
                "all"
            )
        )

    def resize_content_width(
        event,
    ):
        canvas.itemconfigure(
            content_window,
            width=event.width,
        )

    content_frame.bind(
        "<Configure>",
        update_scroll_region,
    )

    canvas.bind(
        "<Configure>",
        resize_content_width,
    )

    def scroll_with_mousewheel(
        event,
    ):
        canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units",
        )

    canvas.bind_all(
        "<MouseWheel>",
        scroll_with_mousewheel,
    )

    # ----------------------------------------------------------
    # Dashboard top row
    # ----------------------------------------------------------

    dashboard_row = Frame(
        content_frame,
        bg=APP_BG,
    )
    dashboard_row.pack(
        fill=X,
    )

    army_panel = _panel(
        dashboard_row,
    )
    army_panel.pack(
        side=LEFT,
        fill=BOTH,
        expand=True,
        padx=(0, 5),
    )

    capability_panel = _panel(
        dashboard_row,
    )
    capability_panel.pack(
        side=LEFT,
        fill=BOTH,
        expand=True,
        padx=5,
    )

    insights_column = Frame(
        dashboard_row,
        bg=APP_BG,
    )
    insights_column.pack(
        side=LEFT,
        fill=BOTH,
        expand=True,
        padx=(5, 0),
    )

    _section_title(
        army_panel,
        "Army Summary",
    )

    army_summary_label = Label(
        army_panel,
        text="",
        bg=PANEL_BG,
        fg=TEXT,
        justify=LEFT,
        anchor="nw",
    )
    army_summary_label.pack(
        fill=X,
        pady=(10, 0),
    )

    _section_title(
        capability_panel,
        "Capability Analysis",
    )

    capability_label = CapabilityDisplay(
        capability_panel,
    )
    capability_label.pack(
        fill=BOTH,
        expand=True,
        pady=(10, 0),
    )

    strengths_panel = _panel(
        insights_column,
        padx=10,
        pady=10,
    )
    strengths_panel.pack(
        fill=X,
        pady=(0, 6),
    )

    _section_title(
        strengths_panel,
        "Key Strengths",
    )

    strengths_label = Label(
        strengths_panel,
        text="",
        bg=PANEL_BG,
        fg=TEXT,
        justify=LEFT,
        anchor="nw",
        wraplength=220,
    )
    strengths_label.pack(
        fill=X,
        pady=(8, 0),
    )

    weaknesses_panel = _panel(
        insights_column,
        padx=10,
        pady=10,
    )
    weaknesses_panel.pack(
        fill=X,
    )

    _section_title(
        weaknesses_panel,
        "Key Weaknesses",
    )

    weaknesses_label = Label(
        weaknesses_panel,
        text="",
        bg=PANEL_BG,
        fg=TEXT,
        justify=LEFT,
        anchor="nw",
        wraplength=220,
    )
    weaknesses_label.pack(
        fill=X,
        pady=(8, 0),
    )

    # ----------------------------------------------------------
    # Scenario analysis
    # ----------------------------------------------------------

    scenario_panel = _panel(
        content_frame,
    )
    scenario_panel.pack(
        fill=X,
        pady=(10, 0),
    )

    _section_title(
        scenario_panel,
        "Scenario Analysis",
    )

    scenario_label = Label(
        scenario_panel,
        text="",
        bg=PANEL_BG,
        fg=TEXT,
        justify=LEFT,
        anchor="nw",
        font=("Consolas", 9),
    )
    scenario_label.pack(
        fill=X,
        pady=(10, 0),
    )

    # ----------------------------------------------------------
    # Evidence & confidence
    # ----------------------------------------------------------

    evidence_panel = _panel(
        content_frame,
    )
    evidence_panel.pack(
        fill=X,
        pady=(10, 12),
    )

    _section_title(
        evidence_panel,
        "Evidence & Confidence",
    )

    evidence_label = Label(
        evidence_panel,
        text="",
        bg=PANEL_BG,
        fg=TEXT,
        justify=LEFT,
        anchor="nw",
        wraplength=760,
    )
    evidence_label.pack(
        fill=X,
        pady=(10, 0),
    )

    select_button = Button(
        file_row,
        text="Load and Analyse",
        bg=ACCENT,
        fg="white",
        activebackground=ACCENT,
        activeforeground="white",
        padx=12,
        pady=6,
        command=lambda: select_and_run_analysis(
            selected_file_label,
            status_label,
            army_summary_label,
            capability_label,
            strengths_label,
            weaknesses_label,
            scenario_label,
            evidence_label,
        ),
    )
    select_button.pack(
        side=RIGHT,
    )

    root.mainloop()


def main() -> None:
    launch_desktop_app()


if __name__ == "__main__":
    main()
