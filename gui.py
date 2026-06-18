from __future__ import annotations

import os
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog

import flet as ft

from file_manager import core


OPERATIONS = {
    "copy": "Копировать файл",
    "delete": "Удалить файл или папку",
    "count": "Подсчитать файлы в папке",
    "find": "Найти файлы по regex",
    "add-date": "Добавить дату создания в имя",
    "analyse": "Анализ размеров папки",
}


def pick_file_native() -> str:
    if platform.system() == "Darwin":
        script = 'POSIX path of (choose file with prompt "Выберите файл")'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return ""

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename()
    root.destroy()
    return path


def pick_directory_native() -> str:
    if platform.system() == "Darwin":
        script = 'POSIX path of (choose folder with prompt "Выберите папку")'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return ""

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askdirectory()
    root.destroy()
    return path


class FileManagerUI:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.page.title = "File Manager GUI"
        self.page.window_width = 980
        self.page.window_height = 760
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.snack_bar = ft.SnackBar(content=ft.Text(""))

        self.operation = ft.Dropdown(
            label="Инструмент",
            width=340,
            value="copy",
            tooltip="Выберите, какую операцию нужно выполнить",
            options=[
                ft.dropdown.Option(key=key, text=f"{key} — {title}")
                for key, title in OPERATIONS.items()
            ],
            on_change=self.on_operation_change,
        )

        self.path_field = ft.TextField(
            label="Путь к файлу или папке",
            hint_text="Выберите путь через кнопки справа",
            expand=True,
            tooltip="Основной путь для выбранной операции",
        )

        self.pattern_field = ft.TextField(
            label="Регулярное выражение",
            hint_text=r"Например: \.txt$",
            visible=False,
            tooltip="Используется только для команды find",
        )

        self.recursive_checkbox = ft.Checkbox(
            label="Рекурсивно обработать вложенные файлы",
            value=False,
            visible=False,
            tooltip="Используется только для команды add-date, если выбрана папка",
        )

        self.result_text = ft.Text(
            "Здесь появится результат выполнения команды.",
            selectable=True,
            size=15,
        )

        self.pick_file_button = ft.ElevatedButton(
            text="Выбрать файл",
            icon=ft.Icons.UPLOAD_FILE,
            tooltip="Открыть окно выбора файла",
            on_click=self.pick_file,
        )

        self.pick_dir_button = ft.ElevatedButton(
            text="Выбрать папку",
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Открыть окно выбора папки",
            on_click=self.pick_directory,
        )

        self.path_row = ft.Row(
            controls=[
                self.path_field,
                self.pick_file_button,
                self.pick_dir_button,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def show_message(self, text: str, error: bool = False) -> None:
        self.page.snack_bar.content = ft.Text(text)
        self.page.snack_bar.bgcolor = ft.Colors.RED_400 if error else ft.Colors.GREEN_400
        self.page.snack_bar.open = True
        self.page.update()

    def pick_file(self, _event: ft.ControlEvent) -> None:
        try:
            path = pick_file_native()
            if path:
                self.path_field.value = path
                self.page.update()
        except Exception as error:
            self.show_message(f"Не удалось выбрать файл: {error}", error=True)

    def pick_directory(self, _event: ft.ControlEvent) -> None:
        try:
            path = pick_directory_native()
            if path:
                self.path_field.value = path
                self.page.update()
        except Exception as error:
            self.show_message(f"Не удалось выбрать папку: {error}", error=True)

    def on_operation_change(self, _event: ft.ControlEvent | None) -> None:
        command = self.operation.value
        self.pattern_field.visible = command == "find"
        self.recursive_checkbox.visible = command == "add-date"

        if command == "copy":
            self.path_field.label = "Путь к файлу"
            self.path_field.hint_text = "Для copy нужно выбрать файл"
        elif command in {"count", "find", "analyse"}:
            self.path_field.label = "Путь к папке"
            self.path_field.hint_text = "Для этой команды нужно выбрать папку"
        else:
            self.path_field.label = "Путь к файлу или папке"
            self.path_field.hint_text = "Выберите путь через кнопки справа"

        self.page.update()

    @staticmethod
    def format_result(command: str, result: object) -> str:
        if command == "copy":
            return f"Файл успешно скопирован:\n{result}"
        if command == "delete":
            return "Удаление выполнено успешно"
        if command == "count":
            return f"Всего файлов: {result}"
        if command == "find":
            matches = list(result)
            return "Найденные файлы:\n" + "\n".join(matches) if matches else "Подходящих файлов не найдено"
        if command == "add-date":
            renamed = list(result)
            return "Переименованные файлы:\n" + "\n".join(renamed) if renamed else "Файлы для переименования не найдены"
        if command == "analyse":
            total, summary = result
            lines = [f"Общий размер: {total} байт", "", "Содержимое:"]
            for name, size in summary.items():
                lines.append(f"- {name}: {size} байт")
            return "\n".join(lines)
        return str(result)

    def validate_path(self, command: str, path: str) -> None:
        if command == "copy":
            if not os.path.isfile(path):
                raise ValueError("Для команды copy нужно выбрать существующий файл")
        elif command in {"count", "find", "analyse"}:
            if not os.path.isdir(path):
                raise ValueError(f"Для команды {command} нужно выбрать существующую папку")
        elif command in {"delete", "add-date"}:
            if not os.path.exists(path):
                raise ValueError("Указанный путь не существует")

    def run_command(self, _event: ft.ControlEvent) -> None:
        command = self.operation.value
        path = self.path_field.value.strip()
        pattern = self.pattern_field.value.strip()
        recursive = bool(self.recursive_checkbox.value)

        try:
            if not command:
                raise ValueError("Сначала выберите инструмент")
            if not path:
                raise ValueError("Укажите путь к файлу или папке")

            self.validate_path(command, path)

            if command == "copy":
                result = core.copy_file(path)
            elif command == "delete":
                result = core.delete_path(path)
            elif command == "count":
                result = core.count_files(path)
            elif command == "find":
                if not pattern:
                    raise ValueError("Для поиска нужно указать регулярное выражение")
                result = core.find_files(path, pattern)
            elif command == "add-date":
                result = core.add_creation_date(path, recursive)
            elif command == "analyse":
                result = core.analyse(path)
            else:
                raise ValueError("Неизвестная команда")

            self.result_text.value = self.format_result(command, result)
            self.show_message("Операция выполнена успешно")

        except Exception as error:
            self.result_text.value = f"Ошибка: {error}"
            self.show_message(f"Ошибка: {error}", error=True)

        self.page.update()

    def clear_fields(self, _event: ft.ControlEvent) -> None:
        self.path_field.value = ""
        self.pattern_field.value = ""
        self.recursive_checkbox.value = False
        self.result_text.value = "Здесь появится результат выполнения команды."
        self.page.update()

    def build(self) -> None:
        self.on_operation_change(None)

        self.page.add(
            ft.Text("Файловый менеджер", size=28, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Графический интерфейс для функций из первого проекта. "
                "Выберите команду, затем путь и при необходимости дополнительные параметры.",
                size=14,
            ),
            ft.Divider(),
            ft.ResponsiveRow(
                [
                    ft.Container(self.operation, col={"xs": 12, "md": 6}),
                    ft.Container(self.pattern_field, col={"xs": 12, "md": 6}),
                ]
            ),
            self.path_row,
            self.recursive_checkbox,
            ft.Row(
                [
                    ft.ElevatedButton(
                        text="Запустить",
                        icon=ft.Icons.PLAY_ARROW,
                        on_click=self.run_command,
                    ),
                    ft.OutlinedButton(
                        text="Очистить",
                        icon=ft.Icons.CLEAR,
                        on_click=self.clear_fields,
                    ),
                ]
            ),
            ft.Divider(),
            ft.Text("Результат", size=20, weight=ft.FontWeight.W_600),
            ft.Container(
                content=self.result_text,
                border=ft.border.all(1, ft.Colors.BLACK26),
                border_radius=12,
                padding=16,
                width=900,
            ),
        )


def main(page: ft.Page) -> None:
    app = FileManagerUI(page)
    app.build()


def run_gui() -> None:
    ft.app(target=main)


if __name__ == "__main__":
    run_gui()