from typing import Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: Optional[bool] = Field(default=True)


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: Optional[str] = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000)

    @model_validator(mode="after")
    def validate_mission_safety(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')
        has_command_leader = any(
            member.rank in (Rank.COMMANDER, Rank.CAPTAIN)
            for member in self.crew
        )
        if not has_command_leader:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )
        if self.duration_days > 365:
            experienced_count = sum(
                member.years_experience >= 5 for member in self.crew
            )
            if experienced_count / len(self.crew) < 0.5:
                raise ValueError(
                    "Long missions require at least 50% experienced crew"
                )
        if any(not member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")
        return self


def main() -> None:
    crew = [
        CrewMember(
            member_id="C001",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=38,
            specialization="Mission Command",
            years_experience=15,
        ),
        CrewMember(
            member_id="C002",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=34,
            specialization="Navigation",
            years_experience=8,
        ),
        CrewMember(
            member_id="C003",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=29,
            specialization="Engineering",
            years_experience=4,
        ),
    ]
    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2024, 11, 1),
        duration_days=900,
        crew=crew,
        budget_millions=2500.0,
    )

    print("Space Mission Crew Validation")
    print("=========================================")
    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(
            f"- {member.name} ({member.rank.value}) - {member.specialization}"
        )
    print("=========================================")

    invalid_crew = [
        member.model_copy(update={"rank": Rank.OFFICER})
        for member in mission.crew
    ]
    try:
        SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2024, 11, 1),
            duration_days=900,
            crew=invalid_crew,
            budget_millions=2500.0
        )
    except ValidationError as error:
        print("Expected validation error:")
        print(error.errors()[0]["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
