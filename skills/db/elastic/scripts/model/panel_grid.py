from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PanelGrid:
    x: int = 0
    y: int = 0
    w: int = 24
    h: int = 15

    @classmethod
    def from_dict(cls, data: dict) -> PanelGrid:
        return cls(
            x=int(data.get("x", 0)),
            y=int(data.get("y", 0)),
            w=int(data.get("w", 24)),
            h=int(data.get("h", 15)),
        )

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}
