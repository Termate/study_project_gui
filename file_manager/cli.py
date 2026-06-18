import argparse
import sys

# Позволяет запускать как пакет (python -m / через main.py),
# так и напрямую (python file_manager/cli.py)
try:
    from . import core
except ImportError:  # pragma: no cover
    import core


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Менеджер файловой системы (CLI)"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Доступные команды",
    )

    # COPY
    copy_parser = subparsers.add_parser("copy", help="Копировать файл")
    copy_parser.add_argument("path", help="Путь к файлу")

    # DELETE
    delete_parser = subparsers.add_parser("delete", help="Удалить файл или папку")
    delete_parser.add_argument("path", help="Путь к файлу или папке")

    # COUNT
    count_parser = subparsers.add_parser("count", help="Подсчитать количество файлов в папке")
    count_parser.add_argument("directory", help="Путь к папке")

    # FIND
    find_parser = subparsers.add_parser("find", help="Найти файлы по регулярному выражению")
    find_parser.add_argument("directory", help="Путь к папке")
    find_parser.add_argument("pattern", help="Регулярное выражение")

    # ADD DATE
    date_parser = subparsers.add_parser("add-date", help="Добавить дату создания в имя файла")
    date_parser.add_argument("path", help="Путь к файлу или папке")
    date_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Применить ко всем вложенным файлам",
    )

    # ANALYSE
    analyse_parser = subparsers.add_parser("analyse", help="Проанализировать размеры в папке")
    analyse_parser.add_argument("directory", help="Путь к папке")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "copy":
            result = core.copy_file(args.path)
            print(f"Файл успешно скопирован: {result}")

        elif args.command == "delete":
            core.delete_path(args.path)
            print("Удаление выполнено успешно")

        elif args.command == "count":
            total = core.count_files(args.directory)
            print(f"Всего файлов: {total}")

        elif args.command == "find":
            matches = core.find_files(args.directory, args.pattern)
            if matches:
                print("Найденные файлы:")
                for match in matches:
                    print(match)
            else:
                print("Подходящих файлов не найдено")

        elif args.command == "add-date":
            renamed = core.add_creation_date(args.path, args.recursive)
            if renamed:
                print("Переименованные файлы:")
                for p in renamed:
                    print(p)
            else:
                print("Файлы для переименования не найдены")

        elif args.command == "analyse":
            total, summary = core.analyse(args.directory)
            print(f"Общий размер: {total} байт")
            print("Содержимое:")
            for name, size in summary.items():
                print(f"- {name}: {size} байт")

        return 0

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
