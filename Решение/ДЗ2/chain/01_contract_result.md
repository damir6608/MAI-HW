# Контракт расчёта заказа

Позиция `OrderItem(unit_price_kopecks: int, quantity: int)` неизменяема.
Цена неотрицательна, количество строго положительно. bool не принимается.

`calculate_total(prices_kopecks: list[int], delivery_kopecks: int = 0) -> int`
суммирует цены и доставку, не изменяет список. Пустой список допустим: функция
универсальна; непустоту заказа проверяет `quote_order`.

`quote_order(items: list[OrderItem], days: int, first_delivery: date,
today: date, delivery_kopecks: int = 0) -> OrderQuote` возвращает
`subtotal_kopecks`, `delivery_kopecks`, `total_kopecks`, `first_delivery`, `days`.

Формула: subtotal = Σ(цена за день × количество) × days;
total = subtotal + доставка за заказ. days принимает только 1 и 7.
TypeError означает некорректный тип, ValueError — недопустимое значение.
datetime не принимается вместо date: часы и часовой пояс не входят в контракт.

| Сценарий | Ожидаемый результат |
|---|---|
| 90000 × 2, 110000 × 1, 1 день, доставка 15000 | 305000 копеек |
| Те же позиции на 7 дней | 2045000 копеек |
| today 2026-10-12, доставка 2026-10-14 | Допуск |
| Доставка 2026-10-13 | ValueError |
| Пустой заказ | ValueError |
| days = 0, 2, 8 | ValueError |
| Цена или доставка < 0 | ValueError |
| Цена float, bool или строка | TypeError |
| quantity = 0 | ValueError |
| quantity = True | TypeError |
| Переход месяца и года при today + 2 | Корректное сравнение дат |

Критерии приёмки: обе формулы дают указанные суммы; дата на границе допускается;
все перечисленные некорректные вводы отклоняются; исходные коллекции сохраняются.
