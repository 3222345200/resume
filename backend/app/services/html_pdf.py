from __future__ import annotations

import base64
import html
import os
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models.resume import Resume
from app.services.minio_storage import load_object_bytes

APP_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_ROOT.parent.parent
TEMPLATE_ROOT = APP_ROOT / "html_templates" / "pro_resume"
TEMPLATE_FILE = "resume.html.j2"
DEFAULT_AVATAR_CANDIDATES = [
    PROJECT_ROOT / "frontend" / "src" / "assets" / "default-avatar.jpg",
]
BROWSER_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path("/usr/bin/google-chrome"),
    Path("/usr/bin/chromium"),
    Path("/usr/bin/chromium-browser"),
    Path("/usr/bin/microsoft-edge"),
]
RUNTIME_ROOT = Path(tempfile.gettempdir()) / "resume_runtime_pdf"
ALLOWED_RICH_TAGS = {"p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li", "a"}
BLOCKED_TAGS = {"script", "style"}

DEFAULT_LAYOUT = {
    "section_title_size": "18px",
    "content_font_size": "13.5px",
    "content_line_height": "1.36",
    "section_divider_gap": "4px",
    "section_title_font_family": "\"FangSong\", \"STFangsong\", \"FangSong_GB2312\", serif",
    "content_font_family": "\"KaiTi\", \"STKaiti\", \"Kaiti SC\", serif",
    "font_family": "\"KaiTi\", \"STKaiti\", \"Kaiti SC\", serif",
    "section_title_color": "#111111",
    "content_font_color": "#111111",
    "font_color": "#111111",
}
SECTION_TITLE_SIZE_OPTIONS = {"14", "15", "16", "17", "18", "19", "20", "21", "22", "24", "26", "28"}
CONTENT_FONT_SIZE_OPTIONS = {"10", "10.5", "11", "11.5", "12", "12.5", "13", "13.5", "14", "14.5", "15", "16", "17", "18"}
CONTENT_LINE_HEIGHT_OPTIONS = {"1.0", "1.1", "1.15", "1.2", "1.25", "1.3", "1.36", "1.4", "1.45", "1.5", "1.6", "1.75", "2.0"}
SECTION_DIVIDER_GAP_OPTIONS = {"0", "1", "2", "3", "4", "5", "6", "8", "10", "12", "14", "16"}
FONT_FAMILY_OPTIONS = {
    "songti": "\"SimSun\", \"Songti SC\", \"STSong\", serif",
    "fangsong": "\"FangSong\", \"STFangsong\", \"FangSong_GB2312\", serif",
    "kaiti": "\"KaiTi\", \"STKaiti\", \"Kaiti SC\", serif",
    "heiti": "\"SimHei\", \"Microsoft YaHei\", \"Noto Sans SC\", sans-serif",
}
MOVABLE_SECTION_ORDER = ("skills", "experience", "projects", "portfolio", "research", "honors")
CUSTOM_SECTION_PREFIX = "custom:"


class RichTextSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.block_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in BLOCKED_TAGS:
            self.block_depth += 1
            return
        if self.block_depth == 0 and tag in ALLOWED_RICH_TAGS:
            if tag == "a":
                href = ""
                for key, value in attrs:
                    if key.lower() == "href" and value:
                        href = value.strip()
                        break
                if href.startswith(("http://", "https://", "mailto:")):
                    safe_href = html.escape(href, quote=True)
                    self.parts.append(f'<a href="{safe_href}">')
                else:
                    self.parts.append("<a>")
                return
            self.parts.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in BLOCKED_TAGS:
            self.block_depth = max(0, self.block_depth - 1)
            return
        if self.block_depth == 0 and tag in ALLOWED_RICH_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.block_depth == 0 and tag.lower() == "br":
            self.parts.append("<br>")

    def handle_data(self, data: str) -> None:
        if self.block_depth == 0:
            self.parts.append(html.escape(data))

    def get_html(self) -> str:
        return "".join(self.parts).strip()


def sanitize_rich_text(value: object, *, list_mode: bool = False) -> str:
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        if not items:
            return ""
        if list_mode:
            return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"
        return "".join(f"<p>{html.escape(item)}</p>" for item in items)

    text = str(value or "").strip()
    if not text:
        return ""

    if "<" not in text and ">" not in text:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""
        if list_mode:
            return "<ul>" + "".join(f"<li>{html.escape(line)}</li>" for line in lines) + "</ul>"
        return "".join(f"<p>{html.escape(line)}</p>" for line in lines)

    sanitizer = RichTextSanitizer()
    sanitizer.feed(text)
    sanitizer.close()
    return sanitizer.get_html()


def plain_text(value: object) -> str:
    return str(value or "").strip()


