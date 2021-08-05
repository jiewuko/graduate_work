from pydantic import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True

    PROJECT_NAME: str = "Cinema together API"
    PROJECT_HOST: str = "0.0.0.0"
    PROJECT_PORT: int = 8001
    WS_PORT: int = 8002

    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USERNAME: str = 'test'
    DB_PASSWORD: str = 'test'
    DB_NAME: str = 'test'

    REDIS_DSN: str = 'redis://localhost:6379/0'

    JWT_SECRET_KEY: str = 'secret'
    JWT_ALG: str = "HS256"

    @property
    def pg_dsn(self):
        return f'postgresql+asyncpg://' \
               f'{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'  # noqa

    class Config:
        env_file = ".envrc"
        case_sensitive = True


settings = Settings()
