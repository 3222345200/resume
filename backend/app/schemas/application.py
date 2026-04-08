from datetime import date, datetime, timezone

from pydantic import BaseModel, Field, field_validator, model_validator


APPLICATION_STATUSES = (
    "想投",
    "已投递",
    "笔试",
    "面试中",
    "HR 面",
    "Offer",
    "已拒绝",
    "已结束",
)
APPLICATION_PRIORITIES = ("低", "中", "高")
FINAL_RESULT_BY_STATUS = {
    "Offer": "Offer",
    "已拒绝": "已拒绝",
    "已结束": "已结束",
}


def _clean_text(value: object) -> str:
    return str(value or "").strip()


class ApplicationStatusHistoryReadSchema(BaseModel):
    id: str
    from_status: str
    to_status: str
    note: str
    changed_at: str

    model_config = {"from_attributes": True}


class ApplicationBaseSchema(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    job_title: str = Field(min_length=1, max_length=200)
    department: str = Field(default="", max_length=200)
    city: str = Field(default="", max_length=120)
    job_link: str = Field(default="", max_length=500)
    jd_summary: str = ""
    salary_range: str = Field(default="", max_length=120)
    job_type: str = Field(default="", max_length=50)
    applied_at: date
    status: str = Field(default="已投递", max_length=50)
    channel: str = Field(default="", max_length=120)
    referrer_name: str = Field(default="", max_length=120)
    contact_name: str = Field(default="", max_length=120)
    contact_value: str = Field(default="", max_length=200)
    resume_id: str | None = None
    note: str = ""
    risk_note: str = ""
    priority: str = Field(default="中", max_length=20)
    next_action: str = ""
    next_follow_up_at: datetime | None = None
    last_follow_up_at: datetime | None = None
    deadline_at: datetime | None = None
    final_result: str = Field(default="", max_length=50)
    interview_count: int = Field(default=0, ge=0)

    @field_validator(
        "company_name",
        "job_title",
        "department",
        "city",
        "job_link",
        "jd_summary",
        "salary_range",
        "job_type",
        "channel",
        "referrer_name",
        "contact_name",
        "contact_value",
        "note",
        "risk_note",
        "next_action",
        "final_result",
        mode="before",
    )
    @classmethod
    def normalize_text_fields(cls, value: object) -> str:
        return _clean_text(value)

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: object) -> str:
        text = _clean_text(value)
        if text not in APPLICATION_STATUSES:
            raise ValueError("status 不在允许范围内")
        return text

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, value: object) -> str:
        text = _clean_text(value) or "中"
        if text not in APPLICATION_PRIORITIES:
            raise ValueError("priority 不在允许范围内")
        return text

    @model_validator(mode="after")
    def normalize_result(self) -> "ApplicationBaseSchema":
        if self.status in FINAL_RESULT_BY_STATUS:
            self.final_result = FINAL_RESULT_BY_STATUS[self.status]
        return self


class ApplicationCreateSchema(ApplicationBaseSchema):
    pass


class ApplicationUpdateSchema(ApplicationBaseSchema):
    pass


class ApplicationStatusUpdateSchema(BaseModel):
    status: str = Field(max_length=50)
    note: str = ""

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: object) -> str:
        text = _clean_text(value)
        if text not in APPLICATION_STATUSES:
            raise ValueError("status 不在允许范围内")
        return text

    @field_validator("note", mode="before")
    @classmethod
    def normalize_note(cls, value: object) -> str:
        return _clean_text(value)


class ApplicationFollowUpUpdateSchema(BaseModel):
    last_follow_up_at: datetime | None = None
    next_follow_up_at: datetime | None = None
    next_action: str = ""

    @field_validator("next_action", mode="before")
    @classmethod
    def normalize_next_action(cls, value: object) -> str:
        return _clean_text(value)


class ApplicationReadSchema(BaseModel):
    id: str
    company_name: str
    job_title: str
    department: str
    city: str
    job_link: str
    jd_summary: str
    salary_range: str
    job_type: str
    applied_at: str
    status: str
    status_updated_at: str
    last_follow_up_at: str | None = None
    next_follow_up_at: str | None = None
    is_todo: bool
    final_result: str
    channel: str
    referrer_name: str
    contact_name: str
    contact_value: str
    resume_id: str | None = None
    resume_title: str | None = None
    interview_count: int
    note: str
    risk_note: str
    priority: str
    next_action: str
    deadline_at: str | None = None
    created_at: str
    updated_at: str


class ApplicationDetailSchema(ApplicationReadSchema):
    status_history: list[ApplicationStatusHistoryReadSchema] = Field(default_factory=list)


class ApplicationListResponseSchema(BaseModel):
    items: list[ApplicationReadSchema]


class ApplicationStatsOverviewSchema(BaseModel):
    total_count: int
    new_this_week: int
    interviewing_count: int
    offer_count: int
    rejected_count: int
    no_feedback_count: int
    todo_count: int


def compute_application_todo(next_follow_up_at: datetime | None) -> bool:
    if next_follow_up_at is None:
        return False
    if next_follow_up_at.tzinfo is None:
        next_follow_up_at = next_follow_up_at.replace(tzinfo=timezone.utc)
    return next_follow_up_at <= datetime.now(timezone.utc)
