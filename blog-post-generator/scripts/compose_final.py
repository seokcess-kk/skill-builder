"""
최종 블로그 게시물 조합 스크립트

Usage:
  python compose_final.py \
    --branded-dir output/keyword/branded/png \
    --seo-content output/keyword/seo/content/seo-content.md \
    --seo-images-dir output/keyword/seo/images \
    --output-dir output/keyword/final \
    --brand-name "바디핏한의원" \
    --keyword "웨스턴돔다이어트"

출력: {YYMMDD}_{브랜드명}_{키워드}.html
"""

import os
import re
import json
import html as html_lib
import base64
import argparse
from datetime import date
from pathlib import Path

from utils import FONT_PAIRINGS, font_link_tags, lighten_hex


def _sanitize_filename(name):
    """파일 시스템 금지 문자 제거"""
    return re.sub(r'[\\/:*?"<>|]', '', name)


def _md_to_html_inline(text):
    """마크다운 인라인 요소를 HTML로 변환 (escape 포함)

    1. **bold** 패턴을 추출하여 보존
    2. 나머지 텍스트는 html.escape 적용
    3. bold를 <strong>으로 치환
    """
    parts = re.split(r'(\*\*.+?\*\*)', text)
    result = []
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            inner = html_lib.escape(part[2:-2])
            result.append(f'<strong>{inner}</strong>')
        else:
            result.append(html_lib.escape(part))
    return ''.join(result)


