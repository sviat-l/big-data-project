from pydantic import BaseModel, Field
from typing import List


class DomainModel(BaseModel):
    domains: List[str] = Field(..., title="The list of domains")


class UserPageModel(BaseModel):
    page_id: int = Field(..., title="The ID of the page")
    page_title: str = Field(..., title="The title of the page")


class PageModel(BaseModel):
    page_id: int = Field(..., title="The ID of the page")
    page_title: str = Field(..., title="The title of the page")
    domain: str = Field(..., title="The domain")


class DomainPageModel(BaseModel):
    domain: str = Field(..., title="The domain")
    number_of_pages: int = Field(..., title="The number of pages created in the domain")


class PagesByUsersModel(BaseModel):
    user_id: int | None = Field(..., title="The ID of the user")
    user_name: str = Field(..., title="The name of the user")
    number_of_pages: int = Field(..., title="The number of pages created by the user")


class Statistic(BaseModel):
    domain: str
    created_pages: int

class HourlyDomainStatsModel(BaseModel):
    time_start: str
    time_end: str
    statistics: List[Statistic]

class BotCreationStat(BaseModel):
    domain: str
    created_by_bots: int

class BotCreationStatsModel(BaseModel):
    time_start: str
    time_end: str
    statistics: List[BotCreationStat]

class TopUser(BaseModel):
    user_id: int
    user_name: str
    page_titles: List[str]
    total_pages: int

class TopUsersModel(BaseModel):
    time_start: str
    time_end: str
    users: List[TopUser]
