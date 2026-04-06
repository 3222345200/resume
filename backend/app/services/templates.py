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
        "description": "左侧信息栏 + 右侧主内容，适合突出技能和个人信息。",
        "accent_color": "#0f766e",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "sidebar_resume",
    },
    {
        "id": "banded_resume",
        "name": "深色标题简历",
        "description": "每个模块标题使用深色背景条，视觉更强，适合项目经历丰富的简历。",
        "accent_color": "#1f2937",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "banded_resume",
    },
    {
        "id": "timeline_resume",
        "name": "时间轴简历",
        "description": "纵向时间线排版，适合经历连续、想突出成长路径的简历。",
        "accent_color": "#7c3aed",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "timeline_resume",
    },
    {
        "id": "minimal_resume",
        "name": "极简留白简历",
        "description": "更克制的黑白留白风格，适合正式、保守和高密度投递场景。",
        "accent_color": "#475569",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
        "template_dir": "minimal_resume",
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
