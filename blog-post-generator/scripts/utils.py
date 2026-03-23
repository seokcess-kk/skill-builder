"""공통 유틸리티 함수"""

import re
import shutil


def find_claude_cmd():
    """claude CLI 실행 경로 (Windows: claude.cmd)"""
    for name in ("claude.cmd", "claude"):
        path = shutil.which(name)
        if path:
            return path
    return None


def count_chars(text):
    """공백 제외 글자수"""
    return len(re.sub(r'\s', '', text))


def strip_codeblock(text):
    """Claude 응답에서 마크다운 코드블록 래핑 제거"""
    text = text.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown"):].strip()
    if text.startswith("```html"):
        text = text[len("```html"):].strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


# 업종 감지 키워드 맵
INDUSTRY_KEYWORDS = {
    "medical": [
        "한의원", "병원", "의원", "치과", "피부과", "클리닉",
        "한약", "시술", "치료", "정형외과", "안과", "내과",
        "성형", "약국",
    ],
    "beauty": ["뷰티", "피부관리", "에스테틱", "네일", "헤어", "미용실", "화장품", "스킨케어"],
    "education": ["학원", "과외", "교육", "입시", "공부", "강의", "수업", "코딩", "영어"],
    "food": ["맛집", "카페", "레스토랑", "배달", "음식", "식당", "베이커리", "디저트"],
    "fitness": ["헬스", "필라테스", "요가", "PT", "다이어트", "피트니스", "운동", "크로스핏", "gym"],
}


def detect_industry(keyword):
    """키워드에서 업종을 자동 감지합니다."""
    keyword_lower = keyword.lower()
    for industry, terms in INDUSTRY_KEYWORDS.items():
        for term in terms:
            if term.lower() in keyword_lower:
                return industry
    return None


def detect_medical(keyword):
    """의료 업종 키워드 감지 (detect_industry의 편의 래퍼)"""
    return detect_industry(keyword) == "medical"
