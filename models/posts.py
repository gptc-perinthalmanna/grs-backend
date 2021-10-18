from typing import Optional, List
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
    responses: Optional[List[PostResponse]]
