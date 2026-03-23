"""
네이버 블로그 상위글 분석 스크립트

크롤링된 블로그 원문 텍스트(JSON)를 입력받아
구조/키워드/이미지/톤 패턴을 분석합니다.

Usage:
  python analyze_competitors.py \
    --input competitor-pages.json \
    --keyword "일산다이어트한의원" \
    --output-dir output/keyword/analysis/

Input JSON 포맷:
[
  {
    "url": "https://blog.naver.com/...",
    "title": "글 제목",
    "text": "본문 전체 텍스트",
    "headings": ["소제목1", "소제목2"],
    "image_count": 5,
    "image_alts": ["alt1", "alt2"],
    "image_details": [{"alt": "", "src": "url", "width": "800", "height": "600", "context": "주변텍스트"}]
  }
]
"""

import os
import re
import json
import argparse
from collections import Counter

from utils import count_chars


def count_keyword(text, keyword):
    """키워드 출현 횟수 (대소문자 무시)"""
    return text.lower().count(keyword.lower())


def keyword_density(text, keyword):
    """키워드 밀도 (%)"""
    total = count_chars(text)
    if total == 0:
        return 0
    kw_chars = count_chars(keyword) * count_keyword(text, keyword)
    return round(kw_chars / total * 100, 2)


def first_keyword_position(text, keyword):
    """키워드 첫 등장 위치 (글자수 기준)"""
    idx = text.lower().find(keyword.lower())
    if idx < 0:
        return None
    return count_chars(text[:idx])


def split_paragraphs(text):
    """문단 분리"""
    paras = re.split(r'\n\s*\n', text.strip())
    return [p.strip() for p in paras if p.strip()]


def detect_tone(text):
    """문체 감지 (간이)"""
    formal_endings = len(re.findall(r'(?:습니다|입니다|됩니다|있습니다|었습니다|겠습니다)[.!?\s]', text))
    casual_endings = len(re.findall(r'(?:해요|에요|이에요|거에요|예요|나요|세요|죠)[.!?\s]', text))
    banmal_endings = len(re.findall(r'(?:한다|된다|있다|없다|이다|같다|보자|하자)[.!?\s]', text))

    total = formal_endings + casual_endings + banmal_endings
    if total == 0:
        return "unknown"

    scores = {
        "formal": formal_endings / total,
        "polite_casual": casual_endings / total,
        "banmal": banmal_endings / total,
    }
    return max(scores, key=scores.get)


def detect_style(text, headings):
    """전달 방식 감지"""
    question_count = len(re.findall(r'[?？]', text))
    list_count = len(re.findall(r'(?:^\d+[.)]\s|^[-•]\s)', text, re.MULTILINE))
    heading_questions = sum(1 for h in headings if '?' in h or '？' in h)

    if heading_questions >= 2 or question_count >= 5:
        return "qa"
    if list_count >= 5:
        return "list"
    return "narrative"


