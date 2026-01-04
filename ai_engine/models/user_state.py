"""
UserState Schema for FigureIt AI Core (v1.0.0)

This file defines the canonical in-memory representation
of a single user across the entire AI system.

DESIGN PRINCIPLES:
- Pure data model (NO business logic)
- Deterministic and testable
- Safe for future MongoDB / API usage
- LLMs NEVER own memory — the system does

LOCKED DECISIONS:
- Enums for categorical safety
- Explicit validation for impossible states
- No chat history stored here
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


# =====================================================
# ENUMS (TYPE SAFETY & CLARITY)
# =====================================================

class Confidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Strictness(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProofExpectation(Enum):
    BASIC = "basic"
    STRONG = "strong"


class Urgency(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# =====================================================
# SUB-SCHEMAS (PURE STATE OBJECTS)
# =====================================================

@dataclass
class BasicProfile:
    """
    Immutable, user-provided context.
    Rarely changes once set.
    """
    college_tier: int            # 1, 2, or 3
    year_of_study: int           # 1–5 (dual degree / repeat allowed)
    time_availability: int       # hours per week
    constraints: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not (1 <= self.college_tier <= 3):
            raise ValueError(f"Invalid college_tier: {self.college_tier}")
        if not (1 <= self.year_of_study <= 5):
            raise ValueError(f"Invalid year_of_study: {self.year_of_study}")
        if self.time_availability < 0:
            raise ValueError("Time availability cannot be negative")


@dataclass
class InterestProfile:
    """
    Soft preference signals gathered via chatbot.
    NEVER decides outcomes alone.
    """
    interest_bias: Dict[str, float]          # e.g. {"backend": 0.7, "ml": 0.3}
    confidence_level: Confidence
    exploration_allowed: bool
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContextProfile:
    """
    Derived lens controlling system behavior.
    First real 'reasoning' output in the pipeline.
    """
    strictness_level: Strictness
    urgency_level: Urgency
    max_focus_skills: int                    # hard cap (1 or 2)
    proof_expectation: ProofExpectation


@dataclass
class EvidenceProfile:
    """
    Objective snapshot of user activity.
    Recomputed whenever data is refreshed.
    """
    github_stats: Dict[str, Any] = field(default_factory=dict)
    leetcode_stats: Dict[str, Any] = field(default_factory=dict)

    # Derived flags (e.g. "tutorial_hell", "easy_padding")
    flags: List[str] = field(default_factory=list)

    # Placeholder for Phase-2 RL (NOT used in v1)
    feature_vector: List[float] = field(default_factory=list)


@dataclass
class DecisionState:
    """
    System's explicit opinion at a point in time.
    """
    focus: List[str] = field(default_factory=list)
    park: List[str] = field(default_factory=list)
    drop: List[str] = field(default_factory=list)

    # skill_name -> explanation
    reasons: Dict[str, str] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BehaviorLog:
    """
    Tracks behavioral signals for future learning.
    NOT used for grading or ranking.
    """
    completed_tasks: int = 0
    skipped_tasks: int = 0
    panic_count: int = 0
    override_count: int = 0
    last_active: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SystemMemory:
    """
    Internal system metadata.
    No chat history or LLM memory is stored here.
    """
    last_intervention: Optional[datetime] = None
    sensitivity: str = "normal"   # "normal" | "fragile" | "resistant"


# =====================================================
# MASTER USER STATE (ENVIRONMENT STATE)
# =====================================================

@dataclass
class UserState:
    """
    Master state object for a single FigureIt user.

    Acts as:
    - Single Source of Truth
    - Environment State for RL (Phase 2)
    - Memory for all AI agents
    """

    user_id: str
    basic_profile: BasicProfile

    # Filled progressively by agents
    interest_profile: Optional[InterestProfile] = None
    context_profile: Optional[ContextProfile] = None
    evidence_profile: Optional[EvidenceProfile] = None
    decision_state: Optional[DecisionState] = None

    behavior_log: BehaviorLog = field(default_factory=BehaviorLog)
    system_memory: SystemMemory = field(default_factory=SystemMemory)

    # Metadata
    schema_version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # -------------------------
    # Serialization Helpers
    # -------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize UserState for JSON / DB storage.
        Enums and datetimes are preserved as-is for now.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserState":
        """
        Deserialize raw dict into UserState.
        Explicitly not implemented in v1.
        """
        raise NotImplementedError(
            "from_dict is intentionally not implemented in v1. "
            "Use a library like pydantic or dacite in persistence layer."
        )


# =====================================================
# SANITY CHECK (LOCAL TEST)
# =====================================================

if __name__ == "__main__":
    try:
        user = UserState(
            user_id="u_test_001",
            basic_profile=BasicProfile(
                college_tier=3,
                year_of_study=2,
                time_availability=10,
                constraints=["slow_internet"]
            )
        )
        print("✅ UserState created successfully")
        print(user)

        # Should fail
        bad_user = UserState(
            user_id="u_bad",
            basic_profile=BasicProfile(
                college_tier=5,
                year_of_study=2,
                time_availability=-5
            )
        )
    except ValueError as e:
        print(f"✅ Validation caught error: {e}")