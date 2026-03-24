"""
Claude CLI 기반 브랜드 섹션 HTML 자동 생성 스크립트

image-generator SKILL.md를 Claude가 직접 읽고, 레시피/액센트 모드/변형을 선택하여
섹션별 HTML을 생성합니다.

2단계 배치 생성:
  Phase 1: 브랜드 분석 + 디자인 계획 (JSON)
  Phase 2: 3~4개씩 나눠서 HTML 생성 (3번 호출)

Usage:
  python generate_brand_html.py \
    --keyword "대구다이어트한의원" \
    --brand-name "다이트한의원 대구점" \
    --homepage "https://daeatdiet.com" \
    --expert "김민수 원장, 한방 비만 전문의" \
    --output-dir output/keyword/branded/html/ \
    --manuscript "직장인 다이어트 — 바쁜 일상에서도 가능한 한방 체질 개선"
"""

import os
import sys
import re
import json
import time
import subprocess
import argparse
from pathlib import Path

from utils import find_claude_cmd, detect_medical, detect_industry, strip_codeblock, FONT_PAIRINGS, FONT_URLS, font_link_tags


ROOT = Path(__file__).parent.parent
SKILL_MD = ROOT / "skills" / "image-generator" / "SKILL.md"
VARIANT_TEMPLATES = ROOT / "skills" / "image-generator" / "references" / "variant-templates.md"
BASE_CSS = ROOT / "skills" / "image-generator" / "assets" / "base-styles.css"
CONTENT_GUIDE = ROOT / "skills" / "image-generator" / "references" / "content-guide.md"
MEDICAL_GUIDE = ROOT / "skills" / "image-generator" / "references" / "medical-ad-compliance.md"


def find_previous_designs(output_dir, brand_name):
    """같은 브랜드의 이전 디자인 계획 검색

    output/{keyword-slug}/branded/html/ 구조를 전제로
    output/*/branded/html/_design_plan.json 을 스캔합니다.
    """
    output_root = Path(output_dir).resolve().parent.parent.parent  # output/
    if not output_root.exists():
        return []

    current_dir = Path(output_dir).resolve()
    brand_lower = brand_name.lower().replace(" ", "")
    history = []

    for plan_file in sorted(output_root.glob("*/branded/html/_design_plan.json")):
        # 현재 생성 중인 디렉토리 제외
        if plan_file.parent.resolve() == current_dir:
            continue
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        # 같은 브랜드인지 판별 (brand_name > slug)
        plan_brand = plan.get("brand_name", "").lower().replace(" ", "")
        slug = plan.get("brand_slug", "").lower().replace("-", "")

        is_same_brand = False
        # 1순위: brand_name 직접 비교 (Phase 1 저장 시 추가된 필드)
        if plan_brand and (brand_lower in plan_brand or plan_brand in brand_lower):
            is_same_brand = True
        # 2순위: slug 비교 (영문 브랜드인 경우)
        elif brand_lower and slug and (brand_lower in slug or slug in brand_lower):
            is_same_brand = True

        if not is_same_brand:
            continue

        # 디자인 핵심 요소만 추출
        section_variants = {}
        for sec_key, sec_data in plan.get("sections", {}).items():
            if isinstance(sec_data, dict):
                section_variants[sec_key] = sec_data.get("variant", "?")

        history.append({
            "keyword": plan_file.parent.parent.parent.name,  # keyword-slug
            "recipe": plan.get("recipe", "?"),
            "accent_mode": plan.get("accent_mode", "?"),
            "theme": plan.get("theme", "?"),
            "section_variants": section_variants,
        })

    return history


# 섹션 배치 분할 (3~4개씩)
SECTION_BATCHES = [
    [("01", "hook"), ("02", "intro"), ("03", "pain"), ("03b", "bridge")],
    [("04", "why"), ("04b", "bridge"), ("05", "solution")],
    [("06", "proof"), ("07", "cta"), ("10", "disclaimer")],
]


