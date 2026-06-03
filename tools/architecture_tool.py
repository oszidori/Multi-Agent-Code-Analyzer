import json
from difflib import get_close_matches
import os
from pydantic import BaseModel

# Minimum similarity ratio for fuzzy matching — 0.8 catches single-char typos
# without risking false positives between similar-but-distinct words (e.g. "server" vs "service")
FUZZY_CUTOFF = 0.8
DESIGN_PATTERNS_PATH = os.environ.get("DESIGN_PATTERNS_PATH")

# Facts extracted from the analyzed codebase, passed in by the calling agent
class ArchitectureFacts(BaseModel):
    technologies: list[str]
    modules: list[str]
    protocols: list[str]
    annotations: list[str]
    keywords: list[str]

# Per-field match detail: which expected values were found, which were not, and the ratio
class FieldMatch(BaseModel):
    field: str
    expected: list[str]
    matched: list[str]
    missing: list[str]
    ratio: float  # matched / expected, 0.0–1.0

# Full score trace for one pattern: individual field results and the two aggregated sub-scores
class ScoreBreakdown(BaseModel):
    required_fields: list[FieldMatch]
    optional_fields: list[FieldMatch]
    required_score: float  # average ratio across all required fields
    optional_score: float  # average ratio across all optional fields

# A pattern that passed the confidence threshold, enriched with its score breakdown
class DetectedPattern(BaseModel):
    id: str
    name: str
    category: str
    confidence: float  # final score: 0.8 * required_score + 0.2 * optional_score
    description: str
    documentation_url: str
    breakdown: ScoreBreakdown

class PatternDetectionResult(BaseModel):
    patterns: list[DetectedPattern]

# The fact fields that pattern definitions can specify requirements/optionals for
fields = ["technologies", "modules", "protocols", "annotations", "keywords"]

def normalize(value: str) -> str:
    return value.strip().lower()

def _build_field_match(field: str, expected: list[str], actual: list[str]) -> FieldMatch:
    expected_norm = {normalize(x) for x in expected}
    actual_norm = {normalize(x) for x in actual}

    matched = []
    missing = []

    for exp in expected_norm:
        # Accept close matches so minor typos in extracted facts still count (e.g. "servce" → "service")
        if exp in actual_norm or get_close_matches(exp, actual_norm, n=1, cutoff=FUZZY_CUTOFF):
            matched.append(exp)
        else:
            missing.append(exp)

    ratio = len(matched) / len(expected_norm)
    return FieldMatch(
        field=field,
        expected=sorted(expected_norm),
        matched=sorted(matched),
        missing=sorted(missing),
        ratio=round(ratio, 2),
    )

def score_pattern(pattern: dict, facts: ArchitectureFacts) -> tuple[float, ScoreBreakdown]:
    required = pattern.get("required", {})
    optional = pattern.get("optional", {})

    required_field_matches: list[FieldMatch] = []
    optional_field_matches: list[FieldMatch] = []

    for field in fields:
        expected = required.get(field, [])
        if expected:
            actual = getattr(facts, field)
            required_field_matches.append(_build_field_match(field, expected, actual))

    for field in fields:
        expected = optional.get(field, [])
        if expected:
            actual = getattr(facts, field)
            optional_field_matches.append(_build_field_match(field, expected, actual))

    required_scores = [fm.ratio for fm in required_field_matches]
    optional_scores = [fm.ratio for fm in optional_field_matches]

    # No required fields defined → treat as fully satisfied (pattern is purely optional-driven)
    required_score = sum(required_scores) / len(required_scores) if required_scores else 1.0
    # No optional fields defined → contributes 0 bonus to confidence
    optional_score = sum(optional_scores) / len(optional_scores) if optional_scores else 0.0

    # Required fields carry 80% of the score; optional fields are a 20% bonus
    confidence = round(0.8 * required_score + 0.2 * optional_score, 2)

    breakdown = ScoreBreakdown(
        required_fields=required_field_matches,
        optional_fields=optional_field_matches,
        required_score=round(required_score, 2),
        optional_score=round(optional_score, 2),
    )

    return confidence, breakdown

def _load_knowledge(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def detect_patterns(facts: ArchitectureFacts, knowledge_path: str = DESIGN_PATTERNS_PATH, threshold: float = 0.6) -> PatternDetectionResult:
    db = _load_knowledge(knowledge_path)
    detected: list[DetectedPattern] = []

    for pattern in db["patterns"]:
        confidence, breakdown = score_pattern(pattern, facts)

        # Patterns below the threshold are silently dropped
        if confidence < threshold:
            continue

        detected.append(
            DetectedPattern(
                id=pattern["id"],
                name=pattern["name"],
                category=pattern["category"],
                confidence=confidence,
                description=pattern["description"],
                documentation_url=pattern["documentation_url"],
                breakdown=breakdown,
            )
        )

    detected.sort(
        key=lambda p: p.confidence,
        reverse=True,
    )

    return PatternDetectionResult(patterns=detected)
