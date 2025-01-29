from pydantic import ConfigDict, BaseModel


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True, strict=False)
