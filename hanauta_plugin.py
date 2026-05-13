#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

PLUGIN_ROOT = Path(__file__).resolve().parent
SERVICE_KEY = "wallpaper_manager"
WALLPAPER_APP = PLUGIN_ROOT / "wallpaper_manager.py"


def _open_wallpaper_manager(window, api: dict[str, object]) -> None:
    status = getattr(window, "wallpaper_plugin_status", None)
    if not WALLPAPER_APP.exists():
        if isinstance(status, QLabel):
            status.setText("wallpaper_manager.py not found in plugin folder.")
        return

    entry_command = api.get("entry_command")
    run_bg = api.get("run_bg")
    command: list[str] = []
    if callable(entry_command):
        try:
            command = list(entry_command(WALLPAPER_APP))
        except Exception:
            command = []
    if not command:
        command = ["python3", str(WALLPAPER_APP)]

    if callable(run_bg):
        try:
            run_bg(command)
        except Exception:
            pass

    if isinstance(status, QLabel):
        status.setText("Wallpaper manager opened.")


def build_wallpaper_service_section(window, api: dict[str, object]) -> QWidget:
    SettingsRow = api["SettingsRow"]
    SwitchButton = api["SwitchButton"]
    ExpandableServiceSection = api["ExpandableServiceSection"]
    material_icon = api["material_icon"]
    icon_path = str(api.get("plugin_icon_path", "")).strip()

    service = window.settings_state.setdefault("services", {}).setdefault(
        SERVICE_KEY,
        {
            "enabled": True,
            "show_in_notification_center": True,
            "show_in_bar": False,
        },
    )

    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)

    display_switch = SwitchButton(bool(service.get("show_in_notification_center", True)))
    display_switch.toggledValue.connect(
        lambda enabled: window._set_service_notification_visibility(SERVICE_KEY, enabled)
    )
    window.service_display_switches[SERVICE_KEY] = display_switch
    layout.addWidget(
        SettingsRow(
            material_icon("widgets"),
            "Show in notification center",
            "Display wallpaper manager controls in notification center.",
            window.icon_font,
            window.ui_font,
            display_switch,
        )
    )

    open_button = QPushButton("Open Wallpaper Manager")
    open_button.setObjectName("primaryButton")
    open_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    open_button.clicked.connect(lambda: _open_wallpaper_manager(window, api))
    layout.addWidget(
        SettingsRow(
            material_icon("wallpaper"),
            "Open wallpaper manager",
            "Launch the standalone wallpaper manager UI.",
            window.icon_font,
            window.ui_font,
            open_button,
        )
    )

    status_label = QLabel("Wallpaper manager plugin ready.")
    status_label.setWordWrap(True)
    status_label.setStyleSheet("color: rgba(246,235,247,0.72);")
    layout.addWidget(status_label)
    window.wallpaper_plugin_status = status_label

    section = ExpandableServiceSection(
        SERVICE_KEY,
        "Wallpaper Manager",
        "Browse, preview, and apply wallpapers from local packs or online sources.",
        "?",
        window.icon_font,
        window.ui_font,
        content,
        window._service_enabled(SERVICE_KEY),
        lambda enabled: window._set_service_enabled(SERVICE_KEY, enabled),
        icon_path=icon_path,
    )
    window.service_sections[SERVICE_KEY] = section
    return section


def register_hanauta_plugin() -> dict[str, object]:
    return {
        "id": SERVICE_KEY,
        "name": "Wallpaper Manager",
        "api_min_version": 1,
        "service_sections": [
            {
                "key": SERVICE_KEY,
                "builder": build_wallpaper_service_section,
                "supports_show_on_bar": False,
            }
        ],
    }

