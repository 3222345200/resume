DEFAULT_TEMPLATE_ID = "pro_resume"
LEGACY_TEMPLATE_IDS = {"neu_resume"}


TEMPLATES = [
    {
        "id": DEFAULT_TEMPLATE_ID,
        "name": "专业简历",
        "description": "经典单栏排版，适合校招、实习和通用投递场景。",
        "accent_color": "#155eef",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "pro_resume",
    },
    {
        "id": "sidebar_resume",
        "name": "侧栏简历",
        "description": "左侧信息栏加右侧正文内容，适合突出技能和个人信息。",
        "accent_color": "#0f766e",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "sidebar_resume",
    },
    {
        "id": "banded_resume",
        "name": "深色标题简历",
        "description": "模块标题使用深色横条，适合项目经历丰富的简历。",
        "accent_color": "#1f2937",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "banded_resume",
    },
    {
        "id": "timeline_resume",
        "name": "时间轴简历",
        "description": "纵向时间线排版，适合强调成长路径和连续经历。",
        "accent_color": "#7c3aed",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "timeline_resume",
    },
    {
        "id": "minimal_resume",
        "name": "极简留白简历",
        "description": "克制留白风格，适合正式、保守和高密度投递场景。",
        "accent_color": "#475569",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "minimal_resume",
    },
    {
        "id": "infographic_resume",
        "name": "信息图简历",
        "description": "强调技能条、数据卡和视觉模块，适合创意岗与产品展示型投递。",
        "accent_color": "#7c3aed",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "infographic_resume",
    },
    {
        "id": "character_resume",
        "name": "人物档案简历",
        "description": "头像卡片与标签化信息并重，更适合内容、品牌、设计和校园展示。",
        "accent_color": "#0f766e",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "modern_panel_resume",
    },
    {
        "id": "editorial_resume",
        "name": "编辑杂志简历",
        "description": "更强调编排感、头图氛围和内容层次，适合视觉与传播类岗位。",
        "accent_color": "#1f2937",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "editorial_resume",
    },
    {
        "id": "swiss_resume",
        "name": "瑞士网格简历",
        "description": "强网格、细线与秩序留白，适合设计导向但仍注重可读性的岗位。",
        "accent_color": "#2563eb",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "compact_resume",
    },
    {
        "id": "harvard_resume",
        "name": "Harvard ATS 简历",
        "description": "学院派、克制、投递友好，优先服务校招、实习与 ATS 筛选场景。",
        "accent_color": "#111827",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "academic_resume",
    },
]

TEMPLATE_MAP = {template["id"]: template for template in TEMPLATES}


def normalize_template_id(template_id: str | None) -> str:
    normalized = str(template_id or "").strip()
    if not normalized or normalized in LEGACY_TEMPLATE_IDS or normalized not in TEMPLATE_MAP:
        return DEFAULT_TEMPLATE_ID
    return normalized


def get_template_definition(template_id: str | None) -> dict[str, str]:
    normalized = normalize_template_id(template_id)
    return TEMPLATE_MAP[normalized]
