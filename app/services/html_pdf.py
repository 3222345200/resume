from __future__ import annotations

import base64
import html
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models.resume import Resume

APP_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = APP_ROOT / "html_templates" / "pro_resume"
TEMPLATE_FILE = "resume.html.j2"
DEFAULT_AVATAR_CANDIDATES = [
    APP_ROOT.parent / "frontend" / "default-avatar.jpg",
    APP_ROOT / "latex_templates" / "pro_resume" / "default-avatar.jpg",
]
EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
]
RUNTIME_ROOT = Path(tempfile.gettempdir()) / "resume_runtime_pdf"
ALLOWED_RICH_TAGS = {"p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li", "a"}
BLOCKED_TAGS = {"script", "style"}


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
    cleaned = raw_path.lstrip("/").replace("/", "\\")
    for candidate in (Path(path_or_url), Path(cleaned), Path(".") / cleaned):
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


def _resolve_avatar_data_uri(avatar_url: str | None) -> str | None:
    source = _resolve_local_path(avatar_url)
    if source:
        return _file_to_data_uri(source)
    for fallback in DEFAULT_AVATAR_CANDIDATES:
        if fallback.exists():
            return _file_to_data_uri(fallback)
    return None


def _find_browser() -> Path:
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise RuntimeError("未找到可用的 Edge 或 Chrome 浏览器，无法生成 PDF。")


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
    skills = _visible_rich_text(content.get("skills"), list_mode=True)
    summary = _visible_rich_text(basics.get("summary"))

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
        },
        "education": education,
        "experience": experience,
        "projects": projects,
        "portfolio": portfolio,
        "research": research,
        "honors": honors,
        "skills": skills,
    }


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

        html_path.write_text(template.render(**_context_from_resume(resume)), encoding="utf-8")

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
            raise RuntimeError("HTML 已生成，但 PDF 文件未输出。")
        return pdf_path.read_bytes()