def _classify_single_image(alt, src, width, height, context, position, total):
    """단일 이미지 분류 (ALT + URL + 크기 + 문맥 + 위치 복합 분석)"""
    alt_lower = alt.lower() if alt else ""
    src_lower = src.lower() if src else ""

    # 1. ALT 텍스트 키워드 (ALT는 이미지 자체를 설명하므로 넓은 키워드 허용)
    if any(w in alt_lower for w in [
        "원장", "의사", "진료", "상담", "치료", "시술", "환자",
        "사진", "photo", "촬영", "선생님", "대표원장", "스탭",
    ]):
        return "real_photo"
    if any(w in alt_lower for w in [
        "시설", "원내", "내부", "공간", "대기실", "접수", "인테리어",
        "건물", "외관", "로비", "복도", "층", "입구",
    ]):
        return "facility_photo"
    if any(w in alt_lower for w in [
        "인포", "단계", "과정", "프로세스", "비교", "전후",
        "차트", "그래프", "도표", "통계", "before", "after",
    ]):
        return "infographic"
    if any(w in alt_lower for w in [
        "일러스트", "그림", "만화", "캐릭터", "아이콘",
    ]):
        return "illustration"
    if any(w in alt_lower for w in [
        "제품", "약", "한약", "장비", "기구", "도구", "기기",
        "화장품", "크림", "앰플", "세럼",
    ]):
        return "product_photo"
    if any(w in alt_lower for w in [
        "음식", "식단", "요리", "레시피", "식사", "메뉴",
        "운동", "스트레칭", "요가", "필라테스", "헬스",
    ]):
        return "lifestyle_photo"

    # 2. 문맥 키워드 (context는 주변 텍스트이므로 오매칭 방지를 위해 보수적으로 매칭)
    ctx_lower = context.lower() if context else ""
    if any(w in ctx_lower for w in ["원장", "의사", "의료진", "진료", "시술", "치료사"]):
        return "real_photo"
    if any(w in ctx_lower for w in ["시설", "원내", "내부", "대기실", "인테리어", "외관"]):
        return "facility_photo"
    if any(w in ctx_lower for w in ["단계", "과정", "프로세스", "비교", "전후"]):
        return "infographic"
    if any(w in ctx_lower for w in ["제품", "장비", "기구", "기기"]):
        return "product_photo"
    if any(w in ctx_lower for w in ["식단", "운동", "스트레칭", "요가", "필라테스"]):
        return "lifestyle_photo"

    # 3. URL 패턴 기반
    if "storep" in src_lower or "shopping" in src_lower:
        return "product_photo"

    # 4. 크기/비율 기반 휴리스틱
    try:
        w, h = int(width), int(height)
        if h > 0:
            ratio = w / h
            if ratio > 2.0:  # 매우 와이드 → 배너/시설 파노라마
                return "facility_photo"
            if ratio < 0.6:  # 세로형 → 인포그래픽 가능성
                return "infographic"
    except (ValueError, TypeError):
        pass

    # 5. 위치 기반 휴리스틱 (이미지 8장 이상, 다른 신호 모두 실패 시 약한 추정)
    if total >= 8:
        if position == 0:
            return "facility_photo"  # 첫 1장: 대표/시설 사진 가능성
        if position == total - 1:
            return "real_photo"  # 마지막 1장: 상담/CTA 사진

    return "unknown"


def guess_image_types(image_data):
    """이미지 유형 추정 (다중 신호 복합 분석)

    image_data: image_details 리스트(dict) 또는 image_alts 리스트(str) 지원
    """
    types = []
    total = len(image_data)

    for i, item in enumerate(image_data):
        # 구형 포맷 (ALT 문자열 리스트) 호환
        if isinstance(item, str):
            img_type = _classify_single_image(
                alt=item, src="", width="", height="",
                context="", position=i, total=total,
            )
        else:
            img_type = _classify_single_image(
                alt=item.get("alt", ""),
                src=item.get("src", ""),
                width=item.get("width", ""),
                height=item.get("height", ""),
                context=item.get("context", ""),
                position=i,
                total=total,
            )
        types.append(img_type)

    return types


def analyze_single(page, keyword):
    """개별 페이지 분석"""
    text = page.get("text", "")
    title = page.get("title", "")
    headings = page.get("headings", [])
    image_count = page.get("image_count", 0)
    image_alts = page.get("image_alts", [])

    paragraphs = split_paragraphs(text)
    char_count = count_chars(text)
    kw_count = count_keyword(text, keyword)
    kw_density = keyword_density(text, keyword)
    kw_in_title = keyword.lower() in title.lower()
    kw_first_pos = first_keyword_position(text, keyword)

    # 키워드가 포함된 소제목 수
    kw_in_headings = sum(1 for h in headings if keyword.lower() in h.lower())

    # 이미지 유형 추정 (image_details 우선, 없으면 image_alts fallback)
    image_details = page.get("image_details", [])
    img_data = image_details if image_details else image_alts
    img_types = guess_image_types(img_data)
    img_type_dist = dict(Counter(img_types))

    return {
        "url": page.get("url", ""),
        "title": title,
        "char_count": char_count,
        "paragraph_count": len(paragraphs),
        "avg_paragraph_length": round(char_count / max(len(paragraphs), 1)),
        "heading_count": len(headings),
        "headings": headings,
        "image_count": image_count,
        "image_type_distribution": img_type_dist,
        "keyword_count": kw_count,
        "keyword_density_pct": kw_density,
        "keyword_in_title": kw_in_title,
        "keyword_first_position": kw_first_pos,
        "keyword_in_headings": kw_in_headings,
        "tone": detect_tone(text),
        "style": detect_style(text, headings),
        "tags": page.get("tags", []),
    }


