"""
Claude CLI 기반 SEO 원고 자동 생성 스크립트

seo-writer SKILL.md를 Claude가 직접 읽고 따르며 SEO 최적화 원고를 작성합니다.

Usage:
  python generate_seo_content.py \
    --keyword "대구다이어트한의원" \
    --analysis output/keyword/seo/analysis/competitor-analysis.json \
    --output-dir output/keyword/seo/content/
"""

import os
import sys
import json
import re
import subprocess
import argparse
from pathlib import Path

from utils import find_claude_cmd, detect_medical, count_chars, strip_codeblock


ROOT = Path(__file__).parent.parent
SEO_GUIDE = ROOT / "skills" / "seo-writer" / "references" / "seo-writing-guide.md"
MEDICAL_GUIDE = ROOT / "skills" / "seo-writer" / "references" / "medical-ad-compliance.md"


def load_analysis(analysis_path):
    """분석 결과 요약 로드"""
    if not analysis_path or not os.path.isfile(analysis_path):
        return ""

    summary_path = Path(analysis_path).parent / "analysis-summary.md"
    if summary_path.exists():
        return summary_path.read_text(encoding="utf-8")
    return ""


def _load_analysis_json(analysis_path):
    """경쟁사 분석 JSON을 한 번만 로드하여 캐시 반환"""
    if not analysis_path or not os.path.isfile(analysis_path):
        return None
    try:
        with open(analysis_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def load_image_strategy(data):
    """분석 데이터에서 이미지 전략 추출"""
    if not data:
        return None
    averages = data.get("averages", {})
    avg_count = averages.get("avg_image_count", 0)
    type_pct = averages.get("image_type_distribution_pct", {})
    if not avg_count:
        return None
    return {"avg_count": avg_count, "type_distribution": type_pct}


def load_competitor_tags(data):
    """분석 데이터에서 추천 태그 추출"""
    if not data:
        return []
    return data.get("averages", {}).get("recommended_tags", [])


def load_writing_strategy(data):
    """분석 데이터에서 원고 작성 전략 추출"""
    if not data:
        return None
    averages = data.get("averages", {})
    if not averages:
        return None
    return {
        "avg_char_count": averages.get("avg_char_count", 0),
        "avg_heading_count": averages.get("avg_heading_count", 0),
        "avg_paragraph_length": averages.get("avg_paragraph_length", 0),
        "tone_distribution": averages.get("tone_distribution", {}),
        "style_distribution": averages.get("style_distribution", {}),
    }


def find_previous_seo_structures(output_dir):
    """이전 SEO 원고의 소제목 구조를 검색하여 반복 방지용 이력 반환

    output/{keyword-slug}/seo/content/seo-content.md 구조를 전제로 스캔.
    """
    output_root = Path(output_dir).resolve().parent.parent.parent  # output/
    if not output_root.exists():
        return []

    current_dir = Path(output_dir).resolve()
    structures = []

    for content_file in sorted(output_root.glob("*/seo/content/seo-content.md")):
        if content_file.parent.resolve() == current_dir:
            continue
        try:
            text = content_file.read_text(encoding="utf-8")
        except OSError:
            continue

        # H2 소제목 추출
        headings = re.findall(r'^## (.+)$', text, re.MULTILINE)
        if not headings:
            continue

        structures.append({
            "keyword": content_file.parent.parent.parent.name,
            "headings": headings,
        })

    return structures


def _build_writing_rules(writing_strategy, previous_structures=None):
    """경쟁사 분석 기반 원고 작성 규칙 생성 (톤/구조/글자수 적응형)"""
    if not writing_strategy:
        rules = [
            "4. **글자수** — 2,000~3,000자",
            "5. **소제목** — ## (H2) 사용, 3~5개",
            "6. **문단** — 1문단 80~150자 (모바일 가독성)",
            "7. **톤** — 해요체, 전문적이면서 친근한 정보형",
        ]
        return "\n".join(rules)

    avg_chars = writing_strategy["avg_char_count"]
    avg_headings = writing_strategy["avg_heading_count"]
    tone_dist = writing_strategy["tone_distribution"]
    style_dist = writing_strategy["style_distribution"]

    # 글자수 (경쟁사 기반, 최소 1500자 보장)
    if avg_chars >= 3000:
        char_range = "2,500~3,500"
    elif avg_chars >= 2000:
        char_range = "2,000~3,000"
    elif avg_chars >= 1500:
        char_range = "1,500~2,500"
    else:
        char_range = "2,000~3,000"

    # 소제목 수
    if avg_headings >= 5:
        heading_range = "4~6"
    elif avg_headings >= 3:
        heading_range = "3~5"
    else:
        heading_range = "3~4"

    # 톤 (경쟁사 우세 문체)
    tone_map = {
        "formal": "합니다체(격식체), 전문적이고 권위 있는 정보형",
        "polite_casual": "해요체, 전문적이면서 친근한 정보형",
        "banmal": "한다체(문어체), 간결하고 단정적인 정보형",
    }
    dominant_tone = max(tone_dist, key=tone_dist.get) if tone_dist else "polite_casual"
    if dominant_tone == "unknown":
        dominant_tone = "polite_casual"
    tone_desc = tone_map.get(dominant_tone, tone_map["polite_casual"])

    # 전달 방식
    style_map = {
        "qa": "Q&A(질문-답변) — 소제목을 질문형으로, 본문에서 답변하는 구조",
        "narrative": "서사형 — 자연스럽게 이야기하듯 풀어가는 구조",
        "list": "리스트형 — 핵심을 번호/불릿으로 정리하는 구조",
    }
    dominant_style = max(style_dist, key=style_dist.get) if style_dist else "narrative"
    style_desc = style_map.get(dominant_style, style_map["narrative"])

    lines = [
        f"4. **글자수** — {char_range}자 (경쟁사 평균 {avg_chars:.0f}자)",
        f"5. **소제목** — ## (H2) 사용, {heading_range}개 (경쟁사 평균 {avg_headings:.0f}개)",
        "6. **문단** — 1문단 80~150자 (모바일 가독성)",
        f"7. **톤** — {tone_desc}",
        f"8. **전달 방식** — {style_desc}",
        "9. **구조 다양성** — 아래 구조 유형 중 전달 방식과 키워드 특성에 맞는 것을 선택하세요. "
        "매번 '도입→원인→해결→요약' 패턴만 반복하지 마세요.",
        "   - **문제-해결형**: 문제 제기 → 원인 분석 → 해결책 → 정리",
        "   - **Q&A형**: 질문형 소제목 → 답변 → 다음 질문 → 총정리",
        "   - **비교-선택형**: 옵션 나열 → 각각 장단점 → 추천/주의사항",
        "   - **체크리스트형**: 확인 항목 나열 → 각 항목 상세 설명 → 요약",
        "   - **스토리형**: 상황 묘사 → 전개/과정 → 결과/교훈 → 정리",
    ]

    # 이전 원고 구조 회피
    if previous_structures:
        avoid_lines = []
        for prev in previous_structures[-3:]:  # 최근 3개만
            hs = " → ".join(prev["headings"][:5])
            avoid_lines.append(f"     · '{prev['keyword']}': {hs}")
        lines.append("   - 이전 포스트와 다른 소제목 구조를 사용하세요:")
        lines.extend(avoid_lines)

    return "\n".join(lines)


def _parse_title_tags_body(content):
    """Claude 출력에서 TITLE, TAGS, 본문을 분리합니다.

    예상 포맷:
      TITLE: 제목 텍스트
      TAGS: 태그1, 태그2, 태그3
      ---
      ## 소제목
      본문...
    """
    title = ""
    tags = []
    body = content

    lines = content.split("\n")
    body_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # TITLE 행
        if stripped.upper().startswith("TITLE:"):
            title = stripped.split(":", 1)[1].strip()
            body_start = i + 1
            continue

        # TAGS 행
        if stripped.upper().startswith("TAGS:"):
            raw_tags = stripped.split(":", 1)[1].strip()
            tags = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]
            body_start = i + 1
            continue

        # --- 구분선 → 이후가 본문
        if stripped == "---":
            body_start = i + 1
            break

        # 위 조건에 해당하지 않는 첫 비공백 행이면 본문 시작
        if stripped:
            body_start = i
            break

    body = "\n".join(lines[body_start:]).strip()

    return title, tags, body


