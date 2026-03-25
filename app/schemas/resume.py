from pydantic import BaseModel, Field


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


class ExperienceItemSchema(BaseModel):
    company: str = ""
    role: str = ""
    department: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)


class ProjectItemSchema(BaseModel):
    name: str = ""
    tech_stack: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)


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
    slug: str | None = Field(default=None, max_length=120)
    language: str = Field(default="zh-CN", max_length=20)
    status: str = Field(default="draft", max_length=30)
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
