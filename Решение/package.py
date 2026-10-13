"""Build the testing report, validate deliverables and create the submission ZIP."""

import hashlib
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import unquote


def main() -> None:
    """Build the report from original responses and package verified files."""
    root = Path(__file__).resolve().parent
    hw2 = root / "ДЗ2"
    experiments = hw2 / "experiments"
    before = (experiments / "before_response.md").read_text(encoding="utf-8-sig")
    after = (experiments / "after_response.md").read_text(encoding="utf-8-sig")
    report = '''---
assignment: ДЗ2
project: FoodTech
experiment: sequential_before_after
date: 2026-10-12
---

# Проверка влияния проектных правил

Одна и та же задача расчёта стоимости выполнена до и после подключения
проектных правил. Оба исходных ответа сохранены без исправлений, затем
проверены одним набором из 15 тестов. После правил проходит 15/15 вместо 8/15.

## Постановка и условия

Точный общий промпт — [experiments/task.md](experiments/task.md):

```text
Role: Python-разработчик.
Task: Напиши функцию calculate_total(prices_kopecks, delivery_kopecks=0),
которая считает общую стоимость готовых наборов питания с доставкой.
Context: prices_kopecks — список цен наборов в копейках; доставка также
задана в копейках. Функция возвращает итог в копейках. Python 3.12.
Format: Только исходный код функции в Python-файле.
```

Первый ответ создан в текущей сессии Codex до создания и чтения rules.md.
После него файл правил создан и явно прочитан, затем для той же постановки
создан второй ответ. Общие инструкции среды и история чата сохранялись;
проектный файл правил — добавленный контекст второго варианта. Модель и
параметры генерации отдельно не фиксировались и не переключались для опыта.

Это последовательный учебный эксперимент, не независимое слепое A/B-исследование.
Правила конкретизируют дополнительные условия входа, которых нет в коротком
запросе: целые неотрицательные копейки, список цен и запрет bool.
Проверка измеряет соблюдение полного проектного контракта. Она не означает,
что первый вариант ошибается на корректных входных данных краткого запроса.

## Сырой ответ до применения правил

Следующий блок скопирован из before_response.md автоматически без редактирования.

''' + before.strip() + '''

Исходный файл: [before.py](experiments/before.py).

## Сырой ответ после применения правил

Следующий блок скопирован из after_response.md автоматически без редактирования.

''' + after.strip() + '''

Исходный файл: [after.py](experiments/after.py).
Рабочий модуль pricing.py идентичен второму варианту.

## Единые проверки

Общий набор — [test_pricing.py](../foodtech_demo/tests/test_pricing.py).
Переменная PRICING_VARIANT выбирает только модуль, тесты не меняются.

| Группа | До правил | После правил |
|---|---|---|
| Сумма, доставка по умолчанию, пустой список, ноль | 4/4 | 4/4 |
| Точное большое целое, неизменность ввода, целый результат | 3/3 | 3/3 |
| Отрицательная цена и отрицательная доставка | 0/2 | 2/2 |
| float в цене и доставке | 0/2 | 2/2 |
| bool в цене и доставке | 0/2 | 2/2 |
| Строка в цене | 1/1 — TypeError возникает в sum | 1/1 — явная валидация |
| tuple вместо списка | 0/1 | 1/1 |
| Всего | 8/15 | 15/15 |

Отдельная качественная проверка исходников: у before нет аннотаций и docstring;
у after есть типизированная сигнатура, документированные ошибки и явные проверки.
Эти признаки не прибавлялись к числу 15 исполняемых тестов.

## Реальный запуск

Из папки Решение:

```powershell
python verify.py
```

Полные журналы: [before.txt](../evidence/before.txt),
[after.txt](../evidence/after.txt), [tests.txt](../evidence/tests.txt).
Среда и время проверки: [summary.json](../evidence/summary.json).

```text
До правил:    Ran 15 tests, FAILED (failures=7), exit_code=1
После правил: Ran 15 tests, OK, exit_code=0
Основной проект: Ran 41 tests, OK, exit_code=0
```

В before неуспешные проверки оставлены для демонстрации исходного результата.
Запуск всего пакета считается успешным при ожидаемом провале before и
успехе основного модуля и after. verify.py проверяет эти условия автоматически.

## Вывод

Правила сделали контракт явным: второй вариант отклоняет отрицательные суммы,
float, bool и неверный тип контейнера, сохраняя правильное сложение на валидных
входах. Появились аннотации и документированная семантика ошибок. Обычные
сценарии проходят в обоих вариантах; преимущество второго проявляется в
проверке ограничений проекта. Прирост составляет 7 успешных проверок из 15.

Сравнение ограничено одной задачей и одной последовательной сессией. История
чата и добавление подробных требований влияют на результат; независимый
эффект каждого правила и общая производительность моделей не измерялись.
Для повседневной работы полезность подхода подтверждена работающим модулем
заказа и граничными тестами; перенос на другие задачи требует новых проверок.
'''
    (hw2 / "testing.md").write_text(report, encoding="utf-8")

    required = [
        "README.md", "CHECKLIST.md", "ДЗ1/report.md", "ДЗ1/comparison.md",
        "ДЗ1/llm_checklist.md", "ДЗ2/hw_ai_rules.md", "ДЗ2/rules.md",
        "ДЗ2/prompt_templates.md", "ДЗ2/prompt_methodology.md", "ДЗ2/testing.md",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    broken_links = []
    for path in root.rglob("*.md"):
        content = path.read_text(encoding="utf-8-sig")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#")):
                continue
            target_path = unquote(target.split("#", 1)[0])
            if not (path.parent / target_path).exists():
                broken_links.append({"file": str(path.relative_to(root)), "target": target})
    rules = (hw2 / "rules.md").read_bytes()
    agents = (root / "foodtech_demo" / "AGENTS.md").read_bytes()
    rule_count = len(re.findall(r"^\d+\. ", rules.decode("utf-8"), flags=re.M))
    templates = (hw2 / "prompt_templates.md").read_text(encoding="utf-8")
    template_count = len(re.findall(r"^## \d+ ", templates, flags=re.M))
    rtcfs = {name: templates.count(f"### {name}") for name in ("Role", "Task", "Context", "Format")}
    raw_equal = True
    for name, response in (("before", before), ("after", after)):
        match = re.search(r"```python\n(.*?)\n```", response, flags=re.S)
        code = (experiments / f"{name}.py").read_text(encoding="utf-8")
        raw_equal = raw_equal and match is not None and match.group(1) == code.strip()
    final_equal = (experiments / "after.py").read_bytes() == (
        root / "foodtech_demo" / "foodtech" / "pricing.py"
    ).read_bytes()
    style_issues = []
    for path in (root / "foodtech_demo").rglob("*.py"):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if len(line) > 100:
                style_issues.append(f"{path.relative_to(root)}:{line_number}")
    results = {
        "required_files": len(required), "missing_files": missing,
        "broken_local_links": broken_links, "rule_count": rule_count,
        "template_count": template_count, "RTCF_block_counts": rtcfs,
        "rules_identical_to_AGENTS": rules == agents,
        "raw_responses_match_source": raw_equal,
        "production_pricing_identical_to_after": final_equal,
        "lines_over_100_in_demo": style_issues,
    }
    ok = (
        not missing and not broken_links and rule_count >= 10
        and template_count >= 5 and all(count == 2 * template_count for count in rtcfs.values())
        and rules == agents and raw_equal and final_equal and not style_issues
    )
    results["passed"] = ok
    (root / "evidence" / "package_validation.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    if not ok:
        raise SystemExit(json.dumps(results, ensure_ascii=False, indent=2))

    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
        and path.name != "manifest.sha256.json"
    )
    manifest = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in files
    }
    manifest_path = root / "manifest.sha256.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    files.append(manifest_path)
    output = root.parent / "ДЗ1_ДЗ2_FoodTech.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, "Решение/" + path.relative_to(root).as_posix())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise SystemExit("ZIP integrity check failed")
        for name, digest in manifest.items():
            actual = hashlib.sha256(archive.read("Решение/" + name)).hexdigest()
            if actual != digest:
                raise SystemExit(f"ZIP hash mismatch: {name}")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"ZIP: {output.name}; files: {len(files)}; bytes: {output.stat().st_size}")


if __name__ == "__main__":
    main()
