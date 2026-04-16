from __future__ import annotations

from src.core.schemas import FIOResult
from src.providers.extraction_provider import ExtractionProvider


def test_extraction_provider_extracts_expected_fio() -> None:
    text = "\n".join(
        [
            "СОБСТВЕННИК",
            "(владелец)",
            "КОБАЛАВА",
            "KOBALAVA",
            "МАКСИМ",
            "MAKSIM",
            "ЮРЬЕВИЧ",
            "СудъектРоссийской Федерации",
            "MockBa",
        ]
    )

    provider = ExtractionProvider()
    result = provider.extract_fio(text)

    assert result == FIOResult(
        surname="Кобалава",
        name="Максим",
        patronymic="Юрьевич",
    )
