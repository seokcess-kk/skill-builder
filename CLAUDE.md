# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

필요한 스킬을 직접 만들고 관리하는 프로젝트. 현재 주요 스킬은 `blog-post-generator`.

## 프로젝트 구조

```
skill-builder/
├── CLAUDE.md                              ← 이 파일 (공통 규칙)
├── .gitignore
├── .claude/
│   ├── settings.json
│   └── skills/
│       └── ui-ux-pro-max/SKILL.md         ← UI/UX 디자인 시스템 (외부 스킬)
│
└── blog-post-generator/                   ← 메인 스킬
    ├── SKILL.md                           ← 통합 워크플로우 스펙
    ├── requirements.txt                   ← Python 의존성 (8개)
    ├── .gitignore
    ├── Blog Post Generator.bat            ← 원클릭 실행 (환경변수 자동 로드)
    ├── .streamlit/config.toml             ← Streamlit 테마/서버 설정
    │
    ├── app/
    │   └── main.py                        ← Streamlit UI 오케스트레이터 (902줄)
    │
    ├── scripts/                           ← 실행 스크립트 (11개)
    │   ├── utils.py                       ← 공유 유틸리티
    │   ├── fetch_competitors.py           ← Step 1: 네이버 상위글 크롤링
    │   ├── analyze_competitors.py         ← Step 1: 패턴 분석 (텍스트만, 이미지 유형 분석 제거)
    │   ├── generate_seo_content.py        ← Step 2: SEO 원고 생성 (Claude CLI, 텍스트만)
    │   ├── generate_brand_html.py         ← Step 3: 브랜드 HTML 생성 (Claude CLI, 2-phase)
    │   ├── render_chrome.py               ← Step 3: HTML→PNG (Selenium)
    │   ├── validate_seo.py                ← Step 2 내부 검증 + Step 5 최종 검증
    │   ├── insert_image_markers.py        ← Step 4: 원고 기반 이미지 마커 삽입 (Claude CLI)
    │   ├── build_prompts.py               ← Step 4: 마커 → prompts.json (no-text 규칙 적용)
    │   ├── generate_images.py             ← Step 4: Gemini 이미지 생성
    │   └── compose_final.py               ← Step 6: 최종 HTML 조합
    │
    └── skills/                            ← 하위 스킬
        ├── image-generator/               ← 브랜드 섹션 이미지 생성
        │   ├── SKILL.md                   ← 스킬 스펙 (레시피/변형/액센트 모드)
        │   ├── assets/base-styles.css     ← CSS 디자인 시스템
        │   └── references/
        │       ├── variant-templates.md   ← 섹션별 HTML 변형 템플릿
        │       ├── content-guide.md       ← 콘텐츠 작성 가이드
        │       ├── content-template.md    ← 콘텐츠 템플릿
        │       └── medical-ad-compliance.md ← 의료광고법 가이드
        │
        └── seo-writer/                    ← SEO 콘텐츠 생성
            ├── SKILL.md                   ← 스킬 스펙
            └── references/
                ├── seo-writing-guide.md   ← SEO 작성 규칙
                ├── naver-ranking-factors.md ← 네이버 상위노출 요인
                ├── image-prompt-templates.md ← Gemini 이미지 프롬프트 가이드
                └── medical-ad-compliance.md ← 의료광고법 가이드
```

## blog-post-generator 파이프라인

Streamlit UI(`app/main.py`)가 7단계 파이프라인을 순차 실행합니다. 각 스크립트는 독립 실행도 가능.

SEO 콘텐츠 파이프라인이 먼저 완결된 후 브랜드 이미지를 생성하여, 브랜드 이미지 실패 시에도 SEO 콘텐츠가 온전하게 보존됩니다.

```
Step 1: fetch_competitors.py → competitor-pages.json
           ↓
        analyze_competitors.py → competitor-analysis.json + analysis-summary.md
           ↓
Step 2: generate_seo_content.py (Claude CLI) → seo-content.md (텍스트만)
           └→ 내부 검증(skip_images) → C/D등급이면 자동 수정 1회
           ↓
Step 3: validate_seo.py (skip_images) → SEO 검증 (이미지 삽입 전)
           ↓
Step 4: insert_image_markers.py (Claude CLI) → seo-content.md에 이미지 마커 삽입
           ↓
        build_prompts.py → prompts.json (no-text 규칙만 추가)
           ↓
        generate_images.py (Gemini API) → SEO 이미지
           ↓
Step 5: validate_seo.py → seo-validation.json (이미지 포함 최종 검증)
           ↓
Step 6: generate_brand_html.py (Claude CLI, 2-phase) → HTML 섹션들
           ↓
        render_chrome.py (Selenium) → PNG 변환
           ↓
Step 7: compose_final.py → 최종 HTML (브랜드 이미지 + SEO 원고 + Disclaimer 병합)
```