def date_label(value: object) -> str:
    text = plain_text(value)
    if not text:
        return ""
    if text == "至今":
        return text
    parts = text.split(".")
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        return f"{parts[0]}.{parts[1]}"
    return text


def _has_visible_text(value: object) -> bool:
    if isinstance(value, list):
        return any(_has_visible_text(item) for item in value)
    text = str(value or "").strip()
    if not text:
        return False
    sanitized = sanitize_rich_text(text)
    plain = sanitized.replace("<br>", "").replace("&nbsp;", " ")
    plain = plain.replace("<p>", "").replace("</p>", "").replace("<ul>", "").replace("</ul>", "")
    plain = plain.replace("<ol>", "").replace("</ol>", "").replace("<li>", "").replace("</li>", "")
    plain = plain.replace("<strong>", "").replace("</strong>", "").replace("<b>", "").replace("</b>", "")
    plain = plain.replace("<em>", "").replace("</em>", "").replace("<i>", "").replace("</i>", "")
    plain = plain.replace("<u>", "").replace("</u>", "").replace("<a>", "").replace("</a>", "")
    return bool(plain.strip())


def _compact_entry(entry: dict[str, object]) -> dict[str, object] | None:
    if any(_has_visible_text(value) for value in entry.values()):
        return entry
    return None


def _visible_rich_text(value: object, *, list_mode: bool = False) -> str:
    rendered = sanitize_rich_text(value, list_mode=list_mode)
    return rendered if _has_visible_text(rendered) else ""


def _normalize_hex_color(value: str, fallback: str) -> str:
    return value if len(value) == 7 and value.startswith("#") and all(ch in "0123456789abcdefABCDEF" for ch in value[1:]) else fallback


def _layout_context(raw_layout: object) -> dict[str, str]:
    layout = raw_layout if isinstance(raw_layout, dict) else {}
    section_title_size = str(layout.get("section_title_size") or "18").strip()
    content_font_size = str(layout.get("content_font_size") or "13.5").strip()
    content_line_height = str(layout.get("content_line_height") or "1.36").strip()
    section_divider_gap = str(layout.get("section_divider_gap") or "4").strip()
    fallback_font_family_key = str(layout.get("font_family") or "kaiti").strip()
    section_title_font_family_key = str(layout.get("section_title_font_family") or fallback_font_family_key or "fangsong").strip()
    content_font_family_key = str(layout.get("content_font_family") or fallback_font_family_key or "kaiti").strip()
    fallback_color = str(layout.get("font_color") or "#111111").strip()
    section_title_color = str(layout.get("section_title_color") or fallback_color or "#111111").strip()
    content_font_color = str(layout.get("content_font_color") or fallback_color or "#111111").strip()

    return {
        "section_title_size": f"{section_title_size if section_title_size in SECTION_TITLE_SIZE_OPTIONS else '18'}px",
        "content_font_size": f"{content_font_size if content_font_size in CONTENT_FONT_SIZE_OPTIONS else '13.5'}px",
        "content_line_height": content_line_height if content_line_height in CONTENT_LINE_HEIGHT_OPTIONS else "1.36",
        "section_divider_gap": f"{section_divider_gap if section_divider_gap in SECTION_DIVIDER_GAP_OPTIONS else '4'}px",
        "section_title_font_family": FONT_FAMILY_OPTIONS.get(section_title_font_family_key, DEFAULT_LAYOUT["section_title_font_family"]),
        "content_font_family": FONT_FAMILY_OPTIONS.get(content_font_family_key, DEFAULT_LAYOUT["content_font_family"]),
        "font_family": FONT_FAMILY_OPTIONS.get(fallback_font_family_key, DEFAULT_LAYOUT["font_family"]),
        "section_title_color": _normalize_hex_color(section_title_color, DEFAULT_LAYOUT["section_title_color"]),
        "content_font_color": _normalize_hex_color(content_font_color, DEFAULT_LAYOUT["content_font_color"]),
        "font_color": _normalize_hex_color(fallback_color, DEFAULT_LAYOUT["font_color"]),
    }


def _build_environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_ROOT)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["rich"] = sanitize_rich_text
    env.filters["text"] = plain_text
    env.filters["date_label"] = date_label
    return env


