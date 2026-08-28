"""标签接口请求模型。"""

from pydantic import BaseModel, Field


# region 标签创建请求
class TagCreateRequest(BaseModel):
    """创建标签接口接收的标签名称和显示颜色。"""

    # 长度与 Tag ORM 模型的 String(50) 保持一致。
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    # 颜色可以不传；传入时必须是 # 加六位十六进制字符。
    color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="十六进制标签颜色，例如 #3B82F6",
    )


# endregion


__all__ = ["TagCreateRequest"]
