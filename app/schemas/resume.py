import re

from pydantic import BaseModel, Field, model_validator


DATE_VALUE_PATTERN = re.compile(r"^\d{4}\.\d{2}$")


def _parse_date_value(value: str) -> tuple[int, int] | None:
    if not value:
        return None
    if value == "至今":
        return (9999, 12)
    if not DATE_VALUE_PATTERN.fullmatch(value):
        raise ValueError("日期格式必须为 YYYY.MM 或 至今")

    year_str, month_str = value.split(".")
    year = int(year_str)
    month = int(month_str)
    if month < 1 or month > 12:
        raise ValueError("日期月份必须在 01 到 12 之间")
    return (year, month)


def _validate_date_range(start_date: str, end_date: str) -> None:
    start = _parse_date_value(start_date)
    end = _parse_date_value(end_date)
    if start and end and start > end:
        raise ValueError("开始日期不能晚于结束日期")


class BasicsSchema(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    location: str = ""
    summary: str = ""
    job_target: str = ""
    avatar_url: str | None = None


class EducationItemSchema(BaseModel):
    school: str = ""
    major: str = ""
    degree: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "EducationItemSchema":
        _validate_date_range(self.start_date, self.end_date)
        return self


class ExperienceItemSchema(BaseModel):
    company: str = ""
    role: str = ""
    department: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "ExperienceItemSchema":
        _validate_date_range(self.start_date, self.end_date)
        return self


class ProjectItemSchema(BaseModel):
    name: str = ""
    tech_stack: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectItemSchema":
        _validate_date_range(self.start_date, self.end_date)
        return self


class ResearchItemSchema(BaseModel):
    title: str = ""
    label: str = ""
    summary: str = ""


class HonorItemSchema(BaseModel):
    title: str = ""
    label: str = ""
    summary: str = ""


class ResumeContentSchema(BaseModel):
    basics: BasicsSchema = Field(default_factory=BasicsSchema)
    education: list[EducationItemSchema] = Field(default_factory=list)
    experience: list[ExperienceItemSchema] = Field(default_factory=list)
    projects: list[ProjectItemSchema] = Field(default_factory=list)
    research: list[ResearchItemSchema] = Field(default_factory=list)
    honors: list[HonorItemSchema] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class ResumeBaseSchema(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    template_id: str = Field(min_length=1, max_length=100)
    content: ResumeContentSchema = Field(default_factory=ResumeContentSchema)


class ResumeCreateSchema(ResumeBaseSchema):
    pass


class ResumeUpdateSchema(ResumeBaseSchema):
    pass


class ResumeReadSchema(ResumeBaseSchema):
    id: str
    rendered_pdf_url: str | None = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class TemplateSummarySchema(BaseModel):
    id: str
    name: str
    description: str
    accent_color: str
    font_family: str


class UploadResponseSchema(BaseModel):
    url: str
    filename: str


class RenderResponseSchema(BaseModel):
    message: str
    pdf_url: str


class ResumeListResponseSchema(BaseModel):
    items: list[ResumeReadSchema]