def compute_averages(analyses):
    """전체 분석의 평균 도출"""
    n = len(analyses)
    if n == 0:
        return {}

    def avg(key):
        vals = [a[key] for a in analyses if a[key] is not None]
        return round(sum(vals) / max(len(vals), 1), 1) if vals else 0

    # 톤/스타일 분포
    tone_dist = dict(Counter(a["tone"] for a in analyses))
    style_dist = dict(Counter(a["style"] for a in analyses))

    # 이미지 유형 합산
    all_img_types = Counter()
    for a in analyses:
        all_img_types.update(a["image_type_distribution"])
    total_imgs = sum(all_img_types.values()) or 1
    img_type_pct = {k: round(v / total_imgs * 100) for k, v in all_img_types.items()}

    # 공통 소제목 키워드 추출
    all_heading_words = []
    for a in analyses:
        for h in a["headings"]:
            words = re.findall(r'[\w가-힣]+', h)
            all_heading_words.extend(words)
    common_heading_words = [w for w, c in Counter(all_heading_words).most_common(15) if c >= 2 and len(w) >= 2]

    # 태그 집계
    all_tags = []
    for a in analyses:
        all_tags.extend(a.get("tags", []))
    tag_counts = Counter(all_tags)
    recommended_tags = [t for t, c in tag_counts.most_common(20) if c >= 2 and len(t) >= 2]
    tag_frequency = {t: c for t, c in tag_counts.most_common(30)}

    return {
        "sample_count": n,
        "avg_char_count": avg("char_count"),
        "avg_paragraph_count": avg("paragraph_count"),
        "avg_paragraph_length": avg("avg_paragraph_length"),
        "avg_heading_count": avg("heading_count"),
        "avg_image_count": avg("image_count"),
        "avg_keyword_density_pct": avg("keyword_density_pct"),
        "avg_keyword_count": avg("keyword_count"),
        "keyword_in_title_ratio": round(sum(1 for a in analyses if a["keyword_in_title"]) / n * 100),
        "tone_distribution": tone_dist,
        "style_distribution": style_dist,
        "image_type_distribution_pct": img_type_pct,
        "common_heading_keywords": common_heading_words,
        "recommended_tags": recommended_tags,
        "tag_frequency": tag_frequency,
    }


def _build_image_strategy(averages):
    """경쟁사 분석 기반 이미지 전략 권장사항 생성"""
    avg_count = averages.get("avg_image_count", 0)
    type_pct = averages.get("image_type_distribution_pct", {})

    lines = []

    # 1. 이미지 수 권장
    if avg_count >= 20:
        rec_count = "8~10"
    elif avg_count >= 10:
        rec_count = "6~8"
    elif avg_count >= 5:
        rec_count = "5~7"
    else:
        rec_count = "5~6"
    lines.append(f"- 권장 이미지 수: {rec_count}장 (경쟁사 평균 {avg_count:.0f}장)")

    # 2. 유형별 권장 비율 (unknown 제외)
    known_types = {k: v for k, v in type_pct.items() if k != "unknown"}

    if known_types:
        top_types = sorted(known_types.items(), key=lambda x: x[1], reverse=True)
        type_names = {
            "real_photo": "실사 사진(인물/상담)",
            "facility_photo": "시설/공간 사진",
            "infographic": "인포그래픽(도형/아이콘)",
            "illustration": "일러스트",
            "product_photo": "제품 사진",
            "lifestyle_photo": "라이프스타일 사진",
        }
        type_descs = [f"{type_names.get(t, t)} {p}%" for t, p in top_types[:3]]
        lines.append(f"- 주요 유형: {', '.join(type_descs)}")
    else:
        # 유형 분류가 대부분 unknown인 경우 기본 권장
        lines.append("- 권장 유형 배분: 시설/공간 사진 2~3장, 실사/상담 사진 2~3장, "
                      "인포그래픽(아이콘/도형) 1~2장, 라이프스타일 사진 1~2장")

    # 3. 배치 전략
    lines.append("- 배치: 도입부(시설/대표 이미지) → 본문(콘텐츠 관련) → 마무리(상담/CTA)")

    return "\n".join(lines)


