from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Sequence

from src.core.schemas import FIOResult
from src.core.services.extraction_service import ExtractionService


TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё]+")
CYR_WORD_RE = re.compile(r"^[А-ЯЁ]+$")
LATIN_ONLY_RE = re.compile(r"^[A-Za-z]+$")
HAS_LATIN_RE = re.compile(r"[A-Za-z]")

# Compact lookalike transliteration for mixed-script OCR noise.
LOOKALIKE_LATIN = "ABCEHKMOPTXYabcehkmoptxy"
LOOKALIKE_CYRILLIC = "АВСЕНКМОРТХУавсенкмортху"
LOOKALIKE_MAP = str.maketrans(LOOKALIKE_LATIN, LOOKALIKE_CYRILLIC)

STOPWORDS = {
    "РЕСПУБЛИКА",
    "КРАЙ",
    "ОБЛАСТЬ",
    "РАЙОН",
    "НАС",
    "НАСЕЛЕННЫЙ",
    "ПУНКТ",
    "УЛИЦА",
    "ДОМ",
    "КОРПУС",
    "СТРОЕНИЕ",
    "КВАРТИРА",
    "ОСОБЫЕ",
    "ОТМЕТКИ",
}


@dataclass(slots=True)
class ExtractionProviderSettings:
    """Runtime-tunable parameters for rule-based FIO extraction."""

    anchor_text: str = "СОБСТВЕННИК"
    anchor_threshold: float = 0.55
    owner_threshold: float = 0.68
    min_word_length: int = 3


class ExtractionProvider(ExtractionService):
    """Rule-based FIO extraction from OCR text."""

    def __init__(self, settings: ExtractionProviderSettings | None = None) -> None:
        self.settings = settings or ExtractionProviderSettings()

    def extract_fio(self, text: str) -> FIOResult:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return FIOResult()

        anchor_idx, anchor_score = self._find_anchor(lines)
        if anchor_idx is not None and anchor_score >= self.settings.anchor_threshold:
            primary_zone = lines[anchor_idx + 1 :]
        else:
            primary_zone = lines

        primary_tokens = self._collect_tokens(primary_zone)
        if len(primary_tokens) >= 3:
            surname, name, patronymic = primary_tokens[:3]
            return self._build_fio(surname=surname, name=name, patronymic=patronymic)

        # Fallback requested by product: collect 3 words starting from name token.
        fallback_tokens = self._collect_tokens(lines)
        fallback_triplet = self._fallback_from_name(fallback_tokens)
        if fallback_triplet is None:
            return FIOResult()

        name, patronymic, surname = fallback_triplet
        return self._build_fio(surname=surname, name=name, patronymic=patronymic)

    def _find_anchor(self, lines: Sequence[str]) -> tuple[int | None, float]:
        best_idx: int | None = None
        best_score = -1.0

        for idx, line in enumerate(lines):
            words = [self._normalize_word(token) for token in TOKEN_RE.findall(line)]
            merged = "".join(word for word in words if word)
            if not merged:
                continue

            score = SequenceMatcher(None, merged, self.settings.anchor_text).ratio()
            if score > best_score:
                best_idx = idx
                best_score = score

        return best_idx, best_score

    def _collect_tokens(self, lines: Sequence[str]) -> list[str]:
        tokens: list[str] = []
        for line in lines:
            for raw_token in TOKEN_RE.findall(line):
                token = self._normalize_word(raw_token)
                if token is None:
                    continue
                if self._is_close_to_owner(token):
                    continue
                if token in STOPWORDS:
                    continue
                if len(token) < self.settings.min_word_length:
                    continue
                tokens.append(token)
        return tokens

    def _fallback_from_name(self, tokens: Sequence[str]) -> tuple[str, str, str] | None:
        if len(tokens) < 3:
            return None

        return tokens[0], tokens[1], tokens[2]

    def _normalize_word(self, raw: str) -> str | None:
        if LATIN_ONLY_RE.fullmatch(raw):
            return None

        repaired = raw.translate(LOOKALIKE_MAP).upper()
        repaired = re.sub(r"[^А-ЯЁA-Z]", "", repaired)
        if HAS_LATIN_RE.search(repaired):
            return None
        if not CYR_WORD_RE.fullmatch(repaired):
            return None
        return repaired

    def _is_close_to_owner(self, token: str) -> bool:
        score = SequenceMatcher(None, token, "ВЛАДЕЛЕЦ").ratio()
        return score >= self.settings.owner_threshold

    @staticmethod
    def _title_case(token: str) -> str:
        return token[:1] + token[1:].lower()

    def _build_fio(self, *, surname: str, name: str, patronymic: str) -> FIOResult:
        return FIOResult(
            surname=self._title_case(surname),
            name=self._title_case(name),
            patronymic=self._title_case(patronymic),
        )
