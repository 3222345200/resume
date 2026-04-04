TEMPLATE_ID = "pro_resume"
LEGACY_TEMPLATE_IDS = {"neu_resume"}


def normalize_template_id(template_id: str | None) -> str:
    if not template_id or template_id in LEGACY_TEMPLATE_IDS:
        return TEMPLATE_ID
    return template_id


TEMPLATES = [
    {
        "id": TEMPLATE_ID,
        "name": "专业简历模板",
        "description": "简洁职业风格，支持中文教育、技能、实习、项目、科研与荣誉内容。",
        "accent_color": "#155eef",
        "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
    }
]