### 출력 구조

```
output/{keyword-slug}/
├── seo/analysis/          ← Step 1: 경쟁사 분석 (JSON + 요약 MD)
├── seo/content/           ← Step 2~3: SEO 원고 + 검증 결과
├── seo/images/            ← Step 4: prompts.json + Gemini 이미지
├── branded/html/          ← Step 6: 브랜드 섹션 HTML (01-hook ~ 10-disclaimer)
├── branded/png/           ← Step 6: PNG 렌더링
└── final/                 ← Step 7: {YYMMDD}_{브랜드명}_{키워드}.html
```

### 공유 유틸리티 (`scripts/utils.py`)

| 함수 | 용도 |
|------|------|
| `find_claude_cmd()` | claude CLI 경로 탐색 (Windows: claude.cmd) |
| `count_chars(text)` | 공백 제외 글자수 |
| `strip_codeblock(text)` | Claude 응답의 마크다운 코드블록 래핑 제거 |
| `detect_industry(keyword)` | 키워드에서 업종 자동 감지 (medical/beauty/education/food/fitness) |
| `detect_medical(keyword)` | 의료 업종 감지 (detect_industry 편의 래퍼) |

## 실행 방법

```bash
# Streamlit UI (기본)
cd blog-post-generator
streamlit run app/main.py --server.headless true

# 또는 bat 파일 더블클릭 (환경변수 자동 로드)
"Blog Post Generator.bat"

# 개별 스크립트 실행 예시
python scripts/fetch_competitors.py --keyword "키워드" --output-dir output/slug/seo/analysis/ --count 7
python scripts/analyze_competitors.py --input output/slug/seo/analysis/competitor-pages.json --keyword "키워드" --output-dir output/slug/seo/analysis/
python scripts/validate_seo.py --content output/slug/seo/content/seo-content.md --keyword "키워드" --analysis output/slug/seo/analysis/competitor-analysis.json
```

## 네이밍 규칙

- 스킬 폴더: `kebab-case` (예: blog-post-generator)
- 스크립트: `snake_case.py` (예: fetch_competitors.py)
- bat 파일: 사람이 읽기 쉬운 이름 (예: Blog Post Generator.bat)
- 출력 파일: `{YYMMDD}_{브랜드명}_{키워드}.확장자`

## 환경변수

모든 API 키는 `~/.bashrc`에서 관리:
- `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` — 네이버 검색 API (필수)
- `GOOGLE_API_KEY` — Gemini API (SEO 이미지 생성)

bat 파일이 bash가 있으면 `~/.bashrc`에서 자동 로드.

## UI/UX 규칙

- **모든 UI 작업 시 `.claude/skills/ui-ux-pro-max/SKILL.md`를 참조하여 디자인 시스템을 적용할 것**
- Streamlit UI: Clean + Minimal 스타일 기본 (Soft UI + SaaS 심미)
- 포트: 8501 (기본), 충돌 시 8502, 8503 순차 사용

## 스킬 필수 파일

| 파일 | 필수 | 용도 |
|------|------|------|
| SKILL.md | O | 스킬 스펙, 워크플로우 정의 |
| requirements.txt | O | Python 의존성 |
| .gitignore | O | output/, __pycache__/ 제외 |
| {Name}.bat | UI 있을 때 | 원클릭 실행 |

## 콘텐츠 규칙

- 정보성 글만 생성 (후기성 글은 허위/과장 광고 리스크로 생성하지 않음)
- 의료 키워드 감지 시 의료광고법 컴플라이언스 가이드 자동 적용
- 브랜드 섹션 이미지에 전문가 사진/img 태그 사용 금지 — 텍스트/레이아웃만으로 구성
- **SEO 이미지(Gemini 생성)에 텍스트 삽입 금지** — AI 이미지 생성 시 한글 텍스트가 오타/깨짐 발생하므로 모든 SEO 이미지는 텍스트 없이 시각적 요소만으로 구성

## 코드 컨벤션

- 공통 함수는 `scripts/utils.py`에 정의하고 각 스크립트에서 import
- 외부 데이터(크롤링, 사용자 입력)를 HTML에 렌더링할 때는 반드시 `html.escape()` 적용
- Claude CLI 응답의 코드블록 래핑은 `strip_codeblock()`으로 제거
- 스크립트 간 중복 로직 금지 — utils.py로 통합 후 import