def _build_tag_hint(competitor_tags):
    """경쟁사 태그를 프롬프트 힌트로 변환"""
    if not competitor_tags:
        return ""
    tags_str = ", ".join(competitor_tags[:10])
    return f"\n- 경쟁사 상위글 공통 태그 참고: {tags_str}"


def _build_image_marker_guide(image_strategy):
    """경쟁사 분석 기반 이미지 마커 가이드 생성"""
    if not image_strategy:
        return "   - 이미지 수: 5~8장"

    avg = image_strategy["avg_count"]
    type_dist = image_strategy["type_distribution"]

    # 이미지 수 권장 (경쟁사 대비)
    if avg >= 20:
        rec = "8~10"
    elif avg >= 10:
        rec = "6~8"
    elif avg >= 5:
        rec = "5~7"
    else:
        rec = "5~6"

    lines = [f"   - 이미지 수: {rec}장 (경쟁사 평균 {avg:.0f}장 — 양으로 경쟁하지 말고 질로 승부)"]

    # 유형별 권장 배분
    known = {k: v for k, v in type_dist.items() if k != "unknown"}
    type_names = {
        "real_photo": "실사 사진(인물/상담)",
        "facility_photo": "시설/공간 사진",
        "infographic": "인포그래픽(아이콘/도형)",
        "illustration": "일러스트",
        "product_photo": "제품 사진",
        "lifestyle_photo": "라이프스타일 사진",
    }

    if known:
        top = sorted(known.items(), key=lambda x: x[1], reverse=True)[:3]
        rec_types = ", ".join(f"{type_names.get(t, t)}({p}%)" for t, p in top)
        lines.append(f"   - 경쟁사 주요 유형: {rec_types} → 이 비율을 참고하되 다양하게 배분")
    else:
        lines.append("   - 유형 배분 권장: 도입부에 facility_photo 1장, 본문에 real_photo/lifestyle_photo 3~4장, "
                      "infographic 1~2장, 마무리에 real_photo 1장")

    # 배치 전략
    lines.append("   - 배치 순서: 도입부(시설/공간) → 본문(콘텐츠 관련 실사/라이프스타일) → 마무리(상담/CTA)")

    return "\n".join(lines)


