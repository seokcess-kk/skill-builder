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
import hashlib
import subprocess
import argparse
from pathlib import Path
from datetime import date

from utils import find_claude_cmd, detect_medical, count_chars, strip_codeblock
from validate_seo import validate as _validate


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


def load_competitor_tags(data):
    """분석 데이터에서 추천 태그 추출"""
    if not data:
        return []
    return data.get("averages", {}).get("recommended_tags", [])


def load_competitor_titles(data):
    """분석 데이터에서 경쟁사 제목 목록 추출"""
    if not data:
        return []
    return data.get("averages", {}).get("competitor_titles", [])


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


def load_content_analysis(data):
    """분석 데이터에서 콘텐츠 분석 (필수 주제, 차별화 주제, 경쟁사 아웃라인) 추출"""
    if not data:
        return None
    averages = data.get("averages", {})
    must_cover = averages.get("must_cover_topics", [])
    unique = averages.get("unique_topics", [])
    outlines = averages.get("content_outlines", [])
    if not must_cover and not outlines:
        return None
    return {
        "must_cover_topics": must_cover,
        "unique_topics": unique,
        "content_outlines": outlines,
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


def _build_keyword_density_guide(keyword, writing_strategy):
    """키워드 길이에 맞는 구체적 밀도 가이드 생성

    긴 키워드(7자+)는 소수 삽입으로도 밀도 4%를 넘기기 쉬우므로,
    목표 글자수 기반으로 적정 출현 횟수를 계산하여 명시합니다.
    """
    kw_len = count_chars(keyword)

    # 목표 글자수 추정
    target_chars = 2500
    if writing_strategy:
        avg = writing_strategy.get("avg_char_count", 0)
        if avg >= 3000:
            target_chars = 3000
        elif avg >= 2000:
            target_chars = 2500
        elif avg >= 1500:
            target_chars = 2000
        else:
            target_chars = 2500

    # 적정 출현 횟수 계산 (밀도 2~3% 목표)
    ideal_count_low = max(round(target_chars * 0.02 / kw_len), 3)
    ideal_count_high = max(round(target_chars * 0.03 / kw_len), ideal_count_low + 1)
    max_count = max(round(target_chars * 0.038 / kw_len), ideal_count_high)  # 3.8%까지 허용 (4% 미만)

    return (
        f"   - 키워드 '{keyword}'({kw_len}자): 본문에 **{ideal_count_low}~{ideal_count_high}회** 삽입 (최대 {max_count}회 — 초과 시 키워드 스터핑)\n"
        f"   - 밀도 목표: 2~3% (4% 초과 금지)"
    )


def _detect_previous_format_patterns(previous_structures):
    """이전 포스트의 포맷 패턴을 감지하여 사용된 스타일 목록 반환"""
    if not previous_structures:
        return []

    used_patterns = []

    for prev in previous_structures[-3:]:
        headings = prev.get("headings", [])

        # 소제목 스타일 감지
        question_headings = sum(1 for h in headings if "?" in h or "？" in h)
        if question_headings >= 2:
            used_patterns.append("질문형 소제목")
        elif any("체크" in h or "확인" in h or "포인트" in h for h in headings):
            used_patterns.append("체크리스트형 소제목")
        else:
            used_patterns.append("서술형 소제목")

    return list(set(used_patterns))


def _build_format_diversity_rules(previous_structures, start_num=9):
    """포맷 다양화 규칙 생성

    이전 포스트와 다른 마크다운 포맷을 사용하도록 구체적 지시를 생성합니다.
    start_num: 규칙 번호 (폴백 경로에서는 7, 정상 경로에서는 9)
    """
    # 날짜+이전구조 기반으로 포맷 세트를 로테이션 (같은 날 여러 글도 다른 변형 선택)
    prev_count = len(previous_structures) if previous_structures else 0
    seed_str = f"{date.today().isoformat()}:{prev_count}"
    seed = hashlib.md5(seed_str.encode()).hexdigest()
    variant_idx = int(seed, 16) % 5

    # 포맷 변형 풀
    format_variants = [
        {
            "list_style": "번호 리스트 (1. 2. 3.)",
            "emphasis": "핵심 문장을 **볼드**로 강조, 부연 설명은 괄호 () 활용",
            "special": "섹션 도입에 짧은 한 줄 요약을 먼저 제시 후 상세 설명",
            "transition": "소제목 사이에 '그렇다면', '여기서 중요한 건' 같은 자연스러운 연결 문장 사용",
        },
        {
            "list_style": "불릿 리스트 (- 항목) + 항목마다 굵은 키워드",
            "emphasis": "중요 개념을 *이탤릭*으로, 핵심 결론만 **볼드**로",
            "special": "각 섹션 끝에 한 줄 핵심 정리 (예: '→ 결국 중요한 건 ~입니다')",
            "transition": "독자에게 직접 질문을 던지며 다음 섹션으로 연결 ('~해본 적 있으신가요?')",
        },
        {
            "list_style": "인라인 나열 (첫째, 둘째, 셋째를 문장 속에 자연스럽게 배치)",
            "emphasis": "강조할 부분을 짧은 독립 문장으로 분리 (한 줄에 핵심만)",
            "special": "비교/대조 구조 활용 ('A와 달리 B는 ~', '일반적으로는 ~ 하지만 실제로는 ~')",
            "transition": "앞 섹션의 마지막 문장이 다음 섹션의 주제를 자연스럽게 암시",
        },
        {
            "list_style": "혼합형 — 짧은 항목은 번호(1. 2. 3.), 상세 항목은 불릿(-)",
            "emphasis": "핵심 수치/기간을 **볼드**로 강조 (예: **3개월**, **2~3kg**)",
            "special": "경험적 표현 삽입 ('실제로 ~한 경우가 많아요', '현장에서 보면 ~')",
            "transition": "'이런 이유로', '이 점을 고려하면' 같은 인과 연결 사용",
        },
        {
            "list_style": "대시(-) 리스트를 사용하되, 각 항목을 2줄로 구성 (요약 + 부연)",
            "emphasis": "섹션당 **볼드 1회만** 사용 (가장 핵심 메시지에만), 나머지는 문장 구조로 강조",
            "special": "구체적 예시/사례를 각 섹션에 1개씩 포함 ('예를 들어 ~', '~한 분은 ~')",
            "transition": "시간/단계 흐름으로 연결 ('처음에는 ~ → 그다음 ~ → 결국 ~')",
        },
    ]

    variant = format_variants[variant_idx]

    # 이전 패턴 회피
    prev_patterns = _detect_previous_format_patterns(previous_structures) if previous_structures else []
    avoid_hint = ""
    if prev_patterns:
        avoid_hint = f"\n   - 이전 포스트에서 '{', '.join(prev_patterns)}' 스타일을 사용했으므로 다른 접근을 시도하세요."

    lines = [
        f"{start_num}. **포맷 다양화** — 매번 같은 마크다운 스타일을 반복하지 마세요.",
        f"   - 리스트 스타일: {variant['list_style']}",
        f"   - 강조 방식: {variant['emphasis']}",
        f"   - 서술 기법: {variant['special']}",
        f"   - 섹션 전환: {variant['transition']}",
        avoid_hint,
    ]

    return "\n".join(line for line in lines if line)


def _build_writing_rules(writing_strategy, previous_structures=None):
    """경쟁사 분석 기반 원고 작성 규칙 생성 (톤/구조/글자수 적응형)"""
    if not writing_strategy:
        rules = [
            "3. **글자수** — **반드시 2,000자 이상** 작성 (공백 제외). 2,000~3,000자 범위. 글자수가 부족하면 본론 섹션을 더 깊이 전개하세요.",
            "4. **소제목** — ## (H2) 사용, 3~5개",
            "5. **문단** — 1문단 80~150자 (모바일 가독성)",
            "6. **톤** — 해요체, 전문적이면서 친근한 정보형",
            _build_format_diversity_rules(previous_structures, start_num=7),
        ]
        return "\n".join(rules)

    avg_chars = writing_strategy["avg_char_count"]
    avg_headings = writing_strategy["avg_heading_count"]
    tone_dist = writing_strategy["tone_distribution"]
    style_dist = writing_strategy["style_distribution"]

    # 글자수 (경쟁사 기반, 최소 2000자 보장)
    if avg_chars >= 3000:
        char_min = 2500
        char_range = "2,500~3,500"
    elif avg_chars >= 2000:
        char_min = 2000
        char_range = "2,000~3,000"
    elif avg_chars >= 1500:
        char_min = 2000
        char_range = "2,000~2,500"
    else:
        char_min = 2000
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
        f"3. **글자수** — **반드시 {char_min:,}자 이상** 작성 (공백 제외). {char_range}자 범위 (경쟁사 평균 {avg_chars:.0f}자). 글자수가 부족하면 본론 섹션을 더 깊이 전개하세요.",
        f"4. **소제목** — ## (H2) 사용, {heading_range}개 (경쟁사 평균 {avg_headings:.0f}개)",
        "5. **문단** — 1문단 80~150자 (모바일 가독성)",
        f"6. **톤** — {tone_desc}",
        f"7. **전달 방식** — {style_desc}",
        "8. **구조 다양성** — 아래 구조 유형 중 전달 방식과 키워드 특성에 맞는 것을 선택하세요. "
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

    # 포맷 다양화 규칙 추가
    lines.append(_build_format_diversity_rules(previous_structures))

    return "\n".join(lines)


def _parse_title_tags_body(content):
    """Claude 출력에서 TITLE 후보들, TAGS, 본문을 분리합니다.

    지원 포맷:
      TITLE1: / TITLE2: / TITLE3: (기본)
      TITLE: (하위 호환 — 단일 제목)
      제목 1: / 제목1: / 제목 후보 1: (한글 변형)
      **TITLE1:** / **제목:** (볼드 래핑)
      - TITLE1: (리스트 형태)
      1. 제목 (번호 리스트)
    반환: (titles_list, tags, body) — titles_list는 1~3개 제목 리스트
    """
    titles = []
    tags = []
    body = content

    lines = content.split("\n")
    body_start = 0
    meta_end = 0  # 메타데이터(제목/태그/구분선)가 끝나는 위치

    for i, line in enumerate(lines):
        stripped = line.strip()
        # 볼드(**) 래핑 제거
        clean = re.sub(r'\*\*', '', stripped).strip()
        # 리스트 마커(- , * ) 제거
        clean = re.sub(r'^[-*]\s+', '', clean).strip()

        # TITLE / TITLE1~3 행 (영문)
        if re.match(r'^TITLE\s*\d*\s*[:\-]\s*', clean, re.IGNORECASE):
            t = re.split(r'^TITLE\s*\d*\s*[:\-]\s*', clean, flags=re.IGNORECASE)[-1].strip()
            if t:
                titles.append(t)
            meta_end = i + 1
            continue

        # 한글 변형: "제목", "제목 1", "제목 후보 1" 등
        kr_match = re.match(r'^제목\s*(?:후보\s*)?\d*\s*[:\-]\s*(.+)', clean)
        if kr_match:
            t = kr_match.group(1).strip()
            if t and len(t) >= 5:
                titles.append(t)
            meta_end = i + 1
            continue

        # TAGS / 태그 행
        if re.match(r'^(?:TAGS|태그)\s*[:\-]', clean, re.IGNORECASE):
            raw_tags = re.split(r'^(?:TAGS|태그)\s*[:\-]\s*', clean, flags=re.IGNORECASE)[-1].strip()
            tags = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]
            meta_end = i + 1
            continue

        # --- 구분선 → 이후가 본문
        if stripped in ("---", "***", "___"):
            meta_end = i + 1
            break

        # 비공백 행이 메타데이터 패턴이 아니면 본문 시작
        if stripped:
            # 아직 제목/태그를 하나도 못 찾았으면 좀 더 탐색 (최대 10행)
            if not titles and not tags and i < 10:
                continue
            meta_end = i
            break

    body_start = meta_end
    body = "\n".join(lines[body_start:]).strip()

    # 폴백: 본문에서 제목 추출 시도 (첫 번째 # 헤더를 제목으로)
    if not titles and body:
        h1_match = re.match(r'^#\s+(.+)$', body, re.MULTILINE)
        if h1_match:
            titles.append(h1_match.group(1).strip())
            body = body[h1_match.end():].strip()

    return titles, tags, body


