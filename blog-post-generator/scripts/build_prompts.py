"""
SEO 텍스트의 이미지 마커에서 Gemini 프롬프트를 생성하는 스크립트

Phase 2(insert_image_markers.py)에서 삽입된 [IMAGE: ...] 마커를 추출하고,
Claude가 작성한 이미지 프롬프트를 그대로 활용하여
generate_images.py가 사용할 prompts.json을 생성합니다.

고정 템플릿 없이 Claude의 창의적 프롬프트를 존중하되,
텍스트 삽입 방지(no-text) 규칙만 적용합니다.

Usage:
  python build_prompts.py \
    --seo-content output/keyword/content/seo-content.md \
    --output-dir output/keyword/images/ \
    --keyword "일산다이어트한의원"

Input 마커 포맷:
  [IMAGE: {filename} | {type} - {description}]
  [IMAGE: {type} - {description}]

Output: prompts.json (generate_images.py 입력용)
"""

import os
import re
import json
import argparse


# 유형별 기본 비율 매핑
TYPE_ASPECT_RATIOS = {
    "real_photo": "4:3",
    "facility_photo": "16:9",
    "product_photo": "1:1",
    "illustration": "4:3",
    "infographic": "3:4",
    "lifestyle_photo": "4:3",
    "concept_comparison": "4:3",
    "mood_photo": "16:9",
}


# 텍스트/숫자를 암시하는 표현 → 시각적 대체어 매핑 (안전망)
# Claude가 이미 영문 프롬프트를 작성하지만, 혹시 텍스트 암시 표현이 남아있을 경우 대체
_TEXT_IMPLYING_PATTERNS = [
    (re.compile(r'\bsteps?\s*\d+', re.IGNORECASE), "sequential icon flow"),
    (re.compile(r'\bcomparison\s+chart\b', re.IGNORECASE), "visual contrast between two elements"),
    (re.compile(r'\bdata\s+table\b', re.IGNORECASE), "graphical visualization"),
    (re.compile(r'\bwith\s+(text|labels?|captions?|titles?|numbers?|digits?)\b', re.IGNORECASE), "with visual elements"),
    (re.compile(r'\blabeled\b', re.IGNORECASE), "marked with icons"),
    (re.compile(r'\bnumbered\b', re.IGNORECASE), "sequentially arranged"),
]


def parse_image_markers(content):
    """SEO 콘텐츠에서 이미지 마커를 순서대로 추출합니다.

    지원 포맷:
      [IMAGE: filename.png | type - description]
      [IMAGE: type - description]

    순서 기반 번호 부여 — compose_final.py와 동일한 카운터 로직.
    """
    markers = []

    # 모든 [IMAGE: ...] 마커를 등장 순서대로 찾기
    all_pattern = re.compile(r'\[IMAGE:\s*([^\]]+)\]')
    # 포맷 1 판별: filename | type - description
    fmt1_pattern = re.compile(r'^(.+?)\s*\|\s*(\w+)\s*-\s*(.+)$')
    # 포맷 2 판별: type - description
    fmt2_pattern = re.compile(r'^(\w+)\s*-\s*(.+)$')

    for i, match in enumerate(all_pattern.finditer(content), start=1):
        raw = match.group(1).strip()

        m1 = fmt1_pattern.match(raw)
        if m1:
            markers.append({
                "filename": m1.group(1).strip(),
                "type": m1.group(2).strip(),
                "description": m1.group(3).strip(),
            })
            continue

        m2 = fmt2_pattern.match(raw)
        if m2:
            markers.append({
                "filename": f"seo-img-{i:02d}.png",
                "type": m2.group(1).strip(),
                "description": m2.group(2).strip(),
            })
            continue

        # 어느 포맷도 안 맞으면 기본값
        markers.append({
            "filename": f"seo-img-{i:02d}.png",
            "type": "real_photo",
            "description": raw,
        })

    return markers


def _sanitize_description(description):
    """프롬프트에서 텍스트 암시 표현을 시각적 표현으로 대체합니다 (안전망)."""
    sanitized = description
    for pattern, replacement in _TEXT_IMPLYING_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def build_prompt(marker, brand_color=None):
    """이미지 마커에서 Gemini 프롬프트를 생성합니다.

    Claude가 Phase 2에서 작성한 창의적 프롬프트를 그대로 활용하고,
    텍스트 삽입 방지 규칙만 앞뒤로 추가합니다.
    """
    img_type = marker["type"]
    description = _sanitize_description(marker["description"])
    aspect_ratio = TYPE_ASPECT_RATIOS.get(img_type, "4:3")

    # no-text 접두사
    prompt = (
        "IMPORTANT: Generate a purely visual image with ZERO text of any kind. "
        "Do not render any letters, words, numbers, labels, captions, watermarks, "
        "or typographic elements anywhere in the image. "
    )

    # Claude가 작성한 프롬프트를 그대로 사용
    prompt += description

    # 브랜드 컬러 힌트
    if brand_color:
        prompt += f", accent color {brand_color} used subtly in the composition"

    # no-text 접미사 (이중 강조)
    prompt += (
        ". The image must contain absolutely no text, no words, no letters, "
        "no numbers, no labels, no watermarks, no signatures, no captions, "
        "no Korean characters, no English characters, no writing of any kind."
    )

    return {
        "id": marker["filename"].replace(".png", ""),
        "type": img_type,
        "prompt": prompt,
        "filename": marker["filename"],
        "aspect_ratio": aspect_ratio,
    }


def main():
    parser = argparse.ArgumentParser(description="이미지 마커에서 Gemini 프롬프트 생성")
    parser.add_argument("--seo-content", required=True, help="SEO 콘텐츠 마크다운 파일")
    parser.add_argument("--output-dir", required=True, help="prompts.json 출력 디렉토리")
    parser.add_argument("--brand-color", help="브랜드 HEX 컬러 (예: #4A90D9)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.seo_content, "r", encoding="utf-8") as f:
        content = f.read()

    # 이미지 마커 추출
    markers = parse_image_markers(content)
    if not markers:
        print("WARNING: 이미지 마커를 찾을 수 없습니다.")
        print("  먼저 insert_image_markers.py를 실행하세요.")
        print("  마커 포맷: [IMAGE: type - description]")
        return

    print(f"이미지 마커 {len(markers)}개 발견")
    print("-" * 40)

    # 프롬프트 생성
    prompts = []
    for i, marker in enumerate(markers):
        prompt_item = build_prompt(marker, args.brand_color)
        prompts.append(prompt_item)
        print(f"[{i+1}] {prompt_item['id']} ({prompt_item['type']}, {prompt_item['aspect_ratio']})")
        print(f"    {prompt_item['prompt'][:100]}...")
        print()

    # prompts.json 저장
    output_path = os.path.join(args.output_dir, "prompts.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

    print("-" * 40)
    print(f"prompts.json 생성 완료: {output_path}")
    print(f"총 {len(prompts)}개 이미지 프롬프트")
    print()
    print("다음 단계:")
    print(f"  python generate_images.py --prompts-file {output_path} --output-dir {args.output_dir}")


if __name__ == "__main__":
    main()
