"""XR6 Toolkit - aplikasi Android (Flet) yang menggabungkan
xr6-filter-wall dan xr6-pro. Logik teras kekal dalam pakej PyPI;
fail ini hanyalah lapisan UI yang nipis."""

import flet as ft

from xr6_filter_wall import (
    FilterWall,
    SecurityViolationError,
    compute_sha256,
    verify_sha256,
)
from xr6_pro import calculate_energy_efficiency

OK = ft.Colors.GREEN_700
BAD = ft.Colors.RED_700


def main(page: ft.Page):
    page.title = "XR6 Toolkit"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.padding = 16

    def result_box() -> ft.Text:
        return ft.Text("", selectable=True, size=15)

    def show(box: ft.Text, message: str, color=None):
        box.value = message
        box.color = color
        box.update()

    # ---------- Skrin 1: SHA-256 ----------
    hash_input = ft.TextField(label="Teks", multiline=True, min_lines=3, max_lines=6)
    expected_input = ft.TextField(label="SHA-256 dijangka (untuk semakan)")
    hash_out = result_box()

    def do_hash(_):
        show(hash_out, compute_sha256(hash_input.value or ""))

    def do_verify(_):
        if not expected_input.value:
            show(hash_out, "Sila isi SHA-256 dijangka.", BAD)
            return
        if verify_sha256(hash_input.value or "", expected_input.value):
            show(hash_out, "Sah: integriti dipadankan.", OK)
        else:
            show(hash_out, "Tidak sepadan: data mungkin telah diubah.", BAD)

    hash_view = ft.Column(
        [
            ft.Text("Integriti SHA-256", size=20, weight=ft.FontWeight.BOLD),
            hash_input,
            ft.Row(
                [
                    ft.FilledButton("Kira hash", on_click=do_hash),
                    ft.OutlinedButton("Semak", on_click=do_verify),
                ]
            ),
            expected_input,
            hash_out,
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
    )

    # ---------- Skrin 2: Filter Wall ----------
    fw_input = ft.TextField(label="Input untuk diperiksa", multiline=True, min_lines=3, max_lines=6)
    strict_switch = ft.Switch(label="Mod ketat (tolak corak berbahaya)", value=True)
    fw_out = result_box()

    def do_inspect(_):
        wall = FilterWall(strict=bool(strict_switch.value))
        try:
            cleaned = wall.inspect_text(fw_input.value or "")
            show(fw_out, f"Lulus:\n{cleaned}", OK)
        except SecurityViolationError as err:
            show(fw_out, f"Disekat: {err}", BAD)

    fw_view = ft.Column(
        [
            ft.Text("Filter Wall", size=20, weight=ft.FontWeight.BOLD),
            fw_input,
            strict_switch,
            ft.FilledButton("Periksa", on_click=do_inspect),
            fw_out,
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
    )

    # ---------- Skrin 3: Kecekapan tenaga ----------
    base_input = ft.TextField(label="Watt asas (baseline)", keyboard_type=ft.KeyboardType.NUMBER)
    opt_input = ft.TextField(label="Watt dioptimumkan", keyboard_type=ft.KeyboardType.NUMBER)
    en_out = result_box()

    def do_energy(_):
        try:
            res = calculate_energy_efficiency(
                float(base_input.value), float(opt_input.value)
            )
        except (TypeError, ValueError) as err:
            show(en_out, f"Input tidak sah: {err}", BAD)
            return
        show(
            en_out,
            f"Pengurangan kuasa: {res['power_reduction_percentage']}%\nStatus: {res['status']}",
            OK if res["status"] == "Optimal" else BAD,
        )

    energy_view = ft.Column(
        [
            ft.Text("Kecekapan Tenaga", size=20, weight=ft.FontWeight.BOLD),
            base_input,
            opt_input,
            ft.FilledButton("Kira", on_click=do_energy),
            en_out,
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
    )

    # ---------- Navigasi ----------
    views = [hash_view, fw_view, energy_view]
    body = ft.Container(content=views[0], expand=True)

    def on_nav(e):
        body.content = views[int(e.control.selected_index)]
        body.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.TAG, label="Hash"),
            ft.NavigationBarDestination(icon=ft.Icons.SHIELD, label="Firewall"),
            ft.NavigationBarDestination(icon=ft.Icons.BOLT, label="Tenaga"),
        ],
        on_change=on_nav,
    )
    page.add(ft.SafeArea(content=body, expand=True))


ft.run(main)