def _build_competitor_title_hint(competitor_titles):
    """경쟁사 제목을 프롬프트 힌트로 변환"""
    if not competitor_titles:
        return ""
    examples = "\n".join(f"  · {t}" for t in competitor_titles[:5])
    return f"\n- 경쟁사 상위글 제목 참고 (차별화하되 후킹 패턴은 학습):\n{examples}"


def _build_tag_hint(competitor_tags):
    """경쟁사 태그를 프롬프트 힌트로 변환"""
    if not competitor_tags:
        return ""
    tags_str = ", ".join(competitor_tags[:10])
    return f"\n- 경쟁사 상위글 공통 태그 참고: {tags_str}"


def generate_content(keyword, analysis_path, output_dir):
    """claude -p로 SEO 원고 생성"""
    claude_cmd = find_claude_cmd()
    if not claude_cmd:
        print("ERROR: claude CLI가 설치되지 않았습니다.")
        sys.exit(1)

    analysis_summary = load_analysis(analysis_path)
    analysis_data = _load_analysis_json(analysis_path)
    writing_strategy = load_writing_strategy(analysis_data)
    competitor_tags = load_competitor_tags(analysis_data)
    competitor_titles = load_competitor_titles(analysis_data)
    content_analysis = load_content_analysis(analysis_data)
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

    content_block = ""
    if content_analysis:
        parts = []
        must = content_analysis.get("must_cover_topics", [])
        unique = content_analysis.get("unique_topics", [])
        outlines = content_analysis.get("content_outlines", [])

        if must:
            parts.append(f"**필수 주제** (경쟁사 과반수가 다루는 주제 — 반드시 포함): {', '.join(must[:15])}")
        if unique:
            parts.append(f"**차별화 기회** (소수만 다루는 주제 — 1~2개 선택하여 차별화): {', '.join(unique[:10])}")
        if outlines:
            parts.append("**경쟁사 콘텐츠 구조** (각 글이 실제로 다루는 내용):")
            for i, outline in enumerate(outlines[:5], 1):
                parts.append(f"  글 {i}: {outline['title'][:40]}")
                for sec in outline["sections"][:4]:
                    parts.append(f"    - [{sec['heading']}] {sec['summary'][:100]}")

        content_block = "\n## 경쟁사 콘텐츠 분석\n이 키워드의 상위 노출 글들이 실제로 다루는 내용입니다. 이를 참고하여 **동일한 수준 이상의 정보를 포함**하되, 구성과 관점에서 차별화하세요.\n\n" + "\n".join(parts)

    prompt = f"""당신은 네이버 블로그 SEO 전문 작가입니다.

먼저 아래 파일을 읽어주세요:
1. {seo_guide_path} — SEO 작성 가이드
{medical_instruction}

{analysis_block}
{content_block}

## 작업
'{keyword}' 키워드에 최적화된 네이버 블로그 원고를 작성하세요.

## 핵심 규칙
1. **정보성 글만 작성** — 후기성/광고성 글 금지
2. **키워드 '{keyword}'를 자연스럽게 삽입**
   - 첫 문단 50자 이내에 첫 등장
   - 소제목 2개 이상에 포함
   - **마지막 문단에 반드시 키워드 1회 포함** (검증 항목)
{_build_keyword_density_guide(keyword, writing_strategy)}
{_build_writing_rules(writing_strategy, previous_structures)}

## 출력 형식
아래 형식으로 출력하세요. 설명, 주석, 코드블록 래핑 없이 바로 출력합니다.

```
TITLE1: 제목 후보 1
TITLE2: 제목 후보 2
TITLE3: 제목 후보 3
TAGS: 태그1, 태그2, 태그3, ... (8~15개, 메인 키워드 + 롱테일 변형 + 지역명/업종)
---
## 소제목1
본문 ...
```

**제목 규칙:**
- 제목 후보를 **반드시 3개** 출력 (TITLE1, TITLE2, TITLE3)
- 각 제목은 30~40자 이내
- 메인 키워드 '{keyword}'를 앞쪽에 배치
- 3개의 제목은 서로 다른 후킹 전략을 사용:
  · 하나는 호기심/질문 유발형 (예: "~, 이것만은 꼭 알고 가세요")
  · 하나는 실용/정보형 (예: "~ 총정리|완벽 가이드")
  · 하나는 FOMO/경고형 (예: "~ 모르면 손해|놓치면 안 되는")
- 경쟁사 제목과 차별화하되, 검증된 후킹 패턴은 참고{_build_competitor_title_hint(competitor_titles)}

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
    if content_analysis:
        must = content_analysis.get("must_cover_topics", [])
        outlines = content_analysis.get("content_outlines", [])
        print(f"  콘텐츠 분석: 필수 주제 {len(must)}개, 경쟁사 아웃라인 {len(outlines)}건")
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
    titles, tags, body = _parse_title_tags_body(content)

    if not titles:
        print("  WARNING: 제목(TITLE:)이 파싱되지 않았습니다. Claude 출력 형식을 확인하세요.")
    if not tags:
        print("  WARNING: 태그(TAGS:)가 파싱되지 않았습니다. Claude 출력 형식을 확인하세요.")

    # 첫 번째 제목을 기본 선택으로 사용
    title = titles[0] if titles else ""

    # 저장
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "seo-content.md")
    meta_path = os.path.join(output_dir, "seo-meta.json")

    def _save_and_report(title, tags, body):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(body)
        meta = {"title": title, "title_candidates": titles, "tags": tags}
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        plain = re.sub(r'\[IMAGE:[^\]]+\]', '', body)
        plain = re.sub(r'^#{1,3}\s+', '', plain, flags=re.MULTILINE)
        cc = count_chars(plain)
        if len(titles) > 1:
            print(f"\n  제목 후보:")
            for idx, t in enumerate(titles, 1):
                marker = " ← 기본" if idx == 1 else ""
                print(f"    {idx}. {t}{marker}")
        else:
            print(f"\n  제목: {title}")
        print(f"  태그: {len(tags)}개 — {', '.join(tags[:5])}{'...' if len(tags) > 5 else ''}")
        print(f"  글자수: {cc}자")
        return cc

    _save_and_report(title, tags, body)

    # --- 내부 검증 + 재시도 (B등급 미만이면 최대 2회 자동 수정) ---
    _GRADE_RANK = {"A": 0, "B": 1, "C": 2, "D": 3}
    max_retries = 2

    for retry in range(max_retries):
        val_result = _validate(output_path, keyword, analysis_path, skip_images=True, quiet=True)
        grade = val_result.get("grade", "D")
        val_issues = val_result.get("issues", [])
        val_warnings = val_result.get("warnings", [])

        retry_label = f" (수정 {retry}회차)" if retry > 0 else ""
        print(f"  내부 검증{retry_label}: {grade}등급 (issue {len(val_issues)}건, warning {len(val_warnings)}건)")

        # B등급 이상이면 수정 불필요
        if _GRADE_RANK.get(grade, 3) <= 1:
            break

        if not val_issues:
            break
        print("-" * 50)
        print(f"  등급 미달(B 미만) — 자동 수정 시도 ({retry + 1}/{max_retries})...")
        for issue in val_issues:
            print(f"    ❌ {issue}")
        for w in val_warnings:
            print(f"    ⚠ {w}")

        # 수정 프롬프트 구성
        feedback_lines = "\n".join(f"- {i}" for i in val_issues)
        warning_lines = "\n".join(f"- {w}" for w in val_warnings) if val_warnings else "없음"

        fix_prompt = f"""아래는 SEO 블로그 원고입니다. 검증 결과 B등급 미만입니다.
