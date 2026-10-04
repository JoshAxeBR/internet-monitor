import time
import tkinter as tk
from collections import deque
from tkinter import ttk

import psutil


class InternetMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Internet Monitor")
        self.geometry("980x620")
        self.minsize(900, 560)
        self.configure(bg="#0f172a")

        self.interface_names = self._get_interfaces()
        self.selected_interface = self.interface_names[0] if self.interface_names else ""

        self.download_history = deque(maxlen=90)
        self.upload_history = deque(maxlen=90)
        self.last_snapshot = None
        self.total_download = 0
        self.total_upload = 0

        self._build_ui()
        self._register_initial_values()
        self.after(1000, self.update_loop)

    def _get_interfaces(self):
        try:
            counters = psutil.net_io_counters(pernic=True)
            return list(counters.keys())
        except Exception:
            return ["eth0"]

    def _build_ui(self):
        self.main_frame = tk.Frame(self, bg="#0f172a", padx=24, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(self.main_frame, bg="#0f172a")
        header.pack(fill=tk.X, pady=(0, 18))

        title = tk.Label(
            header,
            text="Monitor de Consumo de Internet",
            font=("Segoe UI", 22, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Acompanhamento em tempo real da rede",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0f172a",
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        controls = tk.Frame(self.main_frame, bg="#0f172a")
        controls.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            controls,
            text="Interface:",
            font=("Segoe UI", 11, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        ).pack(side=tk.LEFT)

        self.interface_combo = ttk.Combobox(
            controls,
            values=self.interface_names,
            width=18,
            state="readonly",
        )
        self.interface_combo.pack(side=tk.LEFT, padx=(10, 0))
        if self.interface_names:
            self.interface_combo.set(self.selected_interface)
        self.interface_combo.bind("<<ComboboxSelected>>", self.on_interface_change)

        cards = tk.Frame(self.main_frame, bg="#0f172a")
        cards.pack(fill=tk.X, pady=(0, 18))

        self.cards = []
        card_specs = [
            ("Download", "0 KB/s", "#22c55e", "#14532d"),
            ("Upload", "0 KB/s", "#3b82f6", "#1e3a8a"),
            ("Total baixado", "0 MB", "#f59e0b", "#78350f"),
            ("Total enviado", "0 MB", "#ef4444", "#7f1d1d"),
        ]

        for title_text, initial_value, accent, accent_dark in card_specs:
            card = tk.Frame(cards, bg=accent_dark, bd=0, padx=18, pady=18)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
            card.configure(highlightbackground=accent, highlightthickness=1)

            tk.Label(
                card,
                text=title_text,
                font=("Segoe UI", 10, "bold"),
                fg="#e2e8f0",
                bg=accent_dark,
            ).pack(anchor="w")

            value_label = tk.Label(
                card,
                text=initial_value,
                font=("Segoe UI", 24, "bold"),
                fg="#f8fafc",
                bg=accent_dark,
            )
            value_label.pack(anchor="w", pady=(10, 0))
            self.cards.append(value_label)

        chart_wrapper = tk.Frame(self.main_frame, bg="#111827", bd=1, relief=tk.SOLID)
        chart_wrapper.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            chart_wrapper,
            text="Uso de rede (últimos 90 segundos)",
            font=("Segoe UI", 11, "bold"),
            fg="#e2e8f0",
            bg="#111827",
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(12, 0))

        self.chart = tk.Canvas(
            chart_wrapper,
            width=900,
            height=300,
            bg="#0b1120",
            highlightthickness=0,
        )
        self.chart.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.draw_chart()

    def _register_initial_values(self):
        self.last_snapshot = self._read_snapshot()

    def _read_snapshot(self):
        try:
            counters = psutil.net_io_counters(pernic=True)
            if self.selected_interface not in counters:
                return None

            current = counters[self.selected_interface]
            return {
                "time": time.time(),
                "bytes_recv": current.bytes_recv,
                "bytes_sent": current.bytes_sent,
            }
        except Exception:
            return None

    def on_interface_change(self, event):
        self.selected_interface = self.interface_combo.get()
        self.last_snapshot = self._read_snapshot()
        self.download_history.clear()
        self.upload_history.clear()
        self.total_download = 0
        self.total_upload = 0
        self.update_labels()

    def _format_bytes(self, value_bytes):
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(value_bytes)
        unit_index = 0
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        return f"{size:.2f} {units[unit_index]}"

    def _format_speed(self, value_bytes_per_sec):
        if value_bytes_per_sec < 1024:
            return f"{value_bytes_per_sec:.0f} B/s"
        if value_bytes_per_sec < 1024 * 1024:
            return f"{value_bytes_per_sec / 1024:.2f} KB/s"
        return f"{value_bytes_per_sec / (1024 * 1024):.2f} MB/s"

    def update_labels(self):
        download_speed = 0
        upload_speed = 0
        if self.download_history:
            download_speed = max(self.download_history, default=0)
        if self.upload_history:
            upload_speed = max(self.upload_history, default=0)

        self.cards[0].configure(text=self._format_speed(download_speed))
        self.cards[1].configure(text=self._format_speed(upload_speed))
        self.cards[2].configure(text=self._format_bytes(self.total_download))
        self.cards[3].configure(text=self._format_bytes(self.total_upload))

    def update_loop(self):
        snapshot = self._read_snapshot()
        if snapshot and self.last_snapshot:
            dt = max(snapshot["time"] - self.last_snapshot["time"], 0.1)
            download_delta = max(snapshot["bytes_recv"] - self.last_snapshot["bytes_recv"], 0)
            upload_delta = max(snapshot["bytes_sent"] - self.last_snapshot["bytes_sent"], 0)

            download_speed = download_delta / dt
            upload_speed = upload_delta / dt

            self.download_history.append(download_speed)
            self.upload_history.append(upload_speed)
            self.total_download += download_delta
            self.total_upload += upload_delta

        self.last_snapshot = snapshot
        self.update_labels()
        self.draw_chart()
        self.after(1000, self.update_loop)

    def draw_chart(self):
        self.chart.delete("all")
        width = 900
        height = 300
        padding_left = 48
        padding_right = 18
        padding_top = 18
        padding_bottom = 32

        plot_width = width - padding_left - padding_right
        plot_height = height - padding_top - padding_bottom

        # background grid
        for i in range(5):
            y = padding_top + (plot_height / 4) * i
            self.chart.create_line(padding_left, y, width - padding_right, y, fill="#1e293b")

        self.chart.create_line(padding_left, padding_top, padding_left, height - padding_bottom, fill="#334155")
        self.chart.create_line(padding_left, height - padding_bottom, width - padding_right, height - padding_bottom, fill="#334155")

        history_download = list(self.download_history)
        history_upload = list(self.upload_history)
        max_value = max(
            max(history_download, default=0),
            max(history_upload, default=0),
            1048576,
        )

        if len(history_download) > 1:
            points_download = []
            for idx, value in enumerate(history_download):
                x = padding_left + (idx / max(len(history_download) - 1, 1)) * plot_width
                y = height - padding_bottom - (value / max_value) * plot_height
                points_download.append((x, y))
            self._draw_line(points_download, "#22c55e")

        if len(history_upload) > 1:
            points_upload = []
            for idx, value in enumerate(history_upload):
                x = padding_left + (idx / max(len(history_upload) - 1, 1)) * plot_width
                y = height - padding_bottom - (value / max_value) * plot_height
                points_upload.append((x, y))
            self._draw_line(points_upload, "#3b82f6")

        # axis labels
        self.chart.create_text(width / 2, height - 8, text="tempo (segundos)", fill="#94a3b8", font=("Segoe UI", 9))
        self.chart.create_text(12, height / 2, text="KB/s", fill="#94a3b8", font=("Segoe UI", 9), anchor="center")

    def _draw_line(self, points, color):
        if len(points) < 2:
            return
        for idx in range(len(points) - 1):
            x1, y1 = points[idx]
            x2, y2 = points[idx + 1]
            self.chart.create_line(x1, y1, x2, y2, fill=color, width=2)


if __name__ == "__main__":
    app = InternetMonitorApp()
    app.mainloop()
