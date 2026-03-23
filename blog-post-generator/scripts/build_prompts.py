"""
SEO 텍스트의 이미지 마커에서 Gemini 프롬프트를 생성하는 스크립트

SEO 콘텐츠(마크다운)에서 [IMAGE: ...] 마커를 추출하고,
image-prompt-templates.md의 유형별 템플릿을 기반으로
generate_images.py가 사용할 prompts.json을 생성합니다.

Usage:
  python build_prompts.py \
    --seo-content output/keyword/content/seo-content.md \
    --output-dir output/keyword/images/ \
    --keyword "일산다이어트한의원"

Input 마커 포맷:
  [IMAGE: {filename} | {type} - {description}]
  예: [IMAGE: seo-img-01-consultation.png | real_photo - 한의원 상담 장면]

Output: prompts.json (generate_images.py 입력용)
"""

import os
import re
import json
import hashlib
import argparse

from utils import detect_industry


# 유형별 프롬프트 스타일 변형 풀
# 각 유형에 여러 스타일을 두고 로테이션하여 포스트 간 이미지 다양성을 확보
PROMPT_STYLE_VARIANTS = {
    "real_photo": [
        {
            "base": (
                "A {description}, "
                "shot with 85mm portrait lens, soft natural lighting from large windows, "
                "clean and minimal interior with white walls, "
                "professional photography style, warm and trustworthy atmosphere, "
                "Korean setting, high quality"
            ),
            "default_ratio": "4:3",
        },
        {
            "base": (
                "A {description}, "
                "shot with 35mm lens, warm tungsten overhead lighting, "
                "modern interior with light wood panels and green plants, "
                "documentary photography style, authentic and approachable feel, "
                "Korean setting, high quality"
            ),
            "default_ratio": "4:3",
        },
        {
            "base": (
                "A {description}, "
                "shot with 50mm lens, bright diffused daylight, "
                "contemporary space with glass partitions and neutral tones, "
                "editorial photography style, confident and professional mood, "
                "Korean setting, high quality"
            ),
            "default_ratio": "4:3",
        },
    ],
    "facility_photo": [
        {
            "base": (
                "Interior of a modern Korean {description}, "
                "minimalist contemporary design with warm wood accents, "
                "neutral beige and white color palette, "
                "professional architectural photography, wide angle 24mm lens, "
                "bright and welcoming atmosphere, no people"
            ),
            "default_ratio": "16:9",
        },
        {
            "base": (
                "Interior of a Korean {description}, "
                "clean Scandinavian-inspired design with concrete and white surfaces, "
                "cool gray and soft mint palette, "
                "architectural photography, 20mm ultra-wide lens, "
                "airy and spacious atmosphere, no people"
            ),
            "default_ratio": "16:9",
        },
        {
            "base": (
                "Interior of a Korean {description}, "
                "warm boutique-style design with soft indirect lighting, "
                "earth tone palette with terracotta and cream, "
                "interior design photography, 28mm lens, "
                "cozy and premium atmosphere, no people"
            ),
            "default_ratio": "16:9",
        },
    ],
    "product_photo": [
        {
            "base": (
                "{description} arranged on a clean white marble surface, "
                "soft diffused studio lighting, minimal white background with subtle shadow, "
                "shot from 45-degree angle, fine detail visible, "
                "professional product photography, warm natural tone"
            ),
            "default_ratio": "1:1",
        },
        {
            "base": (
                "{description} placed on a light linen fabric surface, "
                "golden hour side lighting, soft bokeh background, "
                "shot from overhead flat-lay angle, "
                "lifestyle product photography, warm organic tone"
            ),
            "default_ratio": "1:1",
        },
    ],
    "illustration": [
        {
            "base": (
                "Flat vector illustration of {description}, "
                "soft pastel color palette, clean thin outlines, "
                "white background, modern illustration style, "
                "simple and visual only, no text labels, no annotations"
            ),
            "default_ratio": "4:3",
        },
        {
            "base": (
                "Minimal line art illustration of {description}, "
                "muted earth tone color palette, single continuous line style, "
                "off-white background, elegant and refined, "
                "simple and visual only, no text labels, no annotations"
            ),
            "default_ratio": "4:3",
        },
    ],
    "infographic": [
        {
            "base": (
                "Clean minimal visual diagram showing {description}, "
                "flat design style, simple geometric icons and colored shapes only, "
                "connected by arrows and lines, white background, "
                "purely graphical with icons and symbols only, "
                "absolutely no text or labels or numbers anywhere"
            ),
            "default_ratio": "3:4",
        },
        {
            "base": (
                "Modern isometric visual diagram showing {description}, "
                "3D isometric icons and soft gradient shapes, "
                "flowing connections and dotted paths, light gray background, "
                "purely graphical with icons and symbols only, "
                "absolutely no text or labels or numbers anywhere"
            ),
            "default_ratio": "3:4",
        },
    ],
    "lifestyle_photo": [
        {
            "base": (
                "{description}, "
                "natural candid photography style, warm morning sunlight, "
                "soft warm color grading, shot with 50mm lens, "
                "Korean model, authentic and relatable everyday moment"
            ),
            "default_ratio": "4:3",
        },
        {
            "base": (
                "{description}, "
                "lifestyle editorial photography, soft overcast daylight, "
                "cool neutral color grading, shot with 35mm lens, "
                "Korean model, calm and mindful everyday scene"
            ),
            "default_ratio": "4:3",
        },
        {
            "base": (
                "{description}, "
                "bright airy photography style, gentle backlight from window, "
                "clean pastel color grading, shot with 85mm lens, "
                "Korean model, fresh and positive daily moment"
            ),
            "default_ratio": "4:3",
        },
    ],
    "concept_comparison": [
        {
            "base": (
                "Split image concept showing contrast: {description}, "
                "clean modern style, clear visual separation, "
                "conceptual and symbolic representation, "
                "not showing real patients, artistic interpretation, "
                "no text or labels on either side"
            ),
            "default_ratio": "4:3",
        },
    ],
    "mood_photo": [
        {
            "base": (
                "{description}, "
                "soft dreamy atmosphere, gentle color grading, "
                "shallow depth of field, editorial photography style, "
                "calm and peaceful mood"
            ),
            "default_ratio": "16:9",
        },
        {
            "base": (
                "{description}, "
                "cinematic atmosphere, warm amber color grading, "
                "anamorphic lens flare, film photography style, "
                "contemplative and serene mood"
            ),
            "default_ratio": "16:9",
        },
    ],
}

