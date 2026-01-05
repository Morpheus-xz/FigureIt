from dataclasses import dataclass
from typing import Dict
from datetime import datetime


@dataclass
class SkillMarketSignal:
    jobs: int
    blogs: int
    saturation: str            # low | medium | high
    previous_jobs: int         # for trend calculation


class MarketState:
    """
    Deterministic snapshot of market reality.
    This class NEVER uses LLMs.
    """

    def __init__(self):
        # MVP static dataset (replace with real APIs later)
        self.skills: Dict[str, SkillMarketSignal] = {
            # Frontend
            "React": SkillMarketSignal(4200, 380, "high", 4500),
            "Next.js": SkillMarketSignal(2600, 240, "medium", 2300),
            "Vue.js": SkillMarketSignal(1200, 150, "medium", 1100),

            # Backend
            "Python": SkillMarketSignal(5100, 420, "medium", 4800),
            "Java": SkillMarketSignal(4700, 300, "medium", 5000),
            "Node.js": SkillMarketSignal(3800, 350, "high", 4000),
            "Go": SkillMarketSignal(1500, 180, "low", 1100),

            # Infra
            "Docker": SkillMarketSignal(3600, 260, "medium", 3400),
            "AWS": SkillMarketSignal(5400, 410, "medium", 5000),

            # Data / ML
            "TensorFlow": SkillMarketSignal(1800, 260, "high", 2000),
            "PyTorch": SkillMarketSignal(2100, 290, "medium", 1900),

            # Niche
            "Rust": SkillMarketSignal(900, 120, "low", 700),
            "PHP": SkillMarketSignal(1600, 90, "high", 1900),
        }

        self.generated_at = datetime.utcnow().isoformat()
