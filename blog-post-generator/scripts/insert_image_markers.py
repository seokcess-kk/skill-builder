"""
SEO 원고에 이미지 마커를 삽입하는 스크립트 (Phase 2)

완성된 SEO 텍스트를 Claude가 읽고, 각 섹션의 내용/맥락에 맞는
이미지를 자율적으로 결정하여 마커를 삽입합니다.

Claude가 직접 Gemini 이미지 생성용 프롬프트를 작성하므로,
고정 템플릿 없이 콘텐츠에 최적화된 다양한 이미지가 생성됩니다.

Usage:
  python insert_image_markers.py \
    --seo-content output/keyword/seo/content/seo-content.md \
    --keyword "일산다이어트한의원"
"""

import os
import sys
import re
import json
import argparse
import subprocess
from pathlib import Path

from utils import find_claude_cmd, detect_industry, count_chars, strip_codeblock


ROOT = Path(__file__).parent.parent
IMAGE_PROMPT_GUIDE = ROOT / "skills" / "seo-writer" / "references" / "image-prompt-templates.md"
MEDICAL_GUIDE = ROOT / "skills" / "seo-writer" / "references" / "medical-ad-compliance.md"


def _load_analysis_avg_image_count(analysis_path):
    """경쟁사 분석에서 평균 이미지 수만 추출"""
    if not analysis_path or not os.path.isfile(analysis_path):
        return None
    try:
        with open(analysis_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("averages", {}).get("avg_image_count")
    except (json.JSONDecodeError, OSError):
        return None


def _recommend_image_count(avg_count):
    """경쟁사 평균 기반 권장 이미지 수 범위"""
    if not avg_count:
        return "5~7"
    if avg_count >= 20:
        return "8~10"
    if avg_count >= 10:
        return "6~8"
    if avg_count >= 5:
        return "5~7"
    return "5~6"


def _find_previous_image_types(output_dir):
    """이전 포스트의 이미지 유형 패턴을 검색하여 반복 방지"""
    output_root = Path(output_dir).resolve().parent.parent.parent  # output/
    if not output_root.exists():
        return []

    current_dir = Path(output_dir).resolve()
    patterns = []

    for content_file in sorted(output_root.glob("*/seo/content/seo-content.md")):
        if content_file.parent.resolve() == current_dir:
            continue
        try:
            text = content_file.read_text(encoding="utf-8")
        except OSError:
            continue

        types = re.findall(r'\[IMAGE:\s*(?:[^\]|]+\|\s*)?(\w+)\s*[-–]\s*', text)
        if types:
            patterns.append({
                "keyword": content_file.parent.parent.parent.name,
                "types": types,
            })

    return patterns


def insert_markers(seo_content_path, keyword, analysis_path=None, brand_color=None):
    """Claude CLI로 원고를 읽고 이미지 마커를 삽입"""
    claude_cmd = find_claude_cmd()
    if not claude_cmd:
        print("ERROR: claude CLI가 설치되지 않았습니다.")
        sys.exit(1)

    industry = detect_industry(keyword)
    is_medical = industry == "medical"

    # 원고 읽기
    with open(seo_content_path, "r", encoding="utf-8") as f:
        seo_text = f.read()

    char_count = count_chars(re.sub(r'^#{1,3}\s+', '', seo_text, flags=re.MULTILINE))

    # 경쟁사 평균 이미지 수
    avg_img = _load_analysis_avg_image_count(analysis_path)
    count_hint = _recommend_image_count(avg_img)
    avg_hint = f" (경쟁사 평균 {avg_img:.0f}장)" if avg_img else ""

    # 이전 포스트 이미지 패턴 (반복 회피)
    output_dir = str(Path(seo_content_path).parent)
    prev_patterns = _find_previous_image_types(output_dir)
    prev_hint = ""
    if prev_patterns:
        lines = []
        for p in prev_patterns[-3:]:
            lines.append(f"  - '{p['keyword']}': {' → '.join(p['types'])}")
        prev_hint = (
            "\n\n**이전 포스트 이미지 유형 시퀀스 (반복 회피):**\n"
            + "\n".join(lines)
            + "\n위와 다른 유형 조합과 순서를 사용하세요."
        )

    # 업종별 힌트
    industry_hint = ""
    if industry:
        industry_names = {
            "medical": "의료/건강",
            "beauty": "뷰티/미용",
            "education": "교육",
            "food": "음식/요리",
            "fitness": "피트니스/운동",
        }
        industry_hint = f"\n- 업종: {industry_names.get(industry, industry)}"

    # 브랜드 컬러 힌트
    color_hint = ""
    if brand_color:
        color_hint = f"\n- 브랜드 컬러: {brand_color} (일부 이미지에 자연스럽게 반영)"

    # 의료 규제 힌트
    medical_hint = ""
    if is_medical:
        medical_hint = (
            "\n- **의료 업종 주의**: 실제 환자 사진/비포애프터 금지. "
            "시술 장면은 개념적/상징적으로만 묘사. 의료광고법 준수."
        )

    # 이미지 프롬프트 가이드 경로
    guide_path = str(IMAGE_PROMPT_GUIDE.resolve()) if IMAGE_PROMPT_GUIDE.exists() else ""
    guide_instruction = ""
    if guide_path:
        guide_instruction = f"\n\n먼저 이 파일을 읽어 이미지 프롬프트 작성법을 숙지하세요:\n- {guide_path}"

    prompt = f"""당신은 블로그 콘텐츠의 시각 디렉터입니다.
아래 SEO 원고를 읽고, 각 섹션의 내용에 어울리는 이미지 마커를 삽입하세요.
{guide_instruction}

## 원고
```
{seo_text}
```

## 이미지 마커 규칙

### 수량 및 배치
- 총 {count_hint}장{avg_hint}
- 200~400자 간격으로 배치
- 첫 이미지는 2~3문단 이내에 배치
- 소제목 직후 또는 핵심 설명 후에 배치

### 마커 형식
```
[IMAGE: {{type}} - {{Gemini 이미지 생성 프롬프트(영문)}}]
```

### type (비율 결정용)
| type | 비율 | 용도 |
|------|------|------|
| real_photo | 4:3 | 인물, 상담, 시술 장면 |
| facility_photo | 16:9 | 시설, 공간, 인테리어 |
| product_photo | 1:1 | 제품, 도구, 약재 |
| illustration | 4:3 | 개념도, 설명 일러스트 |
| infographic | 3:4 | 프로세스, 비교 도형 |
| lifestyle_photo | 4:3 | 일상, 운동, 식단 |
| concept_comparison | 4:3 | 개념적 비교/대조 |
| mood_photo | 16:9 | 감성, 분위기, 배경 |

### 프롬프트 작성 핵심 원칙

1. **콘텐츠 맥락 반영** — 해당 섹션이 다루는 구체적 내용을 이미지에 반영하세요.
   예) "다이어트 정체기" 섹션 → 체중계 위에 선 발, 좌절감을 표현하는 구도
   예) "한방 치료 원리" 섹션 → 한약재가 놓인 나무 테이블, 따뜻한 톤

2. **매 이미지마다 다른 촬영 스타일** — 같은 렌즈, 같은 조명, 같은 구도를 반복하지 마세요.
   - 렌즈: 24mm wide, 35mm, 50mm, 85mm portrait, 100mm macro 등 다양하게
   - 조명: 자연광, 스튜디오 조명, 골든아워, 역광, 간접조명 등
   - 구도: 정면, 45도, 오버헤드, 로우앵글, 클로즈업 등
   - 색감: warm/cool/muted/vibrant/pastel 등

3. **장면을 구체적으로 묘사** — 키워드 나열이 아닌, 하나의 장면을 서술하세요.
   ✗ "Korean clinic, modern, clean, professional"
   ✓ "A bright consultation room with floor-to-ceiling windows, a Korean doctor in a white coat reviewing charts with a patient across a light oak desk, warm afternoon sunlight casting soft shadows, shot from a low angle with 35mm lens"

4. **유형 다양성** — {count_hint}장 중 최소 4가지 이상의 서로 다른 type을 사용하세요.
   연속 2장 이상 같은 type 금지.

5. **절대 텍스트 금지** — 프롬프트에 반드시 "no text, no words, no letters, no labels, no numbers, no watermarks" 포함.
   텍스트/숫자/단계를 암시하는 표현도 금지 (예: "4-step process", "comparison chart with labels" ❌)
   인포그래픽은 아이콘/도형/화살표만으로 구성.
{industry_hint}{color_hint}{medical_hint}{prev_hint}

## 출력
원고 전체를 그대로 출력하되, 적절한 위치에 [IMAGE: ...] 마커만 삽입하세요.
원고 텍스트를 수정하거나 삭제하지 마세요.
설명, 주석, 코드블록 래핑 없이 원고+마커만 출력합니다.
"""

    print("=" * 50)
    print("  이미지 마커 삽입 (Phase 2)")
    print("=" * 50)
    print(f"  키워드: {keyword}")
    print(f"  업종: {industry or '일반'}")
    print(f"  원고 글자수: {char_count}자")
    print(f"  권장 이미지: {count_hint}장{avg_hint}")
    if prev_patterns:
        print(f"  이전 패턴 이력: {len(prev_patterns)}건 (반복 회피)")
    print("-" * 50)
    print("  Claude가 이미지를 배치 중...")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [claude_cmd, "-p", "--allowedTools", "Read"],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        env=env,
    )

    if result.returncode != 0:
        print(f"ERROR: claude 실행 실패 (exit code {result.returncode})")
        print(result.stderr[:500] if result.stderr else "")
        sys.exit(1)

    content_with_markers = strip_codeblock(result.stdout)

    # 마커 수 확인
    markers = re.findall(r'\[IMAGE:[^\]]+\]', content_with_markers)
    marker_types = re.findall(r'\[IMAGE:\s*(\w+)\s*-', content_with_markers)
    unique_types = set(marker_types)

    # 마커가 0개면 원본 유지
    if not markers:
        print("\n  WARNING: 이미지 마커가 삽입되지 않았습니다. 원본 원고를 유지합니다.")
        print("=" * 50)
        return seo_content_path

    # 원본 백업 후 덮어쓰기
    backup_path = str(seo_content_path).replace(".md", ".plain.md")
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(seo_text)

    with open(seo_content_path, "w", encoding="utf-8") as f:
        f.write(content_with_markers)

    print(f"\n  완료!")
    print(f"  삽입된 이미지 마커: {len(markers)}개")
    print(f"  사용된 유형: {len(unique_types)}종 — {', '.join(sorted(unique_types))}")
    print(f"  원본 백업: {backup_path}")
    print(f"  저장: {seo_content_path}")
    print("=" * 50)

    return seo_content_path


def main():
    parser = argparse.ArgumentParser(description="SEO 원고에 이미지 마커 삽입 (Phase 2)")
    parser.add_argument("--seo-content", required=True, help="SEO 원고 마크다운 파일")
    parser.add_argument("--keyword", required=True, help="타겟 키워드")
    parser.add_argument("--analysis", help="경쟁사 분석 JSON 파일 (이미지 수 참조용)")
    parser.add_argument("--brand-color", help="브랜드 HEX 컬러 (예: #4A90D9)")
    args = parser.parse_args()

    insert_markers(args.seo_content, args.keyword, args.analysis, args.brand_color)


if __name__ == "__main__":
    main()
