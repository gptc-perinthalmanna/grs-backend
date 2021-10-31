from typing import Dict, Optional, List, Any
from pydantic import BaseModel, UUID4, validator
from enum import Enum
from datetime import datetime


class Status(str, Enum):
    draft = 'draft'
    open = 'open'
    replied = 'replied'
    authorResponded = 'authorResponded'
    adminResponded = 'adminResponded'
    closed = 'closed'
    deleted = 'deleted'
    hidden = 'hidden'
    priorityChanged = 'priorityChanged'
    solved = 'solved'


class Priority(str, Enum):
    veryLow = 'veryLow'
    low = 'low'
    medium = 'medium'
    high = 'high'
    important = 'important'


class StatusChange(BaseModel):
    prev: Status
    to: Status


class PostResponse(BaseModel):
    id: int
    author: UUID4
    content: str
    statusChange: StatusChange
    published: datetime
    modified: datetime
    deleted: bool = False
    visible: bool = True


    @validator('visible')
    def deleted_val(cls, v, values, **kwargs):
        if 'deleted' in values and values['deleted'] == v:
            raise ValueError('If value is deleted then visibility cannot be true')
        return v


class NewResponse(BaseModel):
    post_key: UUID4
    content: str
    status: Status
    user_id: Optional[UUID4]


class NewPost(BaseModel):
    subject: str
    content: str
    priority: Priority


class Post(BaseModel):
    key: UUID4
    subject: str
    content: str
    priority: Priority
    status: Status
    author: UUID4
    authorName: Optional[str]
    published: datetime
    modified: datetime
    deleted: bool = False
    visible: bool = True

    @validator('visible')
    def deleted_val(cls, v, values, **kwargs):
        if 'deleted' in values and values['deleted'] == v:
            raise ValueError('If value is deleted then visibility cannot be true')
        return v

class Telegram(BaseModel):
    chat_id: int
    message_id: int

class PostInDB(Post):
    telegram: Optional[List[Telegram]] = None
    responses: Optional[List[PostResponse]]


class PostResponseSerialized(PostResponse):
    published: Optional[Any]
    modified: Optional[Any]
    author: Optional[Any]

    @validator('author')
    def serialize_uuid(cls, v):
        return v.hex

    @validator('published', 'modified')
    def serialize_date(cls, v):
        return v.isoformat()


class PostSerialized(Post):
    key: Optional[Any]
    author: Optional[Any]
    published: Optional[Any]
    modified: Optional[Any]
    telegram_message_id: Optional[int] = None
    responses: Optional[List[PostResponseSerialized]]

    @validator('key', 'author')
    def serialize_uuid(cls, v):
        return v.hex

    @validator('published', 'modified')
    def serialize_date(cls, v):
        return v.isoformat()