def ensure_body_classes(html, theme, accent_mode):
    """Phase 2 HTML의 <body>에 theme-{theme} {accent_mode} 클래스를 보장"""
    theme_cls = f"theme-{theme}" if theme else ""
    accent_cls = accent_mode if accent_mode else ""
    required = [c for c in [theme_cls, accent_cls] if c]
    if not required:
        return html

    body_match = re.search(r'<body\b([^>]*)>', html, re.IGNORECASE)
    if not body_match:
        return html

    attrs = body_match.group(1)
    class_match = re.search(r'class="([^"]*)"', attrs)
    if class_match:
        existing = class_match.group(1).split()
        missing = [c for c in required if c not in existing]
        if not missing:
            return html
        new_classes = class_match.group(1) + " " + " ".join(missing)
        new_attrs = attrs[:class_match.start()] + f'class="{new_classes}"' + attrs[class_match.end():]
    else:
        cls_str = " ".join(required)
        new_attrs = attrs + f' class="{cls_str}"'

    return html[:body_match.start()] + f'<body{new_attrs}>' + html[body_match.end():]


def parse_sections(response_text):
    """Claude 응답에서 섹션별 HTML 분리"""
    sections = {}
    pattern = r'===SECTION:(.+?)===\s*\n(.*?)(?=\n===SECTION:|\Z)'
    matches = re.findall(pattern, response_text, re.DOTALL)
    for filename, html in matches:
        filename = filename.strip()
        html = strip_codeblock(html)
        sections[filename] = html
    return sections


