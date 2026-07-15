from __future__ import annotations

import pytest

from request_agent.providers.mock_provider import MockProvider
from request_agent.schemas import Priority, RequestType


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Не могу войти в личный кабинет, пароль не подходит.", RequestType.ACCOUNT_ACCESS),
        ("Прошу вернуть деньги, было двойное списание с карты.", RequestType.BILLING),
        ("Приложение не работает, появляется ошибка 500.", RequestType.TECHNICAL_ISSUE),
        ("Жалоба на грубость сотрудника и плохое обслуживание.", RequestType.COMPLAINT),
        ("Подскажите, где посмотреть тарифы?", RequestType.CONSULTATION),
        ("Добавьте новую функцию экспорта отчетов.", RequestType.FEATURE_REQUEST),
        ("Добрый день, пишу короткое сообщение без явной темы.", RequestType.OTHER),
    ],
)
async def test_classifies_request_types(text: str, expected: RequestType) -> None:
    result = await MockProvider().analyze(text)
    assert result.request_type == expected


async def test_mock_provider_is_stable() -> None:
    provider = MockProvider()
    text = "Не могу войти в личный кабинет. После ввода пароля появляется ошибка 403."
    first = await provider.analyze(text)
    second = await provider.analyze(text)
    assert first == second


async def test_priority_and_human_flag_for_urgent_access_issue() -> None:
    text = "Срочно невозможно войти в аккаунт, работа заблокирована."
    result = await MockProvider().analyze(text)
    assert result.priority == Priority.HIGH
    assert result.needs_human is True
