from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

from app.models.resume import Resume

APP_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = APP_ROOT / 'latex_templates' / 'pro_resume'
TEMPLATE_FILE = 'resume_template.tex.j2'
DEFAULT_AVATAR = 'default-avatar.jpg'


def latex_escape(value: object) -> str:
    text = str(value or '')
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.replace('\n', ' ')


def format_leading_label(value: object) -> str:
    text = str(value or '').strip()
    if not text:
        return ''

    for delimiter in ('：', ':'):
        if delimiter in text:
            prefix, suffix = text.split(delimiter, 1)
            prefix = prefix.strip()
            suffix = suffix.strip()
            if prefix and suffix:
                return f"\\textbf{{{latex_escape(prefix)}}}{latex_escape(delimiter)} {latex_escape(suffix)}"
    return latex_escape(text)


def _build_environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_ROOT)),
        autoescape=False,
        block_start_string='\\BLOCK{',
        block_end_string='}',
        variable_start_string='\\VAR{',
        variable_end_string='}',
        comment_start_string='\\#{',
        comment_end_string='}',
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters['latex'] = latex_escape
    env.filters['label_bold'] = format_leading_label
    return env


def _resolve_avatar_source(avatar_url: str | None) -> Path | None:
    if not avatar_url:
        return None
    parsed = urlparse(avatar_url)
    path = parsed.path or avatar_url
    cleaned = path.lstrip('/').replace('/', '\\')
    candidate = Path(cleaned)
    if candidate.exists():
        return candidate
    local_candidate = Path('.') / cleaned
    if local_candidate.exists():
        return local_candidate
    return None


def _prepare_avatar(output_dir: Path, avatar_url: str | None) -> str:
    source = _resolve_avatar_source(avatar_url)
    if source and source.exists():
        ext = source.suffix or '.jpg'
        target_name = f'avatar{ext.lower()}'
        shutil.copy2(source, output_dir / target_name)
        return target_name
    return DEFAULT_AVATAR


def _context_from_resume(resume: Resume, output_dir: Path) -> dict:
    content = resume.content or {}
    basics = content.get('basics', {})
    avatar_path = _prepare_avatar(output_dir, basics.get('avatar_url'))
    return {
        'title': resume.title,
        'basics': basics,
        'avatar_path': avatar_path,
        'education': content.get('education', []),
        'experience': content.get('experience', []),
        'projects': content.get('projects', []),
        'research': content.get('research', []),
        'honors': content.get('honors', []),
        'skills': content.get('skills', []),
    }


def render_resume_pdf(resume: Resume) -> bytes:
    with tempfile.TemporaryDirectory(prefix=f'resume-{resume.id}-') as temp_dir:
        output_dir = Path(temp_dir) / 'workspace'
        shutil.copytree(TEMPLATE_ROOT, output_dir)

        env = _build_environment()
        template = env.get_template(TEMPLATE_FILE)
        tex_content = template.render(**_context_from_resume(resume, output_dir))

        tex_path = output_dir / 'resume.tex'
        tex_path.write_text(tex_content, encoding='utf-8')

        command = [
            'xelatex',
            '-interaction=nonstopmode',
            '-halt-on-error',
            str(tex_path.name),
        ]

        result = subprocess.run(
            command,
            cwd=output_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        if result.returncode != 0:
            log_path = output_dir / 'resume.log'
            log_content = ''
            if log_path.exists():
                log_content = log_path.read_text(encoding='utf-8', errors='ignore')[-4000:]
            error_text = log_content or result.stderr or result.stdout or 'LaTeX compilation failed'
            if 'fresh TeX installation' in error_text or 'finish the setup before proceeding' in error_text:
                raise RuntimeError(
                    'MiKTeX 尚未完成初始化，请先打开 MiKTeX Console 完成首次设置，'
                    '或在命令行先手动执行一次 xelatex 完成安装。'
                )
            raise RuntimeError(error_text)

        pdf_path = output_dir / 'resume.pdf'
        if not pdf_path.exists():
            raise RuntimeError('PDF generation failed')
        return pdf_path.read_bytes()
