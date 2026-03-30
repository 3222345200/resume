import re

from pydantic import BaseModel, Field, field_validator, model_validator


DATE_VALUE_PATTERN = re.compile(r"^\d{4}\.\d{2}$")

LAYOUT_SECTION_TITLE_SIZES = {"16", "18", "20"}
LAYOUT_CONTENT_FONT_SIZES = {"12.5", "13.5", "14.5"}
LAYOUT_CONTENT_LINE_HEIGHTS = {"1.28", "1.36", "1.5"}
LAYOUT_SECTION_DIVIDER_GAPS = {"2", "4", "6"}
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


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
    avatar_crop: dict[str, float] = Field(default_factory=lambda: {
        "scale": 1,
        "offset_x": 50,
        "offset_y": 50,
    })

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")

    @field_validator("avatar_crop", mode="before")
    @classmethod
    def normalize_avatar_crop(cls, value: object) -> dict[str, float]:
        default = {"scale": 1.0, "offset_x": 50.0, "offset_y": 50.0}
        if not isinstance(value, dict):
            return default

        def clamp(number: object, minimum: float, maximum: float, fallback: float) -> float:
            try:
                parsed = float(number)
            except (TypeError, ValueError):
                return fallback
            return max(minimum, min(maximum, parsed))

        return {
            "scale": clamp(value.get("scale"), 1.0, 3.0, default["scale"]),
            "offset_x": clamp(value.get("offset_x"), 0.0, 100.0, default["offset_x"]),
            "offset_y": clamp(value.get("offset_y"), 0.0, 100.0, default["offset_y"]),
        }


class LayoutSchema(BaseModel):
    section_title_size: str = "18"
    content_font_size: str = "13.5"
    content_line_height: str = "1.36"
    section_divider_gap: str = "4"
    font_color: str = "#111111"

    @field_validator("section_title_size", mode="before")
    @classmethod
    def normalize_section_title_size(cls, value: object) -> str:
        text = str(value or "").strip()
        return text if text in LAYOUT_SECTION_TITLE_SIZES else "18"

    @field_validator("content_font_size", mode="before")
    @classmethod
    def normalize_content_font_size(cls, value: object) -> str:
        text = str(value or "").strip()
        return text if text in LAYOUT_CONTENT_FONT_SIZES else "13.5"

    @field_validator("content_line_height", mode="before")
    @classmethod
    def normalize_content_line_height(cls, value: object) -> str:
        text = str(value or "").strip()
        return text if text in LAYOUT_CONTENT_LINE_HEIGHTS else "1.36"

    @field_validator("section_divider_gap", mode="before")
    @classmethod
    def normalize_section_divider_gap(cls, value: object) -> str:
        text = str(value or "").strip()
        return text if text in LAYOUT_SECTION_DIVIDER_GAPS else "4"

    @field_validator("font_color", mode="before")
    @classmethod
    def normalize_font_color(cls, value: object) -> str:
        text = str(value or "").strip()
        return text if HEX_COLOR_PATTERN.fullmatch(text) else "#111111"


class EducationItemSchema(BaseModel):
    school: str = ""
    major: str = ""
    degree: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: str = ""

    @field_validator("highlights", mode="before")
    @classmethod
    def normalize_highlights(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")

    @model_validator(mode="after")
    def validate_dates(self) -> "EducationItemSchema":
        _validate_date_range(self.start_date, self.end_date)
        return self


class ExperienceItemSchema(BaseModel):
    entry_type: str = "实习经历"
    company: str = ""
    role: str = ""
    department: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: str = ""

    @field_validator("entry_type", mode="before")
    @classmethod
    def normalize_entry_type(cls, value: object) -> str:
        text = str(value or "").strip()
        if text in {"实习经历", "工作经历"}:
            return text
        return "实习经历"

    @field_validator("highlights", mode="before")
    @classmethod
    def normalize_highlights(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")

    @model_validator(mode="after")
    def validate_dates(self) -> "ExperienceItemSchema":
        _validate_date_range(self.start_date, self.end_date)
        return self


class ProjectItemSchema(BaseModel):
    name: str = ""
    description: str = ""
    tech_stack: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: str = ""

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str:
        return str(value or "")

    @field_validator("tech_stack", mode="before")
    @classmethod
    def normalize_tech_stack(cls, value: object) -> str:
        return str(value or "")

    @field_validator("highlights", mode="before")
    @classmethod
    def normalize_highlights(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectItemSchema":
        if not self.description and self.tech_stack:
            self.description = self.tech_stack
        _validate_date_range(self.start_date, self.end_date)
        return self


class ResearchItemSchema(BaseModel):
    title: str = ""
    label: str = ""
    summary: str = ""

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")


class HonorItemSchema(BaseModel):
    title: str = ""
    label: str = ""
    summary: str = ""

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")


class PortfolioItemSchema(BaseModel):
    title: str = ""
    link: str = ""
    summary: str = ""

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")


class ResumeContentSchema(BaseModel):
    basics: BasicsSchema = Field(default_factory=BasicsSchema)
    layout: LayoutSchema = Field(default_factory=LayoutSchema)
    education: list[EducationItemSchema] = Field(default_factory=list)
    experience: list[ExperienceItemSchema] = Field(default_factory=list)
    projects: list[ProjectItemSchema] = Field(default_factory=list)
    portfolio: list[PortfolioItemSchema] = Field(default_factory=list)
    research: list[ResearchItemSchema] = Field(default_factory=list)
    honors: list[HonorItemSchema] = Field(default_factory=list)
    skills: str = ""

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, value: object) -> str:
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return str(value or "")


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
    resume: ResumeReadSchema | None = None


class ResumeListResponseSchema(BaseModel):
    items: list[ResumeReadSchema]
