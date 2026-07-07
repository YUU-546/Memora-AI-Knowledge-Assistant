from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "memora-backend"
    app_secret_key: str = "change-me"
    public_base_url: str = "http://127.0.0.1:8000"
    log_level: str = "INFO"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_max_tokens: int = 1200
    deepseek_temperature: float = 0.2

    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_bitable_app_token: str = ""
    feishu_bitable_table_id: str = ""

    wechat_corp_id: str = ""
    wechat_agent_id: str = ""
    wechat_secret: str = ""
    wechat_token: str = ""
    wechat_aes_key: str = Field(default="", validation_alias="WECHAT_AES_KEY")

    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_oss_bucket: str = ""
    aliyun_oss_endpoint: str = ""

    database_url: str = ""
    redis_url: str = ""

    @property
    def feishu_enabled(self) -> bool:
        return all(
            [
                self.feishu_app_id,
                self.feishu_app_secret,
                self.feishu_bitable_app_token,
                self.feishu_bitable_table_id,
            ]
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