def run_claude(claude_cmd, prompt, allowed_tools="Read,WebFetch", timeout=600):
    """Claude CLI 실행 후 stdout 반환"""
    cmd = [claude_cmd, "-p", "--allowedTools", allowed_tools]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    print(f"    CMD: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        print(f"ERROR: claude CLI 타임아웃 ({timeout}초)")
        return None

    if result.returncode != 0:
        print(f"ERROR: claude 실행 실패 (exit code {result.returncode})")
        if result.stdout:
            print(f"  STDOUT: {result.stdout[:300]}")
        if result.stderr:
            print(f"  STDERR: {result.stderr[:500]}")
        return None

    return result.stdout


def _build_history_block(design_history):
    """이전 디자인 이력을 프롬프트 블록으로 변환"""
    if not design_history:
        return ""

    lines = [
        "## 이전 포스트 디자인 이력 (같은 브랜드 — 반복 금지)",
        "",
        "아래는 이 브랜드의 이전 포스트에서 사용된 디자인입니다.",
        "**동일한 레시피를 재사용하지 마세요.** 액센트 모드와 섹션 변형 조합도 최대한 다르게 선택하세요.",
        "같은 사람이 만든 이미지라는 인상을 주지 않도록 구성/레이아웃/색상 운용을 차별화하세요.",
        "",
    ]
    for i, prev in enumerate(design_history[-5:], 1):
        variants = prev.get("section_variants", {})
        variant_str = ", ".join(f"{k}={v}" for k, v in variants.items())
        lines.append(
            f"  {i}. 키워드 '{prev.get('keyword', '?')}': "
            f"레시피={prev.get('recipe', '?')}, "
            f"액센트={prev.get('accent_mode', '?')}, "
            f"변형=[{variant_str}]"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def phase1_plan(claude_cmd, keyword, brand_name, homepage, expert, manuscript, is_medical,
                design_history=None):
    """Phase 1: 브랜드 분석 + 디자인 계획 (JSON 출력)"""
    skill_path = str(SKILL_MD.resolve())
    variant_path = str(VARIANT_TEMPLATES.resolve())
    css_path = str(BASE_CSS.resolve())
    content_guide_path = str(CONTENT_GUIDE.resolve())
    medical_path = str(MEDICAL_GUIDE.resolve()) if is_medical else None

    medical_instruction = ""
    if medical_path:
        medical_instruction = f"\n5. {medical_path} — 의료광고법 컴플라이언스 (반드시 준수)"

    industry = detect_industry(keyword)
    industry_names = {
        "medical": "의료/건강", "beauty": "뷰티/미용", "education": "교육",
        "food": "음식/요리", "fitness": "피트니스/운동",
    }
    industry_label = industry_names.get(industry, "일반")

    # 업종별 기본 톤 (폴백용)
    industry_default_tone = {
        "medical": "권위", "beauty": "공감", "education": "정보형",
        "food": "친근", "fitness": "임팩트",
    }

    homepage_instruction = ""
    if homepage:
        homepage_instruction = f"""
## 홈페이지 분석 (브랜드 에셋 추출)
WebFetch 도구로 {homepage} 를 읽고 아래 항목을 **실제 홈페이지에서 사용하는 값 그대로** 추출하세요.
임의로 만들어내지 마세요. 홈페이지에 없는 정보는 빈 문자열로 처리합니다.

### 필수 추출 항목
1. **브랜드 컬러**: Primary HEX, Accent HEX (로고, 헤더, 버튼에서 추출)
2. **톤앤매너**: 격식/친근/권위/공감
3. **영문 브랜드명**: 홈페이지에서 실제 사용하는 영문 표기 (예: 로고, 푸터, 메타태그에서 추출). 없으면 빈 문자열
4. **슬로건/핵심 메시지**: 메인 페이지 hero 영역 또는 meta description에서 추출
5. **연락처**: 전화번호, 주소 (홈페이지에 표기된 형식 그대로)
6. **예약/상담 채널**: 네이버 예약, 카카오톡 상담 등 홈페이지에 안내된 채널 목록
7. **전문가 정보**: 대표/원장 이름, 직함 (홈페이지에 공개된 경우만)

### 중요 원칙
- **홈페이지에 있는 에셋만 사용** — 영문 브랜드명, 슬로건, 연락처 등을 임의로 창작하지 마세요
- 홈페이지에 영문명이 "DAEATDIET"이면 "DAEATDIET"을, "Serea"이면 "Serea"를 그대로 사용
- 홈페이지에 영문명이 없으면 brand_eng 필드를 빈 문자열로 출력

**WebFetch 실패 시**: 홈페이지를 읽을 수 없는 경우, "homepage_fetched": false를 JSON에 표기하고 아래 폴백 절차를 따르세요.
"""
    else:
        homepage_instruction = f"""
## 컬러/톤 결정 (홈페이지 없음)
홈페이지 URL이 제공되지 않았습니다. 아래 절차로 결정하세요:
1. 감지 업종({industry_label})에 해당하는 팔레트 풀(SKILL.md 3-2)에서 선택
2. 키워드 '{keyword}'와 브랜드명 '{brand_name}'의 분위기에 맞는 팔레트 선택
3. 톤앤매너: 업종 기본값 '{industry_default_tone.get(industry, "친근")}' 적용
4. brand_eng, contact, channels 등 홈페이지 에셋 필드는 빈 문자열로 출력
5. JSON에 "homepage_fetched": false 표기
"""

    prompt = f"""당신은 네이버 블로그용 섹션 이미지 HTML 전문 디자이너입니다.

먼저 아래 파일들을 순서대로 읽어주세요:
1. {skill_path} — 이미지 생성 스킬 스펙 (레시피, 액센트 모드, 변형 선택 기준)
2. {css_path} — CSS 디자인 시스템
3. {variant_path} — 변형별 HTML 템플릿
4. {content_guide_path} — 콘텐츠 작성 가이드{medical_instruction}

{homepage_instruction}

## 브랜드 정보
- 브랜드명: {brand_name}
- 키워드: {keyword}
- 감지 업종: {industry_label}
- 전문가: {expert or '없음 (브랜드 소개로 대체)'}
- 원고/주제: {manuscript or keyword}

{_build_history_block(design_history)}
## 작업
SKILL.md의 Step 0~3을 실행하여 디자인 계획을 수립하세요:

1. **Step 0.5**: 홈페이지 분석 → 브랜드 컬러/톤 추출 (없으면 팔레트 풀 폴백)
2. **Step 1**: 원고 분석 → 전환 최적화 폴리싱 (각 섹션 텍스트 작성)
3. **Step 3**:
   - 3-1: 테마 자동 감지
   - 3-2b: 폰트 페어링 선택 (아래 테이블에서 업종/톤에 맞는 것 선택)
   - 3-3: 액센트 모드 선택
   - 3-4: 컴포지션 레시피 선택 (조합 설계 원칙에 따라)
   - 3-5: 섹션별 변형 결정
   - 3-6: 안티패턴 자가 점검

## 폰트 페어링 (Step 3-2b)
업종과 톤에 맞는 폰트 페어링을 선택하세요. css_overrides에 --font-display와 --font-body를 포함합니다.

| 페어링 | Display (헤드라인) | Body (본문) | 분위기 | 적합 업종 |
|--------|-------------------|-------------|--------|-----------|
| serif-classic | Noto Serif KR | Noto Sans KR | 권위/정제 | 의료/법률 (기본값) |
| modern-geo | Pretendard | Pretendard | 깨끗/현대 | IT/교육/커머스 |
| warm-mixed | MaruBuri | Pretendard | 따뜻/친근 | 뷰티/라이프스타일 |
| editorial-kr | KoPub Batang | KoPub Dotum | 매거진/고급 | 프리미엄 전반 |
| bold-impact | SUIT | SUIT | 강렬/임팩트 | 스타트업/IT |

## 변형 다양성 규칙 (중요)
- 10개 섹션에서 **최소 3종 이상의 다른 변형(A~E)**을 사용할 것 — 한 변형에 편중 금지
- 예: B를 7개 이상 사용하는 것은 금지. A 2개, B 3개, C 2개, D 2개, E 1개처럼 골고루 분배
- 특히 핵심 섹션(hook, pain, why, solution, proof)은 서로 다른 변형을 선택할 것
- 같은 브랜드의 이전 포스트 이력이 있으면 해당 변형 조합을 피할 것

## 디자인 안티패턴 자가 점검 (Step 3-6)
계획 완성 후, 아래 체크리스트로 자가 점검하세요. 위반 항목이 있으면 계획을 수정한 뒤 출력하세요.

**공통 안티패턴:**
- 헤드라인 텍스트가 680px에서 2줄 초과 (20~25자/줄 기준)
- 한 섹션에 폰트 크기 3종 초과
- 장식 요소(코너, 라인, 아이콘) 섹션당 2개 초과
- 다크 섹션 3개 초과 (전체 7개 중 — Bridge 제외)

**의료/법률 업종:**
- 비격식 이모지(✨🔥💪 등) 사용
- 최상급/보장 표현 무면책 ("최고", "100% 효과", "반드시")
- 불안 유발 빨간색 계열 악센트

**뷰티/라이프스타일:**
- 과도하게 차가운/임상적 톤
- 다크 섹션 3개 초과 (답답한 인상)
- 여성 타겟에 900 weight 무거운 산세리프

**IT/스타트업:**
- Serif 주도 레이아웃 (구식 인상)
- 파스텔만으로 구성 (강한 악센트 없음)

## 브랜드명 반복 규칙 (중요)
- **매 섹션의 headline 또는 subtext에 브랜드명('{brand_name}') 또는 키워드('{keyword}')를 1회 이상 포함**할 것
- Hook: 브랜드명 미포함 가능 (범용 인용문 형태)
- Intro: 브랜드명 필수 (headline에 포함)
- Pain~Proof: headline 또는 subtext에 브랜드명/키워드 자연스럽게 삽입
  예: "팔달구다이어트한의원 원장이 말하는 실패 원인", "[브랜드] 상담 시 확인할 항목"
- CTA: 브랜드명 필수 + 연락처
- 영문 라벨(section tag)은 보조 요소. 한글 브랜드명/키워드가 주요 텍스트에 반드시 있어야 함

## 출력 형식
반드시 아래 JSON 형식으로만 출력하세요. 설명이나 마크다운 없이 JSON만 출력합니다.

```json
{{
  "brand_slug": "brand-slug-here",
  "brand_eng": "홈페이지에서 추출한 영문 브랜드명 (없으면 빈 문자열)",
  "primary_color": "#HEXHEX",
  "accent_color": "#HEXHEX",
  "theme": "editorial|warm|clean|bold",
  "accent_mode": "accent-neutral|accent-warm|...",
  "recipe": "레시피 번호/이름",
  "font_pairing": "serif-classic|modern-geo|warm-mixed|editorial-kr|bold-impact",
  "tone": "격식|친근|권위|공감",
  "slogan": "홈페이지에서 추출한 실제 슬로건 (없으면 빈 문자열)",
  "contact": {{
    "phone": "홈페이지에 표기된 전화번호",
    "address": "홈페이지에 표기된 주소",
    "channels": ["네이버 예약", "카카오톡 상담 등 실제 안내된 채널"]
  }},
  "homepage_fetched": {"true" if homepage else "false"},
  "anti_pattern_check": {{"passed": true, "warnings": []}},
  "sections": {{
    "01-hook": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "02-intro": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "03-pain": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "03b-bridge": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "04-why": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "04b-bridge": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "05-solution": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "06-proof": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "07-cta": {{"variant": "A|B|C|D|E", "headline": "...", "subtext": "...", "body": "..."}},
    "10-disclaimer": {{"variant": "A|B|C|D|E", "items": ["면책 항목1", "면책 항목2", "..."]}}
  }},
  "css_overrides": "CSS :root 변수 오버라이드 문자열 (--c-primary: #HEX; --c-accent: #HEX; --font-display: 'FontName', serif; --font-body: 'FontName', sans-serif; ...)"
}}
```
"""

    print("  [Phase 1] 브랜드 분석 + 디자인 계획 수립 중...")
    raw = run_claude(claude_cmd, prompt)
    if not raw:
        return None, None

    # JSON 추출: ```json 블록 > 최초 { ... 최후 } > 전체 시도
    json_match = re.search(r'```json\s*\n(.*?)\n```', raw, re.DOTALL)
    if json_match:
        raw_json = json_match.group(1)
    else:
        # { ... } 블록 추출 시도
        brace_match = re.search(r'\{.*\}', raw, re.DOTALL)
        raw_json = brace_match.group(0) if brace_match else raw.strip()

    try:
        plan = json.loads(raw_json)
        print(f"    테마: {plan.get('theme', '?')}")
        print(f"    액센트 모드: {plan.get('accent_mode', '?')}")
        print(f"    레시피: {plan.get('recipe', '?')}")
        print(f"    폰트: {plan.get('font_pairing', '?')}")
        print(f"    컬러: {plan.get('primary_color', '?')} / {plan.get('accent_color', '?')}")
        brand_eng = plan.get('brand_eng', '')
        if brand_eng:
            print(f"    영문 브랜드: {brand_eng}")
        contact = plan.get('contact', {})
        if contact.get('phone'):
            print(f"    연락처: {contact.get('phone', '')} / {contact.get('address', '')}")
        print(f"    홈페이지 분석: {'성공' if plan.get('homepage_fetched', True) else '폴백 사용'}")
        ap_check = plan.get('anti_pattern_check', {})
        if ap_check.get('warnings'):
            print(f"    안티패턴 경고: {', '.join(ap_check['warnings'])}")
        return plan, raw
    except json.JSONDecodeError:
        print("ERROR: Phase 1 JSON 파싱 실패")
        return None, raw


def phase2_generate_batch(claude_cmd, plan, batch, batch_num, keyword, brand_name, is_medical):
    """Phase 2: 배치별 HTML 생성"""
    css_path = str(BASE_CSS.resolve())
    variant_path = str(VARIANT_TEMPLATES.resolve())
    medical_path = str(MEDICAL_GUIDE.resolve()) if is_medical else None

    brand_slug = plan.get("brand_slug", "brand")
    primary = plan.get("primary_color", "#333333")
    accent = plan.get("accent_color", "#666666")
    theme = plan.get("theme", "clean")
    css_overrides = plan.get("css_overrides", "")
    accent_mode = plan.get("accent_mode", "")
    font_pairing = plan.get("font_pairing", "serif-classic")
    body_classes = f"theme-{theme} {accent_mode}".strip()
    font_display, font_body = FONT_PAIRINGS.get(font_pairing, FONT_PAIRINGS["serif-classic"])
    _font_links = font_link_tags(font_pairing)

    NL = "\n"
    section_specs = []
    section_names = []
    for num, name in batch:
        key = f"{num}-{name}"
        section_names.append(key)
        sec = plan.get("sections", {}).get(key, {})
        variant = sec.get("variant", "A")
        headline = sec.get("headline", "")
        subtext = sec.get("subtext", "")
        body = sec.get("body", "")
        items = sec.get("items", [])

        spec = f"- **{key}** [필수 변형: {variant}]: headline=\"{headline}\", subtext=\"{subtext}\""
        if body:
            spec += f", body=\"{body}\""
        if items:
            spec += f", items={items}"
        section_specs.append(spec)

    medical_instruction = ""
    if medical_path:
        medical_instruction = f"\n또한 {medical_path} 의 의료광고법 컴플라이언스를 반드시 준수하세요."

    filenames_example = "\n".join(
        f"===SECTION:{brand_slug}-{num}-{name}.html===" for num, name in batch
    )

    # 브랜드 에셋 (Phase 1에서 홈페이지 추출)
    brand_eng = plan.get("brand_eng", "")
    slogan = plan.get("slogan", "")
    contact = plan.get("contact", {})
    contact_phone = contact.get("phone", "")
    contact_address = contact.get("address", "")
    contact_channels = ", ".join(contact.get("channels", []))

    brand_asset_block = f"""
## 브랜드 에셋 (홈페이지에서 추출 — 그대로 사용할 것)
- 한글 브랜드명: {brand_name}
- 영문 브랜드명: {brand_eng or '(없음 — 영문 라벨 사용하지 말 것)'}
- 슬로건: {slogan or '(없음)'}
- 전화번호: {contact_phone or '(없음)'}
- 주소: {contact_address or '(없음)'}
- 예약/상담 채널: {contact_channels or '(없음)'}

**중요**: 위 에셋은 홈페이지에서 실제 추출한 값입니다. 임의로 변형하거나 창작하지 마세요.
- 영문 브랜드명이 있으면 CTA/Disclaimer의 라벨에 사용하세요
- 영문 브랜드명이 없으면 영문 라벨을 만들지 마세요 (한글만 사용)
- 연락처/채널이 있으면 CTA에 그대로 포함하세요"""

    prompt = f"""아래 파일들을 읽어주세요:
1. {css_path} — CSS 디자인 시스템
2. {variant_path} — 변형별 HTML 템플릿{medical_instruction}
{brand_asset_block}

## 디자인 설정
- 브랜드명: {brand_name}
- 키워드: {keyword}
- 테마: {theme}
- body 클래스: `<body class="{body_classes}">`
- Primary 컬러: {primary}
- Accent 컬러: {accent}
- CSS 오버라이드: {css_overrides}

## 생성할 섹션 ({len(batch)}개)
{NL.join(section_specs)}

## 필수 규칙
- 너비 680px 고정
- **<body> 태그에 반드시 `class="{body_classes}"` 적용** — 테마 CSS가 이 클래스에 의존함
- 각 섹션의 [필수 변형: X]에 지정된 변형을 반드시 사용할 것 — 임의로 다른 변형 선택 금지
- 외부 리소스 금지 (단, 폰트 로딩 예외) — 모든 CSS는 <style> 태그 인라인
- **폰트 로딩**: <head>에 반드시 아래 링크를 포함할 것:
  {_font_links}
- base-styles.css의 CSS를 각 HTML <style>에 포함 (브랜드 컬러 교체 적용)
- word-break: keep-all 필수
- 폰트: {font_display} (헤드라인), {font_body} (본문)
- 한국어 줄바꿈: 의미 단위에서 <br> 삽입
- 전문가 사진/이미지 삽입 금지 — img 태그, placeholder 이미지, 원형 photo-box 등 어떤 형태의 이미지 placeholder도 사용하지 않음
- "BRAND", "PHOTO", "IMAGE" 같은 텍스트를 표시하는 빈 박스/원형 요소 생성 금지
- **variant-templates.md의 해당 변형 HTML 구조를 정확히 따를 것** — 임의로 구조를 변형하거나 템플릿에 없는 요소(photo-box 등)를 추가하지 않음
- 각 섹션의 레이아웃/구조가 서로 시각적으로 달라야 함 — 동일한 카드/리스트 패턴 반복 금지

## 출력 형식
각 섹션을 아래 구분자로 구분하여 출력하세요. 설명 없이 HTML만 출력합니다.

{filenames_example}

각 섹션은 완전한 <!DOCTYPE html> ... </html> 형태여야 합니다.
"""

    batch_label = ", ".join(section_names)
    retry_hint = ""
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        print(f"  [Phase 2-{batch_num}] {batch_label} 생성 중... (시도 {attempt}/{max_retries})")
        raw = run_claude(claude_cmd, prompt + retry_hint, allowed_tools="Read", timeout=300)
        if raw:
            sections = parse_sections(raw)
            if sections:
                # 후처리: body 클래스에 테마/액센트 보장
                for fname in sections:
                    sections[fname] = ensure_body_classes(sections[fname], theme, accent_mode)
                return sections
            # 파싱 실패도 재시도 대상
            print(f"    WARNING: 배치 {batch_num} 파싱 실패 (===SECTION: 구분자 없음)")
            if attempt < max_retries:
                retry_hint = "\n\n⚠️ 중요: 반드시 각 섹션을 ===SECTION:파일명.html=== 구분자로 분리하세요. 설명 없이 HTML만 출력합니다."
                print(f"    재시도 대기 5초...")
                time.sleep(5)
                continue
            # 마지막 시도까지 파싱 실패 → raw 저장
            return {"_raw": raw}

        # Claude CLI 실패 시 재시도 대기
        if attempt < max_retries:
            print(f"    재시도 대기 5초...")
            time.sleep(5)

    print(f"    ERROR: 배치 {batch_num} — {max_retries}회 모두 실패")
    return {}


def generate_brand_html(keyword, brand_name, homepage, expert, manuscript, output_dir):
    """2단계 배치 방식으로 브랜드 섹션 HTML 생성"""
    claude_cmd = find_claude_cmd()
    if not claude_cmd:
        print("ERROR: claude CLI가 설치되지 않았습니다.")
        sys.exit(1)

    is_medical = detect_medical(keyword)

    print("=" * 50)
    print("  브랜드 섹션 HTML 생성 (Claude)")
    print("=" * 50)
    print(f"  브랜드: {brand_name}")
    print(f"  키워드: {keyword}")
    print(f"  홈페이지: {homepage or '없음'}")
    print(f"  의료 업종: {'예' if is_medical else '아니오'}")
    print("-" * 50)

    # 이전 디자인 이력 검색 (같은 브랜드 반복 방지)
    design_history = find_previous_designs(output_dir, brand_name)
    if design_history:
        print(f"  이전 디자인 이력: {len(design_history)}건 발견")
        for prev in design_history:
            print(f"    - '{prev['keyword']}': 레시피={prev['recipe']}, 액센트={prev['accent_mode']}")
    print("-" * 50)

    # Phase 1: 계획 수립
    plan, phase1_raw = phase1_plan(
        claude_cmd, keyword, brand_name, homepage, expert, manuscript, is_medical,
        design_history=design_history,
    )

    os.makedirs(output_dir, exist_ok=True)

    if not plan:
        # 디버그용 raw 저장
        if phase1_raw:
            debug_path = os.path.join(output_dir, "_raw_phase1.txt")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(phase1_raw)
            print(f"    Raw 응답 저장: {debug_path}")
        print("ERROR: Phase 1 실패 — 디자인 계획을 수립하지 못했습니다.")
        sys.exit(1)

    # 계획 저장 (brand_name 추가 — 이력 검색 시 한글 매칭용)
    plan["brand_name"] = brand_name
    plan_path = os.path.join(output_dir, "_design_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"    계획 저장: {plan_path}")
    print("-" * 50)

    # Phase 2: 배치별 HTML 생성
    all_sections = {}
    for batch_num, batch in enumerate(SECTION_BATCHES, 1):
        batch_sections = phase2_generate_batch(
            claude_cmd, plan, batch, batch_num, keyword, brand_name, is_medical
        )

        # raw 저장 (파싱 실패 시 디버그용)
        raw_text = batch_sections.pop("_raw", None)
        if raw_text:
            raw_path = os.path.join(output_dir, f"_raw_batch{batch_num}.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_text)
            print(f"    Raw 응답 저장: {raw_path}")

        # 정상 파싱된 섹션은 항상 병합
        all_sections.update(batch_sections)

    if not all_sections:
        print("ERROR: 모든 배치에서 섹션 파싱 실패")
        return 0

    # 파일 저장
    saved = 0
    for filename, html in all_sections.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        saved += 1
        print(f"  [{saved}] {filename}")

    print("-" * 50)
    print(f"  완료: {saved}/10 섹션 생성")
    if saved < 10:
        print(f"  WARNING: {10 - saved}개 섹션 누락 — 개별 실행 탭에서 재시도 가능")
    print(f"  출력: {output_dir}")
    print("=" * 50)

    return saved


def main():
    parser = argparse.ArgumentParser(description="Claude 브랜드 섹션 HTML 생성")
    parser.add_argument("--keyword", required=True, help="타겟 키워드")
    parser.add_argument("--brand-name", required=True, help="브랜드명")
    parser.add_argument("--homepage", default="", help="홈페이지 URL")
    parser.add_argument("--expert", default="", help="전문가 이름/직함")
    parser.add_argument("--manuscript", default="", help="원고/주제")
    parser.add_argument("--output-dir", required=True, help="HTML 출력 디렉토리")
    args = parser.parse_args()

    saved = generate_brand_html(
        args.keyword, args.brand_name, args.homepage,
        args.expert, args.manuscript, args.output_dir,
    )
    if saved == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