def generate_summary(averages, keyword):
    """사람이 읽을 수 있는 요약 생성"""
    lines = [
        f"## 네이버 상위글 분석 요약: '{keyword}'",
        "",
        f"분석 대상: 상위 {averages['sample_count']}개 블로그 글",
        "",
        "### 구조 패턴",
        f"- 평균 글자수: {averages['avg_char_count']:.0f}자",
        f"- 평균 문단수: {averages['avg_paragraph_count']:.0f}개 (문단당 {averages['avg_paragraph_length']:.0f}자)",
        f"- 평균 소제목: {averages['avg_heading_count']:.0f}개",
        f"- 공통 소제목 키워드: {', '.join(averages['common_heading_keywords'][:8])}",
        "",
        "### 키워드 패턴",
        f"- 평균 키워드 밀도: {averages['avg_keyword_density_pct']}%",
        f"- 평균 키워드 출현: {averages['avg_keyword_count']:.0f}회",
        f"- 제목 내 키워드 포함: {averages['keyword_in_title_ratio']}%",
        "",
        "### 이미지 패턴",
        f"- 평균 이미지 수: {averages['avg_image_count']:.0f}장",
        f"- 유형 분포: {json.dumps(averages['image_type_distribution_pct'], ensure_ascii=False)}",
        "",
        "### 이미지 전략 권장사항",
        _build_image_strategy(averages),
        "",
        "### 톤/스타일",
        f"- 문체 분포: {json.dumps(averages['tone_distribution'], ensure_ascii=False)}",
        f"- 전달 방식: {json.dumps(averages['style_distribution'], ensure_ascii=False)}",
    ]

    # 추천 태그
    rec_tags = averages.get("recommended_tags", [])
    tag_freq = averages.get("tag_frequency", {})
    if rec_tags:
        lines.append("")
        lines.append("### 추천 태그")
        lines.append(f"- 상위글 공통 태그 (2회 이상): {', '.join(rec_tags)}")
    if tag_freq:
        top_tags = [f"{t}({c})" for t, c in list(tag_freq.items())[:10]]
        lines.append(f"- 빈도순 태그: {', '.join(top_tags)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="네이버 상위글 분석")
    parser.add_argument("--input", required=True, help="크롤링 데이터 JSON 파일")
    parser.add_argument("--keyword", required=True, help="타겟 키워드")
    parser.add_argument("--output-dir", required=True, help="분석 결과 출력 디렉토리")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        pages = json.load(f)

    print(f"분석 대상: {len(pages)}개 페이지")
    print(f"타겟 키워드: {args.keyword}")
    print("-" * 40)

    # 개별 분석
    analyses = []
    for i, page in enumerate(pages):
        result = analyze_single(page, args.keyword)
        analyses.append(result)
        print(f"[{i+1}/{len(pages)}] {result['title'][:30]}... "
              f"({result['char_count']}자, 이미지 {result['image_count']}개)")

    # 평균/패턴 도출
    averages = compute_averages(analyses)

    # 요약 텍스트
    summary_text = generate_summary(averages, args.keyword)

    # 저장
    detail_path = os.path.join(args.output_dir, "competitor-analysis.json")
    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump({
            "keyword": args.keyword,
            "averages": averages,
            "individual": analyses,
        }, f, ensure_ascii=False, indent=2)

    summary_path = os.path.join(args.output_dir, "analysis-summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print("-" * 40)
    print(summary_text)
    print("-" * 40)
    print(f"상세 결과: {detail_path}")
    print(f"요약: {summary_path}")


if __name__ == "__main__":
    main()
