from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator


def validate_color(value: str) -> str:
    if not value.startswith("#"):
        raise ValueError("Color must start with #")
    if len(value) != 7:
        raise ValueError("Color must have 7 characters")
    return value


Color = Annotated[str, BeforeValidator(validate_color)]
