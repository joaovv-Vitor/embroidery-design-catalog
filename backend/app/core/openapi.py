from typing import Any

from fastapi import FastAPI


def configure_binary_file_fields(app: FastAPI) -> None:
    default_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        schema = default_openapi()
        _replace_binary_content_media_type(schema)
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]


def _replace_binary_content_media_type(value: Any) -> None:
    if isinstance(value, dict):
        if value.get("contentMediaType") == "application/octet-stream":
            value.pop("contentMediaType")
            value["format"] = "binary"
        for child in value.values():
            _replace_binary_content_media_type(child)
    elif isinstance(value, list):
        for child in value:
            _replace_binary_content_media_type(child)
