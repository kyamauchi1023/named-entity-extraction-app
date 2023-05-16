from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Mail(BaseModel):
    body_text: str = Field(None, description="Gmailの本文")
    model: Literal["qa", "ner"] = Field(None, description="モデル名")


class ExtractedInformation(BaseModel):
    event: Optional[List[str]] = Field(None, description="イベント名")
    startingDateTime: Optional[str] = Field(None, description="開始日時(2022/04/18 08:00の形式)")
    endingDateTime: Optional[str] = Field(None, description="終了日時(2022/04/18 09:00の形式)")
    location: Optional[List[str]] = Field(None, description="場所")
    person: Optional[List[str]] = Field(None, description="人名")
