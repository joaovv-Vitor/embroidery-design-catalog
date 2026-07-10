from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Embroidery Design Catalog"
    environment: str = "development"


settings = Settings()