# 하위 호환: 기본 템플릿 (각 유형의 첫 번째 변형)
PROMPT_TEMPLATES = {k: v[0] for k, v in PROMPT_STYLE_VARIANTS.items()}

# 업종별 추가 프롬프트 접미사 변형 풀
INDUSTRY_SUFFIX_VARIANTS = {
    "medical": [
        ", healthcare professional setting, medical context, clean and sterile environment",
        ", modern clinic atmosphere, warm and caring medical environment, soothing tones",
        ", bright medical office setting, welcoming healthcare space, professional and calm",
    ],
    "beauty": [
        ", beauty and skincare aesthetic, luxurious and elegant atmosphere",
        ", soft feminine aesthetic, premium spa-like atmosphere, delicate and refined",
        ", clean K-beauty aesthetic, bright and dewy atmosphere, fresh and modern",
    ],
    "education": [
        ", educational environment, bright and inspiring atmosphere",
        ", modern learning space, focused and productive atmosphere, clean design",
    ],
    "food": [
        ", food photography aesthetic, appetizing and fresh presentation",
        ", rustic table setting, natural ingredients focus, warm homestyle atmosphere",
    ],
    "fitness": [
        ", active lifestyle, energetic and motivating atmosphere",
        ", wellness-focused setting, balanced and mindful movement, natural light gym",
    ],
}

# 하위 호환: 기본 접미사 (각 업종의 첫 번째 변형)
INDUSTRY_SUFFIX = {k: v[0] for k, v in INDUSTRY_SUFFIX_VARIANTS.items()}

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


# 텍스트/숫자를 암시하는 표현 → 시각적 대체어 매핑
# 순서 중요: 구체적(긴) 패턴 → 일반적(짧은) 패턴 순서로 매칭
_TEXT_IMPLYING_PATTERNS = [
    # 복합 패턴 (먼저 매칭)
    (re.compile(r'\d+단계\s*프로세스', re.IGNORECASE), "흐름을 나타내는 아이콘과 화살표 구성"),
    (re.compile(r'\d+단계', re.IGNORECASE), "여러 단계의 아이콘 흐름"),
    (re.compile(r'비교\s*차트', re.IGNORECASE), "두 가지 요소의 시각적 대비"),
    (re.compile(r'수치\s*그래프', re.IGNORECASE), "상승 곡선이 있는 그래픽 요소"),
    (re.compile(r'데이터\s*표', re.IGNORECASE), "그래픽 시각화 요소"),
    (re.compile(r'표로|차트로|그래프로', re.IGNORECASE), "시각적 도형으로"),
    # 단독 한국어 패턴
    (re.compile(r'프로세스', re.IGNORECASE), "흐름 구성"),
    (re.compile(r'통계', re.IGNORECASE), "그래픽 시각화 요소"),
    (re.compile(r'수치', re.IGNORECASE), "그래픽 요소"),
    (re.compile(r'번호|넘버링', re.IGNORECASE), "순서를 나타내는 아이콘"),
    (re.compile(r'라벨|레이블|캡션', re.IGNORECASE), "아이콘"),
    (re.compile(r'차트', re.IGNORECASE), "시각적 도형"),
    (re.compile(r'그래프', re.IGNORECASE), "곡선 그래픽"),
    (re.compile(r'(?<!사진|화살)표(?!현|정|면|시)', re.IGNORECASE), "도형 레이아웃"),
    (re.compile(r'리스트|목록', re.IGNORECASE), "아이콘 나열"),
    (re.compile(r'제목|타이틀|헤딩', re.IGNORECASE), "강조 요소"),
    (re.compile(r'텍스트|문자|글자|글씨|문구|안내문|설명문', re.IGNORECASE), "시각적 요소"),
    (re.compile(r'숫자', re.IGNORECASE), "기호"),
    # 영어 패턴 — \b 단어 경계 필수 (photograph, lifestyle 등 오매칭 방지)
    (re.compile(r'\bchart\b', re.IGNORECASE), "visual diagram"),
    (re.compile(r'\bgraph\b', re.IGNORECASE), "curve graphic"),
    (re.compile(r'\btable\b', re.IGNORECASE), "grid layout"),
    (re.compile(r'\blabels?\b', re.IGNORECASE), "icon"),
    (re.compile(r'\btext\b', re.IGNORECASE), "visual element"),
    (re.compile(r'\bcaptions?\b', re.IGNORECASE), "visual element"),
    (re.compile(r'\btitles?\b', re.IGNORECASE), "accent element"),
    (re.compile(r'\bnumbers?\b|\bdigits?\b', re.IGNORECASE), "symbol"),
    (re.compile(r'\bsteps?\s*\d+', re.IGNORECASE), "sequential icon flow"),
    (re.compile(r'\blist\b', re.IGNORECASE), "icon arrangement"),
]