def _resolve_local_path(path_or_url: str | None) -> Path | None:
    if not path_or_url:
        return None

    parsed = urlparse(path_or_url)
    raw_path = parsed.path or path_or_url

    candidates = [
        Path(path_or_url),
        Path(raw_path),
        Path(".") / raw_path.lstrip("/"),
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _file_to_data_uri(path: Path) -> str:
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "application/octet-stream")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _bytes_to_data_uri(data: bytes, filename: str) -> str:
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(Path(filename).suffix.lower(), "application/octet-stream")
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _avatar_data_uri_from_storage_url(avatar_url: str | None) -> str | None:
    if not avatar_url:
        return None
    path = urlparse(avatar_url).path or avatar_url
    marker = "/api/uploads/avatar/"
    if marker not in path:
        return None
    storage_path = path.split(marker, 1)[1].lstrip("/")
    if "/" not in storage_path:
        return None
    bucket_name, object_name = storage_path.split("/", 1)
    data = load_object_bytes(unquote(object_name), bucket_name=unquote(bucket_name))
    if not data:
        return None
    return _bytes_to_data_uri(data, object_name)


def _resolve_avatar_data_uri(avatar_url: str | None) -> str | None:
    storage_data_uri = _avatar_data_uri_from_storage_url(avatar_url)
    if storage_data_uri:
        return storage_data_uri
    source = _resolve_local_path(avatar_url)
    if source:
        return _file_to_data_uri(source)
    for fallback in DEFAULT_AVATAR_CANDIDATES:
        if fallback.exists():
            return _file_to_data_uri(fallback)
    return None


def _normalize_avatar_crop(value: object) -> dict[str, float]:
    crop = value if isinstance(value, dict) else {}

    def clamp(number: object, minimum: float, maximum: float, fallback: float) -> float:
        try:
            parsed = float(number)
        except (TypeError, ValueError):
            return fallback
        return max(minimum, min(maximum, parsed))

    return {
        "scale": clamp(crop.get("scale"), 1.0, 3.0, 1.0),
        "offset_x": clamp(crop.get("offset_x"), 0.0, 100.0, 50.0),
        "offset_y": clamp(crop.get("offset_y"), 0.0, 100.0, 50.0),
    }


def _find_browser() -> Path:
    env_browser = os.getenv("CHROME_BIN") or os.getenv("BROWSER_PATH")
    if env_browser:
        candidate = Path(env_browser)
        if candidate.exists():
            return candidate

    for command in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        resolved = shutil.which(command)
        if resolved:
            return Path(resolved)

    for candidate in BROWSER_CANDIDATES:
        if candidate.exists():
            return candidate

    raise RuntimeError("未找到可用的浏览器（Chrome / Chromium / Edge），无法生成 PDF。")


