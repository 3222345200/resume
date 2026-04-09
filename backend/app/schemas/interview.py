from datetime import date, datetime, timezone

from pydantic import BaseModel, Field, field_validator, model_validator


INTERVIEW_RESULTS = ("scheduled", "completed", "passed", "rejected", "offer")
INTERVIEW_TYPES = ("online", "phone", "onsite", "video")
QUESTION_CATEGORIES = ("technical", "project", "behavioral", "fundamental", "qa", "other")
SELF_EVALUATIONS = ("good", "normal", "blocked")


def _clean_text(value: object) -> str:
    return str(value or "").strip()


class InterviewQuestionBaseSchema(BaseModel):
    sort_order: int = Field(default=1, ge=1)
    question_text: str = ""
    question_category: str = Field(default="other", max_length=50)
    answer_note: str = ""
    follow_up_question: str = ""
    self_evaluation: str = Field(default="normal", max_length=50)
    need_review: bool = False

    @field_validator("question_text", "answer_note", "follow_up_question", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> str:
        return _clean_text(value)

    @field_validator("question_category", mode="before")
    @classmethod
    def validate_question_category(cls, value: object) -> str:
        text = _clean_text(value) or "other"
        if text not in QUESTION_CATEGORIES:
            raise ValueError("question_category is invalid")
        return text

    @field_validator("self_evaluation", mode="before")
    @classmethod
    def validate_self_evaluation(cls, value: object) -> str:
        text = _clean_text(value) or "normal"
        if text not in SELF_EVALUATIONS:
            raise ValueError("self_evaluation is invalid")
        return text


class InterviewQuestionCreateSchema(InterviewQuestionBaseSchema):
    pass


class InterviewQuestionUpdateSchema(InterviewQuestionBaseSchema):
    pass


class InterviewQuestionReadSchema(InterviewQuestionBaseSchema):
    id: str
    created_at: str
    updated_at: str


class InterviewBaseSchema(BaseModel):
    application_id: str
    resume_id: str | None = None
    round_name: str = Field(default="", max_length=120)
    round_index: int = Field(default=1, ge=1, le=99)
    scheduled_at: datetime | None = None
    interview_type: str = Field(default="online", max_length=50)
    duration_minutes: int = Field(default=60, ge=0, le=720)
    interviewer_name: str = Field(default="", max_length=120)
    interviewer_role: str = Field(default="", max_length=120)
    result: str = Field(default="scheduled", max_length=50)
    is_reviewed: bool = False
    document_title: str = Field(default="", max_length=200)
    document_content: str = ""
    preparation_note: str = ""
    free_note: str = ""
    strength_note: str = ""
    weakness_note: str = ""
    missing_knowledge_note: str = ""
    next_round_prep_note: str = ""
    follow_up_action: str = ""
    follow_up_at: datetime | None = None
    need_thank_you: bool = False
    need_follow_up: bool = False

    @field_validator(
        "application_id",
        "round_name",
        "interviewer_name",
        "interviewer_role",
        "document_title",
        "document_content",
        "preparation_note",
        "free_note",
        "strength_note",
        "weakness_note",
        "missing_knowledge_note",
        "next_round_prep_note",
        "follow_up_action",
        mode="before",
    )
    @classmethod
    def normalize_text_fields(cls, value: object) -> str:
        return _clean_text(value)

    @field_validator("resume_id", mode="before")
    @classmethod
    def normalize_resume_id(cls, value: object) -> str | None:
        text = _clean_text(value)
        return text or None

    @field_validator("interview_type", mode="before")
    @classmethod
    def validate_interview_type(cls, value: object) -> str:
        text = _clean_text(value) or "online"
        if text not in INTERVIEW_TYPES:
            raise ValueError("interview_type is invalid")
        return text

    @field_validator("result", mode="before")
    @classmethod
    def validate_result(cls, value: object) -> str:
        text = _clean_text(value) or "scheduled"
        if text not in INTERVIEW_RESULTS:
            raise ValueError("result is invalid")
        return text

    @model_validator(mode="after")
    def normalize_round_name(self) -> "InterviewBaseSchema":
        if not self.round_name:
            self.round_name = f"第 {self.round_index} 轮"
        return self


class InterviewCreateSchema(InterviewBaseSchema):
    pass


class InterviewUpdateSchema(InterviewBaseSchema):
    pass


class InterviewResultUpdateSchema(BaseModel):
    result: str = Field(max_length=50)
    sync_application_status: bool = True

    @field_validator("result", mode="before")
    @classmethod
    def validate_result(cls, value: object) -> str:
        text = _clean_text(value)
        if text not in INTERVIEW_RESULTS:
            raise ValueError("result is invalid")
        return text


class InterviewApplicationSummarySchema(BaseModel):
    id: str
    company_name: str
    job_title: str
    status: str
    resume_id: str | None = None
    resume_title: str | None = None
    interview_count: int


class InterviewReadSchema(BaseModel):
    id: str
    application_id: str
    resume_id: str | None = None
    company_name: str
    job_title: str
    application_status: str
    resume_title: str | None = None
    round_name: str
    round_index: int
    scheduled_at: str | None = None
    interview_type: str
    duration_minutes: int
    interviewer_name: str
    interviewer_role: str
    result: str
    is_reviewed: bool
    document_title: str
    document_content: str
    preparation_note: str
    free_note: str
    strength_note: str
    weakness_note: str
    missing_knowledge_note: str
    next_round_prep_note: str
    follow_up_action: str
    follow_up_at: str | None = None
    need_thank_you: bool
    need_follow_up: bool
    question_items: list[InterviewQuestionReadSchema] = Field(default_factory=list)
    application_summary: InterviewApplicationSummarySchema
    created_at: str
    updated_at: str


class InterviewListItemSchema(BaseModel):
    id: str
    application_id: str
    company_name: str
    job_title: str
    round_name: str
    round_index: int
    scheduled_at: str | None = None
    interview_type: str
    result: str
    is_reviewed: bool
    interview_count: int
    application_status: str
    updated_at: str


class InterviewListResponseSchema(BaseModel):
    items: list[InterviewListItemSchema]


class InterviewStatsOverviewSchema(BaseModel):
    total_count: int
    this_week_count: int
    upcoming_count: int
    completed_count: int
    pending_review_count: int
    passed_count: int
    rejected_count: int


def compute_this_week_start(today: date | None = None) -> date:
    current_day = today or datetime.now(timezone.utc).date()
    return current_day.fromordinal(current_day.toordinal() - current_day.weekday())
