"""
SEO 원고 검증 스크립트

작성된 SEO 콘텐츠가 상위노출 기준을 충족하는지 검증합니다.
분석 결과(competitor-analysis.json)가 있으면 상위글 평균과 비교합니다.

Usage:
  python validate_seo.py \
    --content output/keyword/content/seo-content.md \
    --keyword "웨스턴돔다이어트" \
    --analysis output/keyword/analysis/competitor-analysis.json
"""

import os
import re
import json
import argparse

from utils import count_chars


def validate(content_path, keyword, analysis_path=None, skip_images=False, quiet=False):
    with open(content_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # 이미지 마커 제거한 순수 텍스트
    plain = re.sub(r'\[IMAGE:[^\]]+\]', '', raw)
    plain_no_md = re.sub(r'^#{1,3}\s+', '', plain, flags=re.MULTILINE)

    char_count = count_chars(plain_no_md)

    # 키워드 분석 (대소문자 무시)
    kw_count = plain_no_md.lower().count(keyword.lower())
    kw_char_len = count_chars(keyword)
    kw_density = round(kw_char_len * kw_count / char_count * 100, 2) if char_count else 0

    # 첫 키워드 위치 (대소문자 무시)
    first_idx = plain_no_md.lower().find(keyword.lower())
    first_pos = count_chars(plain_no_md[:first_idx]) if first_idx >= 0 else None

    # 소제목
    headings = re.findall(r'^##\s+(.+)$', raw, re.MULTILINE)
    kw_lower = keyword.lower()
    kw_nospace = keyword.replace(' ', '').lower()
    kw_in_headings = sum(1 for h in headings if kw_lower in h.lower() or kw_nospace in h.lower())

    # 롱테일 키워드 (키워드를 분리한 부분 매칭)
    # 예: "웨스턴돔다이어트" → "웨스턴돔", "다이어트"
    keyword_parts = []
    if len(keyword) > 4:
        # 한글 복합어 분리 시도
        for i in range(2, len(keyword) - 1):
            part1, part2 = keyword[:i], keyword[i:]
            if len(part1) >= 2 and len(part2) >= 2:
                if plain_no_md.count(part1) > kw_count or plain_no_md.count(part2) > kw_count:
                    keyword_parts.append((part1, plain_no_md.count(part1)))
                    keyword_parts.append((part2, plain_no_md.count(part2)))
                    break

    # 이미지 마커 수
    image_markers = re.findall(r'\[IMAGE:[^\]]+\]', raw)
    image_count = len(image_markers)

    # 문단 분석
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', plain_no_md) if p.strip() and not p.strip().startswith('[')]
    para_lengths = [count_chars(p) for p in paragraphs]
    avg_para_len = round(sum(para_lengths) / max(len(para_lengths), 1))

    # 상위글 분석 데이터 로드
    competitor = None
    if analysis_path and os.path.isfile(analysis_path):
        with open(analysis_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            competitor = data.get("averages", {})

    # === 검증 결과 ===
    issues = []
    warnings = []
    passed = []

    # 1. 글자수
    target_min = 2000
    target_max = 3000
    if competitor:
        comp_avg = competitor.get("avg_char_count", 0)
        if comp_avg > 0:
            target_min = max(int(comp_avg * 0.9), 1500)
            target_max = max(int(comp_avg * 1.5), target_min + 500, 3000)

    if char_count < target_min:
        issues.append(f"글자수 부족: {char_count}자 (최소 {target_min}자 필요, {target_min - char_count}자 추가 필요)")
    elif char_count > target_max:
        warnings.append(f"글자수 과다: {char_count}자 (권장 {target_max}자 이하)")
    else:
        passed.append(f"글자수: {char_count}자 (기준: {target_min}~{target_max}자)")

    # 2. 키워드 밀도
    if kw_density < 1.0:
        issues.append(f"키워드 밀도 부족: {kw_density}% (최소 1.0% 필요, 키워드 추가 삽입 필요)")
    elif kw_density > 4.0:
        issues.append(f"키워드 과다(스터핑 위험): {kw_density}% (4% 이하로 줄이세요)")
    elif kw_density < 1.5:
        warnings.append(f"키워드 밀도 낮음: {kw_density}% (1.5~3% 권장)")
    else:
        passed.append(f"키워드 밀도: {kw_density}% (기준: 1.5~3%)")

    # 3. 첫 키워드 위치
    if first_pos is None:
        issues.append("키워드가 본문에 없습니다!")
    elif first_pos > 100:
        issues.append(f"첫 키워드 위치 늦음: {first_pos}자 (100자 이내 필요)")
    elif first_pos > 50:
        warnings.append(f"첫 키워드 위치: {first_pos}자 (50자 이내가 이상적)")
    else:
        passed.append(f"첫 키워드 위치: {first_pos}자 (기준: 100자 이내)")

    # 4. 소제목
    target_headings = 4
    if competitor:
        target_headings = max(int(competitor.get("avg_heading_count", 4)), 3)

    if len(headings) < 3:
        issues.append(f"소제목 부족: {len(headings)}개 (최소 3개 필요)")
    elif len(headings) > 7:
        warnings.append(f"소제목 과다: {len(headings)}개 (5개 이하 권장)")
    else:
        passed.append(f"소제목: {len(headings)}개 (기준: 3~5개)")

    # 5. 소제목 내 키워드
    if kw_in_headings == 0:
        issues.append("소제목에 키워드가 없습니다 (최소 1~2개 포함 필요)")
    elif kw_in_headings >= 2:
        passed.append(f"소제목 내 키워드: {kw_in_headings}개")
    else:
        warnings.append(f"소제목 내 키워드: {kw_in_headings}개 (2개 이상 권장)")

    # 6. 이미지 수 (skip_images=True일 때 건너뜀 — Phase 2 삽입 전 검증용)
    if not skip_images:
        target_images = 7
        if competitor:
            target_images = max(int(competitor.get("avg_image_count", 7)), 5)

        if image_count < 5:
            issues.append(f"이미지 부족: {image_count}장 (최소 5장 필요)")
        elif image_count < target_images:
            warnings.append(f"이미지 보강 권장: {image_count}장 (상위글 평균 {target_images}장)")
        else:
            passed.append(f"이미지: {image_count}장 (기준: {target_images}장)")

    # 7. 마지막 문단 키워드
    last_para = paragraphs[-1] if paragraphs else ""
    if kw_lower not in last_para.lower():
        warnings.append("마무리 문단에 키워드 없음 (마지막 문단에 1회 삽입 권장)")
    else:
        passed.append("마무리 키워드: 포함")

    # 8. 문단 길이
    long_paras = [l for l in para_lengths if l > 200]
    if long_paras:
        warnings.append(f"긴 문단 {len(long_paras)}개 (200자 초과 — 분리 권장)")

    # === 등급 산출 ===
    score = len(passed)
    total = len(passed) + len(issues) + len(warnings)
    grade = "A" if not issues and not warnings else "B" if not issues else "C" if len(issues) <= 2 else "D"

    # === 출력 (quiet=True이면 생략 — 내부 검증용) ===
    if not quiet:
        print("=" * 55)
        print(f"  SEO 검증: '{keyword}'")
        print("=" * 55)

        print(f"\n📊 기본 지표")
        print(f"  글자수: {char_count}자")
        print(f"  키워드 출현: {kw_count}회")
        print(f"  키워드 밀도: {kw_density}%")
        print(f"  첫 키워드: {first_pos}자 위치")
        print(f"  소제목: {len(headings)}개 (키워드 포함 {kw_in_headings}개)")
        print(f"  이미지 마커: {image_count}개")
        print(f"  평균 문단 길이: {avg_para_len}자")

        if competitor:
            print(f"\n📈 상위글 평균")
            print(f"  글자수: {competitor.get('avg_char_count', 'N/A')}자")
            print(f"  소제목: {competitor.get('avg_heading_count', 'N/A')}개")
            print(f"  이미지: {competitor.get('avg_image_count', 'N/A')}장")

        if issues:
            print(f"\n❌ 수정 필요 ({len(issues)}건)")
            for item in issues:
                print(f"  - {item}")

        if warnings:
            print(f"\n⚠️ 개선 권장 ({len(warnings)}건)")
            for item in warnings:
                print(f"  - {item}")

        if passed:
            print(f"\n✅ 통과 ({len(passed)}건)")
            for item in passed:
                print(f"  - {item}")

        print(f"\n{'=' * 55}")
        print(f"  종합 등급: {grade} ({score}/{total} 통과)")
        print(f"{'=' * 55}")

    # JSON 결과 저장
    result = {
        "keyword": keyword,
        "char_count": char_count,
        "keyword_count": kw_count,
        "keyword_density_pct": kw_density,
        "first_keyword_position": first_pos,
        "heading_count": len(headings),
        "keyword_in_headings": kw_in_headings,
        "image_count": image_count,
        "grade": grade,
        "issues": issues,
        "warnings": warnings,
        "passed": passed,
    }

    if not quiet:
        result_path = os.path.join(os.path.dirname(content_path), "seo-validation.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n결과 저장: {result_path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="SEO 원고 검증")
    parser.add_argument("--content", required=True, help="SEO 콘텐츠 마크다운 파일")
    parser.add_argument("--keyword", required=True, help="타겟 키워드")
    parser.add_argument("--analysis", help="경쟁사 분석 JSON (상위글 평균 비교용)")
    parser.add_argument("--skip-images", action="store_true", help="이미지 수 검증 건너뛰기 (Phase 2 전 검증용)")
    args = parser.parse_args()

    validate(args.content, args.keyword, args.analysis, skip_images=args.skip_images)


if __name__ == "__main__":
    main()
