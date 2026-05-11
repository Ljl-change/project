"""Core data models for DocQualityChecker."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Issue:
    """Represents a single document quality issue."""

    category: str
    severity: str
    location: str
    message: str
    suggestion: str
    excerpt: Optional[str] = None
    rule_id: str = ""
    confidence: str = "medium"
    principle: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue into a serializable dictionary."""

        return asdict(self)


@dataclass
class DocumentStats:
    """Basic statistics extracted from a document."""

    file_name: str
    file_path: str
    total_chars: int
    paragraph_count: int
    empty_paragraph_count: int
    heading_count: int
    table_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert the stats into a serializable dictionary."""

        return asdict(self)


@dataclass
class StructureCheckItem:
    """Represents whether a required section was found."""

    name: str
    exists: bool
    matched_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the structure check item into a serializable dictionary."""

        return asdict(self)


@dataclass
class ParagraphInfo:
    """Stores extracted paragraph metadata."""

    index: int
    text: str
    style_name: str
    is_heading: bool = False
    heading_number: Optional[str] = None


@dataclass
class DocumentContent:
    """Stores extracted content used by rule checks."""

    stats: DocumentStats
    paragraphs: List[ParagraphInfo] = field(default_factory=list)


@dataclass
class AIReportSummary:
    """Natural-language summary generated from structured rule results."""

    overall_comment: str
    main_problems: List[str] = field(default_factory=list)
    priority_suggestions: List[str] = field(default_factory=list)
    polished_summary: str = ""
    risk_notice: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the AI summary into a serializable dictionary."""

        return asdict(self)


@dataclass
class CheckResult:
    """Represents the final check result."""

    stats: DocumentStats
    issues: List[Issue]
    structure_items: List[StructureCheckItem]
    score: int
    level: str
    created_at: str
    ai_summary: Optional[AIReportSummary] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the full result into a serializable dictionary."""

        return {
            "stats": self.stats.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
            "structure_items": [item.to_dict() for item in self.structure_items],
            "score": self.score,
            "level": self.level,
            "created_at": self.created_at,
            "ai_summary": self.ai_summary.to_dict() if self.ai_summary else None,
        }