def _sanitize_description(description):
    """이미지 설명에서 텍스트/숫자를 암시하는 표현을 시각적 표현으로 대체합니다."""
    sanitized = description
    for pattern, replacement in _TEXT_IMPLYING_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def _select_style_index(keyword, img_type):
    """키워드 해시 기반으로 스타일 변형 인덱스를 결정적으로 선택.

    같은 키워드는 항상 같은 스타일을 선택하지만,
    다른 키워드는 다른 스타일을 선택합니다.
    hashlib을 사용하여 PYTHONHASHSEED와 무관하게 재현 가능.
    """
    variants = PROMPT_STYLE_VARIANTS.get(img_type, [])
    if len(variants) <= 1:
        return 0
    digest = hashlib.md5(f"{keyword}:{img_type}".encode()).hexdigest()
    return int(digest, 16) % len(variants)


def build_prompt(marker, industry=None, brand_color=None, keyword=None):
    """이미지 마커에서 Gemini 프롬프트를 생성합니다.

    keyword가 주어지면 키워드별로 다른 스타일 변형을 선택하여
    포스트 간 이미지 다양성을 확보합니다.
    """
    img_type = marker["type"]
    description = _sanitize_description(marker["description"])

    # 스타일 변형 선택 (키워드 기반 로테이션)
    if keyword:
        style_idx = _select_style_index(keyword, img_type)
        variants = PROMPT_STYLE_VARIANTS.get(img_type, [PROMPT_TEMPLATES.get(img_type, PROMPT_TEMPLATES["real_photo"])])
        template = variants[style_idx % len(variants)]
    else:
        template = PROMPT_TEMPLATES.get(img_type, PROMPT_TEMPLATES["real_photo"])

    base_description = template["base"].format(description=description)
    aspect_ratio = template["default_ratio"]

    # no-text 접두사 — 프롬프트 앞에 배치해 최우선 적용
    prompt = (
        "IMPORTANT: Generate a purely visual image with ZERO text of any kind. "
        "Do not render any letters, words, numbers, labels, captions, watermarks, "
        "or typographic elements anywhere in the image. "
    )
    prompt += base_description

    # 업종별 접미사 (키워드 기반 변형 선택)
    if industry:
        suffix_variants = INDUSTRY_SUFFIX_VARIANTS.get(industry, [])
        if suffix_variants and keyword:
            suffix_idx = int(hashlib.md5(keyword.encode()).hexdigest(), 16) % len(suffix_variants)
            prompt += suffix_variants[suffix_idx]
        elif industry in INDUSTRY_SUFFIX:
            prompt += INDUSTRY_SUFFIX[industry]

    # 브랜드 컬러 힌트
    if brand_color:
        prompt += f", accent color {brand_color} used subtly in the composition"

    # 공통 no-text 접미사 — 이중 강조
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
    parser.add_argument("--keyword", help="타겟 키워드 (업종 자동 감지용)")
    parser.add_argument("--brand-color", help="브랜드 HEX 컬러 (예: #4A90D9)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 업종 자동 감지
    industry = None
    if args.keyword:
        industry = detect_industry(args.keyword)
        if industry:
            print(f"업종 자동 감지: {industry} (키워드: {args.keyword})")

    with open(args.seo_content, "r", encoding="utf-8") as f:
        content = f.read()

    # 이미지 마커 추출
    markers = parse_image_markers(content)
    if not markers:
        print("WARNING: 이미지 마커를 찾을 수 없습니다.")
        print("  마커 포맷: [IMAGE: filename.png | type - description]")
        print("  또는:      [IMAGE: type - description]")
        return

    print(f"이미지 마커 {len(markers)}개 발견")
    print("-" * 40)

    # 프롬프트 생성
    prompts = []
    for i, marker in enumerate(markers):
        prompt_item = build_prompt(marker, industry, args.brand_color, args.keyword)
        prompts.append(prompt_item)
        print(f"[{i+1}] {prompt_item['id']} ({prompt_item['type']}, {prompt_item['aspect_ratio']})")
        print(f"    {prompt_item['prompt'][:80]}...")
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
