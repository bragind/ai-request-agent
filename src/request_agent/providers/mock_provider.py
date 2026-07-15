from __future__ import annotations

from dataclasses import dataclass

from request_agent.schemas import LLMResult, Priority, RequestType


@dataclass(frozen=True)
class Rule:
    request_type: RequestType
    keywords: tuple[str, ...]


# The order is intentional: when several categories match, business-impacting
# access and money problems should win over generic technical wording.
CATEGORY_RULES: tuple[Rule, ...] = (
    Rule(
        RequestType.ACCOUNT_ACCESS,
        (
            "войти",
            "вход",
            "пароль",
            "аккаунт",
            "личный кабинет",
            "авторизация",
            "заблокирован",
            "доступ",
        ),
    ),
    Rule(
        RequestType.BILLING,
        (
            "оплата",
            "платеж",
            "платёж",
            "списание",
            "возврат",
            "счет",
            "счёт",
            "деньги",
            "карта",
            "чек",
        ),
    ),
    Rule(
        RequestType.TECHNICAL_ISSUE,
        ("ошибка", "не работает", "сбой", "зависает", "403", "404", "500", "приложение", "сервер"),
    ),
    Rule(
        RequestType.COMPLAINT,
        (
            "жалоба",
            "недоволен",
            "недовольна",
            "грубость",
            "плохое обслуживание",
            "обман",
            "претензия",
        ),
    ),
    Rule(
        RequestType.CONSULTATION,
        ("подскажите", "как", "где", "можно ли", "расскажите", "консультация"),
    ),
    Rule(
        RequestType.FEATURE_REQUEST,
        (
            "добавьте",
            "новая функция",
            "хотелось бы",
            "улучшить",
            "предложение",
            "реализовать возможность",
        ),
    ),
)

CRITICAL_KEYWORDS = (
    "авария",
    "угроза безопасности",
    "утечка данных",
    "система полностью недоступна",
    "не работает у всех",
    "пожар",
    "взлом",
    "критический сбой",
)
HIGH_KEYWORDS = (
    "невозможно войти",
    "не проходит оплата",
    "сервис недоступен",
    "работа заблокирована",
    "ошибка повторяется",
    "срочно",
    "как можно скорее",
)


class MockProvider:
    async def analyze(self, text: str) -> LLMResult:
        lowered = text.lower()
        request_type, matches = self._classify(lowered)
        priority = self._priority(lowered, request_type)
        needs_human = priority in {Priority.HIGH, Priority.CRITICAL} or request_type in {
            RequestType.BILLING,
            RequestType.COMPLAINT,
        }
        return LLMResult(
            request_type=request_type,
            summary=self._summary(text),
            priority=priority,
            needs_human=needs_human,
            confidence=self._confidence(request_type, matches, priority),
        )

    def _classify(self, lowered: str) -> tuple[RequestType, int]:
        for rule in CATEGORY_RULES:
            matches = sum(keyword in lowered for keyword in rule.keywords)
            if matches:
                return rule.request_type, matches
        return RequestType.OTHER, 0

    def _priority(self, lowered: str, request_type: RequestType) -> Priority:
        if any(keyword in lowered for keyword in CRITICAL_KEYWORDS):
            return Priority.CRITICAL
        if any(keyword in lowered for keyword in HIGH_KEYWORDS):
            return Priority.HIGH
        medium_types = {
            RequestType.ACCOUNT_ACCESS,
            RequestType.BILLING,
            RequestType.TECHNICAL_ISSUE,
        }
        if request_type in medium_types:
            return Priority.MEDIUM
        if request_type is RequestType.OTHER:
            return Priority.LOW
        return Priority.MEDIUM

    def _summary(self, text: str) -> str:
        sentence = text.split(".")[0].strip()
        if len(sentence) > 180:
            sentence = sentence[:177].rstrip() + "..."
        if not sentence.endswith((".", "!", "?")):
            sentence = f"{sentence}."
        return sentence

    def _confidence(self, request_type: RequestType, matches: int, priority: Priority) -> float:
        if request_type is RequestType.OTHER:
            return 0.55
        confidence = 0.72 + min(matches, 4) * 0.05
        if priority in {Priority.HIGH, Priority.CRITICAL}:
            confidence += 0.05
        return round(min(confidence, 0.95), 2)