def img_to_base64(img_path):
    """이미지 파일을 base64 data URI로 변환"""
    ext = os.path.splitext(img_path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
    mime_type = mime.get(ext.lstrip("."), "image/png")
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _convert_md_to_html_blocks(md_text, seo_images_dir=None):
    """마크다운 SEO 원고를 HTML 블록 리스트로 변환

    [IMAGE:] 마커를 이미지 태그로 치환하고, 마크다운을 HTML로 변환합니다.
    Returns: (html_blocks: list[str], img_count: int)
    """
    img_placeholders = {}
    _img_counter = [0]
    _seo_pngs = [None]

    def stash_image_marker(match):
        raw = match.group(1).strip()
        _img_counter[0] += 1
        idx = _img_counter[0]

        if "|" in raw:
            filename = raw.split("|")[0].strip()
            desc_part = raw.split("|", 1)[1].strip()
        else:
            filename = f"seo-img-{idx:02d}.png"
            desc_part = raw

        desc_match = re.match(r'\w+\s*-\s*(.+)', desc_part)
        alt_text = html_lib.escape(desc_match.group(1).strip()) if desc_match else filename
        key = f"__IMG_PLACEHOLDER_{len(img_placeholders)}__"

        img_found = False
        if seo_images_dir:
            if _seo_pngs[0] is None:
                if os.path.isdir(seo_images_dir):
                    _seo_pngs[0] = sorted(
                        f for f in os.listdir(seo_images_dir)
                        if f.endswith(".png") and f.startswith("seo-img")
                    )
                else:
                    _seo_pngs[0] = []

            for candidate in [filename, f"seo-img-{idx:02d}.png"]:
                img_path = os.path.abspath(os.path.join(seo_images_dir, candidate))
                if os.path.isfile(img_path):
                    data_uri = img_to_base64(img_path)
                    img_placeholders[key] = f'<p class="img-wrap seo-photo"><img src="{data_uri}" alt="{alt_text}" width="680"></p>'
                    img_found = True
                    break

            if not img_found:
                pngs = _seo_pngs[0]
                if idx <= len(pngs):
                    img_path = os.path.abspath(os.path.join(seo_images_dir, pngs[idx - 1]))
                    data_uri = img_to_base64(img_path)
                    img_placeholders[key] = f'<p class="img-wrap seo-photo"><img src="{data_uri}" alt="{alt_text}" width="680"></p>'
                    img_found = True

        if not img_found:
            img_placeholders[key] = f"<!-- 이미지 누락: {html_lib.escape(filename)} -->"

        return key

    content = re.sub(r'\[IMAGE:\s*([^\]]+)\]', stash_image_marker, md_text)

    blocks = re.split(r'\n{2,}', content.strip())
    html_blocks = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if block in img_placeholders:
            html_blocks.append(img_placeholders[block])
            continue

        h2_match = re.match(r'^##\s+(.+)$', block)
        if h2_match:
            html_blocks.append(f'<h2>{_md_to_html_inline(h2_match.group(1).strip())}</h2>')
            continue

        h3_match = re.match(r'^###\s+(.+)$', block)
        if h3_match:
            html_blocks.append(f'<h3>{_md_to_html_inline(h3_match.group(1).strip())}</h3>')
            continue

        lines = block.split('\n')
        if sum(1 for l in lines if l.strip().startswith('- ')) >= 2:
            items = []
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    items.append(f'<li>{_md_to_html_inline(line[2:])}</li>')
                elif line:
                    html_blocks.append(f'<p>{_md_to_html_inline(line)}</p>')
            if items:
                html_blocks.append('<ul>\n' + '\n'.join(items) + '\n</ul>')
            continue

        merged = ' '.join(l.strip() for l in lines if l.strip())
        merged = _md_to_html_inline(merged)

        has_placeholder = any(ph in merged for ph in img_placeholders)
        if has_placeholder:
            ph_pattern = '(' + '|'.join(re.escape(k) for k in img_placeholders) + ')'
            segments = re.split(ph_pattern, merged)
            for seg in segments:
                seg = seg.strip()
                if not seg:
                    continue
                if seg in img_placeholders:
                    html_blocks.append(img_placeholders[seg])
                else:
                    html_blocks.append(f'<p>{seg}</p>')
        else:
            html_blocks.append(f'<p>{merged}</p>')

    return html_blocks, len(img_placeholders)


def compose_seo_html(seo_content_path, seo_images_dir=None, output_path=None,
                     title="", primary_color="#333333", font_pairing="serif-classic"):
    """SEO 원고만 단독 HTML로 생성

    브랜드 이미지 없이 SEO 텍스트 + SEO 이미지만 포함된 HTML을 생성합니다.
    """
    if not seo_content_path or not os.path.isfile(seo_content_path):
        return None

    with open(seo_content_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    font_display, font_body = FONT_PAIRINGS.get(font_pairing, FONT_PAIRINGS["serif-classic"])
    _font_links_str = font_link_tags(font_pairing)
    border_color = lighten_hex(primary_color, 0.85)

    html_blocks, img_count = _convert_md_to_html_blocks(md_text, seo_images_dir)
    seo_body = '\n\n'.join(html_blocks)

    title_tag = f"<title>{html_lib.escape(title)}</title>" if title else ""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{title_tag}
{_font_links_str}
<style>
body {{
    max-width: 680px;
    margin: 0 auto;
    padding: 20px;
    font-family: {font_body}, 'Malgun Gothic', sans-serif;
    font-size: 16px;
    line-height: 1.9;
    color: #333;
    word-break: keep-all;
}}
img {{ max-width: 100%; height: auto; display: block; margin: 24px auto; }}
h2 {{ font-family: {font_display}; font-size: 21px; margin: 40px 0 16px; padding-bottom: 8px; color: {primary_color}; border-bottom: 1px solid {border_color}; }}
h3 {{ font-family: {font_display}; font-size: 18px; margin: 28px 0 12px; color: {primary_color}; }}
p {{ margin: 14px 0; }}
ul {{ margin: 14px 0; padding-left: 20px; }}
li {{ margin: 6px 0; line-height: 1.8; }}
strong {{ color: {primary_color}; }}
.img-wrap {{ text-align: center; margin: 28px 0; }}
.img-wrap.seo-photo img {{ border-radius: 8px; border: 1px solid {border_color}; }}
</style>
</head>
<body>
<article>
{seo_body}
</article>
</body>
</html>"""

    if not output_path:
        output_path = str(seo_content_path).replace(".md", ".html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  SEO HTML 생성: {output_path} (이미지 {img_count}개)")
    return output_path


def compose_post(branded_dir, seo_content_path, seo_images_dir, output_dir, brand_name, keyword):
    """브랜드 이미지 + SEO 텍스트 + SEO 이미지를 최종 게시물로 조합"""
    os.makedirs(output_dir, exist_ok=True)

    # 디자인 플랜 로드 (브랜드 컬러/폰트 적용 — 없으면 기본값 폴백)
    design_plan = None
    if branded_dir:
        plan_path = os.path.join(os.path.dirname(branded_dir), "html", "_design_plan.json")
        if os.path.isfile(plan_path):
            try:
                with open(plan_path, "r", encoding="utf-8") as f:
                    design_plan = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

    primary_color = design_plan.get("primary_color", "#333333") if design_plan else "#333333"
    accent_color = design_plan.get("accent_color", "#3B82F6") if design_plan else "#3B82F6"
    fp = design_plan.get("font_pairing", "serif-classic") if design_plan else "serif-classic"
    font_display, font_body = FONT_PAIRINGS.get(fp, FONT_PAIRINGS["serif-classic"])
    _font_links = font_link_tags(fp)
    border_color = lighten_hex(primary_color, 0.85)
    bridge_color = lighten_hex(primary_color, 0.7)

    parts = []
    disclaimer_html = ""

    # 1. 브랜드 이미지 섹션 (disclaimer 제외 — SEO 원고 하단에 배치)
    branded_count = 0
    if branded_dir and os.path.isdir(branded_dir):
        png_files = sorted(
            [f for f in os.listdir(branded_dir) if f.endswith(".png")]
        )
        if png_files:
            # 브랜드 섹션 파일명 → 의미 있는 alt 텍스트 매핑
            _section_alt = {
                "hook": "브랜드 훅 섹션",
                "intro": "브랜드 소개 섹션",
                "pain": "고객 고민 섹션",
                "bridge": "전환 섹션",
                "why": "원인 분석 섹션",
                "solution": "솔루션 섹션",
                "proof": "신뢰 근거 섹션",
                "cta": "상담 안내 섹션",
                "disclaimer": "면책 고지 섹션",
            }

            def _branded_alt(filename):
                name = filename.lower().replace(".png", "")
                for key, alt in _section_alt.items():
                    if key in name:
                        return f"{brand_name} {alt}"
                return f"{brand_name} 브랜드 이미지"

            parts.append("<!-- 브랜드 이미지 섹션 -->\n")
            for png in png_files:
                abs_path = os.path.abspath(os.path.join(branded_dir, png))
                data_uri = img_to_base64(abs_path)
                alt = html_lib.escape(_branded_alt(png))
                if "disclaimer" in png.lower():
                    disclaimer_html = f'<p class="img-wrap branded"><img src="{data_uri}" alt="{alt}" width="680"></p>\n'
                    continue
                parts.append(f'<p class="img-wrap branded"><img src="{data_uri}" alt="{alt}" width="680"></p>\n')
                branded_count += 1
            parts.append("\n")

    # 1-1. 브랜드 → SEO 시각적 브릿지
    if branded_count > 0:
        parts.append(f'<div style="text-align:center;margin:40px 0 32px;padding:0 40px;">'
                     f'<div style="height:1px;background:linear-gradient(90deg,transparent 0%,{bridge_color} 50%,transparent 100%);"></div>'
                     f'</div>\n')

    # 2. SEO 텍스트 + 이미지
    seo_img_count = 0
    if seo_content_path and os.path.isfile(seo_content_path):
        with open(seo_content_path, "r", encoding="utf-8") as f:
            seo_content = f.read()

        html_blocks, seo_img_count = _convert_md_to_html_blocks(seo_content, seo_images_dir)
        seo_html = '\n\n'.join(html_blocks)

        parts.append("<!-- SEO 텍스트 섹션 -->\n")
        parts.append(seo_html)

    # 2-1. Disclaimer 이미지를 SEO 원고 하단에 배치
    if disclaimer_html:
        parts.append("\n<!-- Disclaimer -->\n")
        parts.append(disclaimer_html)

    # 3. 최종 HTML 조합
    final_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{_font_links}
<style>
body {{
    max-width: 680px;
    margin: 0 auto;
    padding: 20px;
    font-family: {font_body}, 'Malgun Gothic', sans-serif;
    font-size: 16px;
    line-height: 1.9;
    color: #333;
    word-break: keep-all;
}}
img {{ max-width: 100%; height: auto; display: block; margin: 24px auto; }}
h2 {{ font-family: {font_display}; font-size: 21px; margin: 40px 0 16px; padding-bottom: 8px; color: {primary_color}; border-bottom: 1px solid {border_color}; }}
h3 {{ font-family: {font_display}; font-size: 18px; margin: 28px 0 12px; color: {primary_color}; }}
p {{ margin: 14px 0; }}
ul {{ margin: 14px 0; padding-left: 20px; }}
li {{ margin: 6px 0; line-height: 1.8; }}
strong {{ color: {primary_color}; }}
.img-wrap {{ text-align: center; margin: 28px 0; }}
.img-wrap.branded img {{ border-radius: 0; margin: 0 auto; }}
.img-wrap.seo-photo img {{ border-radius: 8px; border: 1px solid {border_color}; }}
</style>
</head>
<body>
<article>
{"".join(parts)}
</article>
</body>
</html>"""

    # 파일명: {YYMMDD}_{브랜드명}_{키워드}.html
    today = date.today().strftime("%y%m%d")
    filename = _sanitize_filename(f"{today}_{brand_name}_{keyword}") + ".html"
    html_path = os.path.join(output_dir, filename)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"최종 게시물 생성 완료:")
    print(f"  파일: {html_path}")
    print(f"  브랜드 이미지: {branded_count}개")
    print(f"  SEO 이미지: {seo_img_count}개")
    print(f"  Disclaimer: {'있음' if disclaimer_html else '없음'}")

    return html_path


def main():
    parser = argparse.ArgumentParser(description="최종 블로그 게시물 조합")
    parser.add_argument("--branded-dir", help="브랜드 이미지 PNG 디렉토리")
    parser.add_argument("--seo-content", required=True, help="SEO 텍스트 마크다운 파일")
    parser.add_argument("--seo-images-dir", help="SEO 생성 이미지 디렉토리")
    parser.add_argument("--output-dir", required=True, help="최종 출력 디렉토리")
    parser.add_argument("--brand-name", required=True, help="브랜드명")
    parser.add_argument("--keyword", required=True, help="타겟 키워드")
    parser.add_argument("--seo-only", action="store_true", help="SEO 콘텐츠만 단독 HTML로 생성")
    parser.add_argument("--title", default="", help="SEO HTML 제목 (--seo-only용)")
    parser.add_argument("--primary-color", default="#333333", help="Primary 색상 (--seo-only용)")
    parser.add_argument("--font-pairing", default="serif-classic", help="폰트 페어링 (--seo-only용)")
    args = parser.parse_args()

    if args.seo_only:
        compose_seo_html(
            args.seo_content, args.seo_images_dir,
            output_path=os.path.join(os.path.dirname(args.seo_content), "seo-content.html"),
            title=args.title, primary_color=args.primary_color, font_pairing=args.font_pairing,
        )
    else:
        compose_post(
            args.branded_dir, args.seo_content, args.seo_images_dir,
            args.output_dir, args.brand_name, args.keyword,
        )


if __name__ == "__main__":
    main()
