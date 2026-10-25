from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    RADIO = "radio"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"
    VISUAL = "visual"


class AlienContact(BaseModel):
    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def validate_contact_rules(self) -> "AlienContact":
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')
        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")
        if self.contact_type == ContactType.TELEPATHIC and \
                self.witness_count < 3:
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
                )
        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError("Strong signals must include a received message")
        return self


def main() -> None:
    contact = AlienContact(
        contact_id="AC_2024_001",
        timestamp=datetime(2024, 10, 25, 22, 30),
        location="Area 51, Nevada",
        contact_type=ContactType.RADIO,
        signal_strength=8.5,
        duration_minutes=45,
        witness_count=5,
        message_received="Greetings from Zeta Reticuli"
    )

    print("Alien Contact Log Validation")
    print("======================================")
    print("Valid contact report:")
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    print(f"Message: '{contact.message_received}'")
    print("======================================")

    try:
        AlienContact(
            contact_id="AC_2024_002",
            timestamp=datetime(2024, 10, 25, 23, 0),
            location="Area 51, Nevada",
            contact_type=ContactType.PHYSICAL,
            signal_strength=5.0,
            duration_minutes=30,
            witness_count=2,
            message_received=None,
            is_verified=False
        )
    except ValidationError as error:
        print("Expected validation error:")
        print(error.errors()[0]["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
