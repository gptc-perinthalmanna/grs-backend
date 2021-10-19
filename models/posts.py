from typing import Optional, List, Any
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


class PostInDB(Post):
    responses: Optional[List[PostResponse]]


class PostResponseSerialized(PostResponse):
    published: Optional[Any]
    modified: Optional[Any]

    @validator('published')
    def serialize_published(cls, v):
        return v.isoformat()

    @validator('modified')
    def serialize_modified(cls, v):
        return v.isoformat()


class PostSerialized(Post):
    key: Optional[Any]
    author: Optional[Any]
    published: Optional[Any]
    modified: Optional[Any]
    responses: Optional[List[PostResponseSerialized]]

    @validator('key')
    def serialize_key(cls, v):
        return v.hex

    @validator('author')
    def serialize_author(cls, v):
        return v.hex

    @validator('published')
    def serialize_published(cls, v):
        return v.isoformat()

    @validator('modified')
    def serialize_modified(cls, v):
        return v.isoformat()