def _context_from_resume(resume: Resume) -> dict[str, object]:
    content = resume.content or {}
    basics = content.get("basics", {})
    education = [
        item
        for item in (
            _compact_entry(
                {
                    "school": plain_text(raw.get("school")),
                    "major": plain_text(raw.get("major")),
                    "degree": plain_text(raw.get("degree")),
                    "start_date": date_label(raw.get("start_date")),
                    "end_date": date_label(raw.get("end_date")),
                    "highlights": _visible_rich_text(raw.get("highlights"), list_mode=True),
                }
            )
            for raw in content.get("education", [])
        )
        if item
    ]
    experience = [
        item
        for item in (
            _compact_entry(
                {
                    "entry_type": plain_text(raw.get("entry_type")) or "实习经历",
                    "company": plain_text(raw.get("company")),
                    "role": plain_text(raw.get("role")),
                    "department": plain_text(raw.get("department")),
                    "location": plain_text(raw.get("location")),
                    "start_date": date_label(raw.get("start_date")),
                    "end_date": date_label(raw.get("end_date")),
                    "highlights": _visible_rich_text(raw.get("highlights"), list_mode=True),
                }
            )
            for raw in content.get("experience", [])
        )
        if item
    ]
    projects = [
        item
        for item in (
            _compact_entry(
                {
                    "name": plain_text(raw.get("name")),
                    "description": plain_text(raw.get("description") or raw.get("tech_stack")),
                    "start_date": date_label(raw.get("start_date")),
                    "end_date": date_label(raw.get("end_date")),
                    "highlights": _visible_rich_text(raw.get("highlights"), list_mode=True),
                }
            )
            for raw in content.get("projects", [])
        )
        if item
    ]
    portfolio = [
        item
        for item in (
            _compact_entry(
                {
                    "title": plain_text(raw.get("title")),
                    "link": plain_text(raw.get("link")),
                    "summary": _visible_rich_text(raw.get("summary")),
                }
            )
            for raw in content.get("portfolio", [])
        )
        if item
    ]
    research = [
        item
        for item in (
            _compact_entry(
                {
                    "title": plain_text(raw.get("title")),
                    "label": plain_text(raw.get("label")),
                    "summary": _visible_rich_text(raw.get("summary")),
                }
            )
            for raw in content.get("research", [])
        )
        if item
    ]
    honors = [
        item
        for item in (
            _compact_entry(
                {
                    "title": plain_text(raw.get("title")),
                    "label": plain_text(raw.get("label")),
                    "summary": _visible_rich_text(raw.get("summary")),
                }
            )
            for raw in content.get("honors", [])
        )
        if item
    ]
    custom_sections = []
    for index, raw_section in enumerate(content.get("custom_sections", []), start=1):
        section_id = plain_text(raw_section.get("id")) or f"section-{index}"
        title = plain_text(raw_section.get("title")) or "自定义模块"
        items = [
            item
            for item in (
                _compact_entry(
                    {
                        "title": plain_text(raw.get("title")),
                        "subtitle": plain_text(raw.get("subtitle")),
                        "start_date": date_label(raw.get("start_date")),
                        "end_date": date_label(raw.get("end_date")),
                        "description": _visible_rich_text(raw.get("description")),
                        "highlights": _visible_rich_text(raw.get("highlights"), list_mode=True),
                    }
                )
                for raw in raw_section.get("items", [])
            )
            if item
        ]
        custom_sections.append(
            {
                "key": f"{CUSTOM_SECTION_PREFIX}{section_id}",
                "title": title,
                "items": items,
                "kind": "custom",
            }
        )
    skills = _visible_rich_text(content.get("skills"), list_mode=True)
    summary = _visible_rich_text(basics.get("summary"))
    layout = _layout_context(content.get("layout"))

    custom_section_keys = [section["key"] for section in custom_sections]
    allowed_keys = list(MOVABLE_SECTION_ORDER) + custom_section_keys
    requested_order = content.get("section_order") if isinstance(content.get("section_order"), list) else []
    normalized_order: list[str] = []
    for key in requested_order:
        text = str(key or "").strip()
        if text in allowed_keys and text not in normalized_order:
            normalized_order.append(text)
    for key in allowed_keys:
        if key not in normalized_order:
            normalized_order.append(key)

    section_map = {
        "skills": {"key": "skills", "title": "专业技能", "content": skills},
        "experience": {"key": "experience", "title": "工作 / 实习经历", "items": experience},
        "projects": {"key": "projects", "title": "项目经历", "items": projects},
        "portfolio": {"key": "portfolio", "title": "作品集", "items": portfolio},
        "research": {"key": "research", "title": "科研经历", "items": research},
        "honors": {"key": "honors", "title": "荣誉奖项", "items": honors},
    }
    section_map.update({section["key"]: section for section in custom_sections})

    ordered_sections = []
    for key in normalized_order:
        section = section_map.get(key)
        if not section:
            continue
        if section.get("content") or section.get("items"):
            ordered_sections.append(section)

    return {
        "title": resume.title,
        "basics": {
            "name": plain_text(basics.get("name")),
            "phone": plain_text(basics.get("phone")),
            "email": plain_text(basics.get("email")),
            "location": plain_text(basics.get("location")),
            "job_target": plain_text(basics.get("job_target")),
            "summary": summary,
            "avatar_data_uri": _resolve_avatar_data_uri(basics.get("avatar_url")),
            "avatar_crop": _normalize_avatar_crop(basics.get("avatar_crop")),
        },
        "layout": layout,
        "education": education,
        "ordered_sections": ordered_sections,
    }

def get_resume_template_signature() -> str:
    template_path = TEMPLATE_ROOT / TEMPLATE_FILE
    template_stat = template_path.stat()
    return f"{template_stat.st_mtime_ns}:{template_stat.st_size}"


def render_resume_html(resume: Resume) -> str:
    env = _build_environment()
    template = env.get_template(TEMPLATE_FILE)
    return template.render(**_context_from_resume(resume))

def render_resume_pdf(resume: Resume) -> bytes:
    browser_path = _find_browser()
    env = _build_environment()
    template = env.get_template(TEMPLATE_FILE)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"resume-{resume.id}-", dir=RUNTIME_ROOT) as temp_dir:
        workspace = Path(temp_dir)
        html_path = workspace / "resume.html"
        pdf_path = workspace / "resume.pdf"
        profile_path = workspace / "edge-profile"
        profile_path.mkdir(parents=True, exist_ok=True)

        html_path.write_text(render_resume_html(resume), encoding="utf-8")

        command = [
            str(browser_path),
            "--headless=new",
            "--disable-gpu",
            "--disable-crash-reporter",
            "--disable-crashpad",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-sandbox",
            "--allow-file-access-from-files",
            f"--user-data-dir={profile_path}",
            f"--print-to-pdf={pdf_path}",
            "--print-to-pdf-no-header",
            html_path.resolve().as_uri(),
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "HTML to PDF generation failed").strip())

        if not pdf_path.exists():
            raise RuntimeError("HTML 转 PDF 失败，未生成 PDF 文件。")
        return pdf_path.read_bytes()
