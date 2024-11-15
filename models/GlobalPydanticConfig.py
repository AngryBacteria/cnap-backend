from pydantic import ConfigDict

GLOBAL_PYDANTIC_CONFIG = ConfigDict(
    extra="allow", str_strip_whitespace=True, strict=False
)