모든 issue를 해결하고, warning도 가능한 한 해결하여 B등급 이상을 달성하세요.

## 현재 원고
```
{body}
```

## 수정 필요 사항 (반드시 해결 — issue 0건이 되어야 B등급)
{feedback_lines}

## 개선 권장 사항 (해결하면 A등급)
{warning_lines}

## 수정 규칙
- 원고의 전체 구조와 소제목은 유지하되, 지적된 문제만 수정하세요.
- 글자수 부족 시: 기존 섹션의 내용을 더 깊이 전개하세요 (새 섹션 추가보다 기존 섹션 보강).
- 키워드 과다 시: 키워드를 자연어 표현이나 대명사로 대체하여 밀도를 낮추세요.
- 키워드 부족 시: 자연스러운 문맥에서 키워드를 추가 삽입하세요.
- 마지막 문단에 키워드 '{keyword}'를 반드시 1회 포함하세요.
- 설명, 주석, 코드블록 래핑 없이 수정된 원고 본문만 출력하세요.
"""

        fix_result = subprocess.run(
            [claude_cmd, "-p"],
            input=fix_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
            env=env,
        )

        if fix_result.returncode != 0:
            print("  수정 실패 — 원본 유지")
            break

        fixed_body = strip_codeblock(fix_result.stdout)

        # Claude가 TITLE/TAGS를 다시 출력했을 수 있으므로 파싱
        _fix_titles, _fix_tags, fixed_body_clean = _parse_title_tags_body(fixed_body)
        if fixed_body_clean:
            fixed_body = fixed_body_clean
        # 수정본에서 새 제목/태그가 나왔으면 업데이트
        if _fix_titles:
            titles = _fix_titles
            title = titles[0]
        if _fix_tags:
            tags = _fix_tags

        # 수정본이 원본보다 너무 짧으면 무시
        fixed_plain = re.sub(r'\[IMAGE:[^\]]+\]', '', fixed_body)
        fixed_plain = re.sub(r'^#{1,3}\s+', '', fixed_plain, flags=re.MULTILINE)
        fixed_chars = count_chars(fixed_plain)
        orig_plain = re.sub(r'\[IMAGE:[^\]]+\]', '', body)
        orig_plain = re.sub(r'^#{1,3}\s+', '', orig_plain, flags=re.MULTILINE)
        orig_chars = count_chars(orig_plain)

        if fixed_chars < orig_chars * 0.8:
            print(f"  수정본이 너무 짧음 ({fixed_chars}자 < 원본 80%) — 원본 유지")
            break

        # 수정본 재검증
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(fixed_body)
        val2 = _validate(output_path, keyword, analysis_path, skip_images=True, quiet=True)
        grade2 = val2.get("grade", "D")

        rank2 = _GRADE_RANK.get(grade2, 3)
        rank1 = _GRADE_RANK.get(grade, 3)
        issues2 = len(val2.get("issues", []))
        if rank2 > rank1 or (rank2 == rank1 and issues2 >= len(val_issues)):
            # 수정본이 원본보다 나쁘거나 개선 없으면 원본 유지
            print(f"  수정본 등급: {grade2} (개선 없음 — 원본 유지)")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(body)
            break
        else:
            body = fixed_body
            print(f"  수정본 등급: {grade2} (개선됨!)")
            _save_and_report(title, tags, body)
            grade = grade2

    print(f"  최종 등급: {grade}")
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
