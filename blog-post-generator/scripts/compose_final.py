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
import html as html_lib
import base64
import argparse
from datetime import date
from pathlib import Path


def img_to_base64(img_path):
    """이미지 파일을 base64 data URI로 변환"""
    ext = os.path.splitext(img_path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
    mime_type = mime.get(ext.lstrip("."), "image/png")
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def compose_post(branded_dir, seo_content_path, seo_images_dir, output_dir, brand_name, keyword):
    """브랜드 이미지 + SEO 텍스트 + SEO 이미지를 최종 게시물로 조합"""
    os.makedirs(output_dir, exist_ok=True)

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
                    disclaimer_html = f'<p class="img-wrap"><img src="{data_uri}" alt="{alt}" width="680"></p>\n'
                    continue
                parts.append(f'<p class="img-wrap"><img src="{data_uri}" alt="{alt}" width="680"></p>\n')
                branded_count += 1
            parts.append("\n")

    # 2. SEO 텍스트 + 이미지
    seo_img_count = 0
    if seo_content_path and os.path.isfile(seo_content_path):
        with open(seo_content_path, "r", encoding="utf-8") as f:
            seo_content = f.read()

        # 이미지 마커를 플레이스홀더로 치환 (문단 파싱 전)
        # 마커 형식:
        #   [IMAGE: filename.png | type - description]
        #   [IMAGE: type - description]
        img_placeholders = {}
        _img_counter = [0]  # mutable counter for closure

        # build_prompts.py와 동일한 순번 로직: 모든 [IMAGE:] 마커를 등장 순서로 1-indexed
        # filename이 있든 없든 카운터는 항상 증가 (build_prompts.py의 enumerate와 동일)
        def stash_image_marker(match):
            raw = match.group(1).strip()
            _img_counter[0] += 1
            idx = _img_counter[0]

            # 형식 1: filename | type - description
            # 형식 2: type - description
            if "|" in raw:
                filename = raw.split("|")[0].strip()
                desc_part = raw.split("|", 1)[1].strip()
            else:
                filename = f"seo-img-{idx:02d}.png"
                desc_part = raw

            # description 추출 (type - description → description 부분)
            desc_match = re.match(r'\w+\s*-\s*(.+)', desc_part)
            alt_text = html_lib.escape(desc_match.group(1).strip()) if desc_match else filename

            key = f"__IMG_PLACEHOLDER_{len(img_placeholders)}__"

            # 이미지 파일 찾기 (여러 경로 시도)
            img_found = False
            if seo_images_dir:
                # seo-img PNG 목록은 한 번만 스캔
                if not hasattr(stash_image_marker, '_seo_pngs'):
                    if os.path.isdir(seo_images_dir):
                        stash_image_marker._seo_pngs = sorted(
                            f for f in os.listdir(seo_images_dir)
                            if f.endswith(".png") and f.startswith("seo-img")
                        )
                    else:
                        stash_image_marker._seo_pngs = []

                # 1. 정확한 파일명 매칭
                img_path = os.path.abspath(os.path.join(seo_images_dir, filename))
                if os.path.isfile(img_path):
                    data_uri = img_to_base64(img_path)
                    img_placeholders[key] = f'<p class="img-wrap"><img src="{data_uri}" alt="{alt_text}" width="680"></p>'
                    img_found = True
                else:
                    # 2. 순번 기반 매칭 (seo-img-01.png, seo-img-02.png ...)
                    fallback = f"seo-img-{idx:02d}.png"
                    img_path = os.path.abspath(os.path.join(seo_images_dir, fallback))
                    if os.path.isfile(img_path):
                        data_uri = img_to_base64(img_path)
                        img_placeholders[key] = f'<p class="img-wrap"><img src="{data_uri}" alt="{alt_text}" width="680"></p>'
                        img_found = True
                    else:
                        # 3. 디렉토리 내 PNG 순번 매칭
                        pngs = stash_image_marker._seo_pngs
                        if idx <= len(pngs):
                            img_path = os.path.abspath(os.path.join(seo_images_dir, pngs[idx - 1]))
                            data_uri = img_to_base64(img_path)
                            img_placeholders[key] = f'<p class="img-wrap"><img src="{data_uri}" alt="{alt_text}" width="680"></p>'
                            img_found = True

            if not img_found:
                img_placeholders[key] = f"<!-- 이미지 누락: {filename} (마커: {raw[:50]}) -->"

            return key

        content = re.sub(
            r'\[IMAGE:\s*([^\]]+)\]',
            stash_image_marker,
            seo_content,
        )
        seo_img_count = len(img_placeholders)

        # 마크다운 → HTML 블록 단위 변환
        blocks = re.split(r'\n{2,}', content.strip())
        html_blocks = []

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # 이미지 플레이스홀더 (독립 블록)
            if block in img_placeholders:
                html_blocks.append(img_placeholders[block])
                continue

            # H2 소제목
            h2_match = re.match(r'^##\s+(.+)$', block)
            if h2_match:
                title = h2_match.group(1).strip()
                title = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', title)
                html_blocks.append(f'<h2>{title}</h2>')
                continue

            # H3 소제목
            h3_match = re.match(r'^###\s+(.+)$', block)
            if h3_match:
                title = h3_match.group(1).strip()
                title = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', title)
                html_blocks.append(f'<h3>{title}</h3>')
                continue

            # 리스트 블록 (- 로 시작하는 줄이 2개 이상)
            lines = block.split('\n')
            if sum(1 for l in lines if l.strip().startswith('- ')) >= 2:
                items = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('- '):
                        item = line[2:]
                        item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
                        items.append(f'<li>{item}</li>')
                    elif line:
                        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                        html_blocks.append(f'<p>{line}</p>')
                if items:
                    html_blocks.append('<ul>\n' + '\n'.join(items) + '\n</ul>')
                continue

            # 일반 문단 — 이미지 플레이스홀더가 섞여 있으면 분리 처리
            merged = ' '.join(l.strip() for l in lines if l.strip())
            merged = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', merged)

            has_placeholder = any(ph in merged for ph in img_placeholders)
            if has_placeholder:
                # 플레이스홀더 기준으로 분할하여 텍스트/이미지를 올바른 태그로 분리
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
<style>
body {{
    max-width: 680px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Noto Sans CJK KR', 'Malgun Gothic', sans-serif;
    font-size: 16px;
    line-height: 1.9;
    color: #333;
    word-break: keep-all;
}}
img {{ max-width: 100%; height: auto; display: block; margin: 24px auto; border-radius: 4px; }}
h2 {{ font-size: 21px; margin: 40px 0 16px; padding-bottom: 8px; color: #111; border-bottom: 1px solid #eee; }}
h3 {{ font-size: 18px; margin: 28px 0 12px; color: #222; }}
p {{ margin: 14px 0; }}
ul {{ margin: 14px 0; padding-left: 20px; }}
li {{ margin: 6px 0; line-height: 1.8; }}
.img-wrap {{ text-align: center; margin: 28px 0; }}
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
    filename = f"{today}_{brand_name}_{keyword}.html"
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
    args = parser.parse_args()

    compose_post(
        args.branded_dir, args.seo_content, args.seo_images_dir,
        args.output_dir, args.brand_name, args.keyword,
    )


if __name__ == "__main__":
    main()