def generate_content(keyword, analysis_path, output_dir):
    """claude -p로 SEO 원고 생성"""
    claude_cmd = find_claude_cmd()
    if not claude_cmd:
        print("ERROR: claude CLI가 설치되지 않았습니다.")
        sys.exit(1)

    analysis_summary = load_analysis(analysis_path)
    analysis_data = _load_analysis_json(analysis_path)
    image_strategy = load_image_strategy(analysis_data)
    writing_strategy = load_writing_strategy(analysis_data)
    competitor_tags = load_competitor_tags(analysis_data)
    previous_structures = find_previous_seo_structures(output_dir)
    is_medical = detect_medical(keyword)

    # 파일 경로 (Claude가 Read 도구로 읽을 경로)
    seo_guide_path = str(SEO_GUIDE.resolve())
    medical_guide_path = str(MEDICAL_GUIDE.resolve()) if is_medical else None

    # 프롬프트 구성
    medical_instruction = ""
    if medical_guide_path:
        medical_instruction = f"\n3. {medical_guide_path} — 의료광고법 컴플라이언스 가이드 (반드시 준수)"

    analysis_block = ""
    if analysis_summary:
        analysis_block = f"""
## 상위글 분석 결과
{analysis_summary}
"""

    prompt = f"""당신은 네이버 블로그 SEO 전문 작가입니다.

먼저 아래 파일을 읽어주세요:
1. {seo_guide_path} — SEO 작성 가이드
{medical_instruction}

{analysis_block}

## 작업
'{keyword}' 키워드에 최적화된 네이버 블로그 원고를 작성하세요.

## 핵심 규칙
1. **정보성 글만 작성** — 후기성/광고성 글 금지
2. **키워드 '{keyword}'를 자연스럽게 삽입** (밀도 2~3%)
   - 첫 문단 50자 이내에 첫 등장
   - 소제목 2개 이상에 포함
   - 마지막 문단에 1회
3. **이미지 마커** — [IMAGE: type - description] 형식으로 삽입
   - description은 순수 시각적 장면만 묘사 (예: "밝은 진료실에서 상담하는 의사와 환자")
   - 텍스트/숫자/단계를 암시하는 표현 금지 (예: "4단계 프로세스", "비교 차트", "수치 그래프" ❌)
   - infographic 유형은 아이콘/도형 기반 시각 레이아웃만 묘사할 것
   - type은 다음 중 선택: real_photo, facility_photo, infographic, illustration, product_photo, lifestyle_photo, concept_comparison, mood_photo
{_build_image_marker_guide(image_strategy)}
{_build_writing_rules(writing_strategy, previous_structures)}

## 출력 형식
아래 형식으로 출력하세요. 설명, 주석, 코드블록 래핑 없이 바로 출력합니다.

```
TITLE: 제목 (30~40자, 키워드 '{keyword}'를 앞쪽에 배치, 클릭 유도 표현 포함)
TAGS: 태그1, 태그2, 태그3, ... (8~15개, 메인 키워드 + 롱테일 변형 + 지역명/업종)
---
## 소제목1
본문 ...
```

**제목 규칙:**
- 30~40자 이내
- 메인 키워드 '{keyword}'를 앞쪽에 배치
- 클릭 유도: "알아보기", "확인해야 할", "놓치면 안 되는" 등 활용
- 제목 후보를 1개만 출력

**태그 규칙:**
- 메인 키워드를 첫 번째 태그로
- 롱테일 키워드 변형 3~5개
- 관련 일반 키워드 3~5개
- 지역명이 있으면 지역 태그 포함{_build_tag_hint(competitor_tags)}

`---` 구분선 아래부터 소제목(## )으로 시작하는 원고 본문을 작성하세요.
"""

    print("=" * 50)
    print("  SEO 원고 자동 생성 (Claude)")
    print("=" * 50)
    print(f"  키워드: {keyword}")
    print(f"  의료 업종: {'예' if is_medical else '아니오'}")
    print(f"  분석 데이터: {'있음' if analysis_summary else '없음'}")
    if writing_strategy:
        tone_dist = writing_strategy.get("tone_distribution", {})
        style_dist = writing_strategy.get("style_distribution", {})
        dominant_tone = max(tone_dist, key=tone_dist.get) if tone_dist else "?"
        dominant_style = max(style_dist, key=style_dist.get) if style_dist else "?"
        print(f"  경쟁사 톤: {dominant_tone}, 전달 방식: {dominant_style}")
    if previous_structures:
        print(f"  이전 원고 이력: {len(previous_structures)}건 (구조 반복 회피)")
    print("-" * 50)
    print("  Claude가 원고를 작성 중...")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [claude_cmd, "-p", "--allowedTools", "Read,WebFetch"],
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

    content = strip_codeblock(result.stdout)

    # 제목/태그 파싱 및 분리
    title, tags, body = _parse_title_tags_body(content)

    if not title:
        print("  WARNING: 제목(TITLE:)이 파싱되지 않았습니다. Claude 출력 형식을 확인하세요.")
    if not tags:
        print("  WARNING: 태그(TAGS:)가 파싱되지 않았습니다. Claude 출력 형식을 확인하세요.")

    # 저장
    os.makedirs(output_dir, exist_ok=True)

    # 원고 본문 저장 (제목/태그 제외)
    output_path = os.path.join(output_dir, "seo-content.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)

    # 제목/태그 메타 저장
    meta = {"title": title, "tags": tags}
    meta_path = os.path.join(output_dir, "seo-meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 글자수 계산
    plain = re.sub(r'\[IMAGE:[^\]]+\]', '', body)
    plain = re.sub(r'^#{1,3}\s+', '', plain, flags=re.MULTILINE)
    char_count = count_chars(plain)

    print(f"\n  완료!")
    print(f"  제목: {title}")
    print(f"  태그: {len(tags)}개 — {', '.join(tags[:5])}{'...' if len(tags) > 5 else ''}")
    print(f"  글자수: {char_count}자")
    print(f"  원고: {output_path}")
    print(f"  메타: {meta_path}")
    print("=" * 50)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Claude SEO 원고 자동 생성")
    parser.add_argument("--keyword", required=True, help="타겟 키워드")
    parser.add_argument("--analysis", help="경쟁사 분석 JSON 파일")
    parser.add_argument("--output-dir", required=True, help="출력 디렉토리")
    args = parser.parse_args()

    generate_content(args.keyword, args.analysis, args.output_dir)


if __name__ == "__main__":
    main()
