---
name: blog-post-generator
description: "네이버 블로그 게시물 자동 생성 스킬. 브랜드 이미지 + SEO 최적화 원고를 결합하여 상위노출용 완성 게시물을 생성합니다. 사용자가 블로그 글 작성, 블로그 포스트 생성, 네이버 블로그, SEO 블로그, 상위노출, 블로그 이미지, 블로그 콘텐츠 제작, 키워드 분석, 네이버 블로그 글쓰기, 블로그 원고 등을 언급하면 이 스킬을 사용하세요. '블로그 글 써줘', '블로그 콘텐츠 만들어줘', '네이버 상위노출 글 작성해줘' 같은 자연어 요청에도 반드시 트리거하세요."
---

# 네이버 블로그 포스트 생성기

브랜드 이미지 + SEO 최적화 원고를 결합하여 완성된 네이버 블로그 게시물을 생성합니다.

## 사용자 입력

| 항목 | 대상 스킬 | 필수 여부 |
|------|----------|----------|
| ★ 브랜드 원고 (또는 키워드/주제) | image-generator | 필수 |
| ★ 홈페이지 URL | image-generator | 필수 |
| ★ 타겟 키워드 | seo-writer | 필수 |

## 실행 순서

### Phase 1: blog-image-generator

브랜드 원고 + 홈페이지 URL을 기반으로 섹션별 이미지를 생성합니다.

**상세 워크플로우** → `skills/image-generator/SKILL.md`

```
입력: 브랜드 원고 + 홈페이지 URL
  ↓
홈페이지 분석 → 브랜드 색상/톤 추출
  ↓
원고 폴리싱 → 섹션 분리 (Hook~CTA + Disclaimer)
  ↓
HTML 생성 → PNG 렌더링
  ↓
출력: output/{keyword-slug}/branded/png/
```

렌더링:
```bash
python scripts/render_chrome.py \
  output/{keyword-slug}/branded/html \
  output/{keyword-slug}/branded/png \
  --width 680
```

### Phase 2: blog-seo-writer

타겟 키워드만으로 상위글 분석 + SEO 원고 + 이미지를 생성합니다.

**상세 워크플로우** → `skills/seo-writer/SKILL.md`

```
입력: 타겟 키워드
  ↓
Step 1: 상위글 크롤링 + 패턴 분석
Step 2: SEO 텍스트 작성 (내부 검증 → C/D등급이면 자동 수정 1회)
Step 3: SEO 검증 (이미지 삽입 전)
Step 4: SEO 이미지 (마커 삽입 + Gemini 생성)
Step 5: SEO 최종 검증 (이미지 포함)
  ↓
출력: output/{keyword-slug}/seo/
```

**SEO 이미지 규칙**: Gemini로 생성하는 모든 SEO 이미지에 텍스트(한글/영문) 삽입 금지. AI 이미지 생성 시 텍스트 오타·깨짐이 발생하므로 시각적 요소만으로 구성할 것.

스크립트 파이프라인:
```bash
# Step 1: 상위글 수집 + 분석
python scripts/fetch_competitors.py --keyword "{키워드}" --output-dir output/{slug}/seo/analysis/
python scripts/analyze_competitors.py --input output/{slug}/seo/analysis/competitor-pages.json --keyword "{키워드}" --output-dir output/{slug}/seo/analysis/

# Step 2: SEO 텍스트 작성 (Claude) — 내부 검증+자동수정 포함
python scripts/generate_seo_content.py --keyword "{키워드}" --analysis output/{slug}/seo/analysis/competitor-analysis.json --output-dir output/{slug}/seo/content/

# Step 3: SEO 검증 (이미지 삽입 전)
python scripts/validate_seo.py --content output/{slug}/seo/content/seo-content.md --keyword "{키워드}" --analysis output/{slug}/seo/analysis/competitor-analysis.json --skip-images

# Step 4: SEO 이미지 (마커 삽입 + 프롬프트 + Gemini)
python scripts/insert_image_markers.py --seo-content output/{slug}/seo/content/seo-content.md --keyword "{키워드}" --analysis output/{slug}/seo/analysis/competitor-analysis.json
python scripts/build_prompts.py --seo-content output/{slug}/seo/content/seo-content.md --output-dir output/{slug}/seo/images/
python scripts/generate_images.py --prompts-file output/{slug}/seo/images/prompts.json --output-dir output/{slug}/seo/images/

# Step 5: SEO 최종 검증 (이미지 포함)
python scripts/validate_seo.py --content output/{slug}/seo/content/seo-content.md --keyword "{키워드}" --analysis output/{slug}/seo/analysis/competitor-analysis.json
```

### Phase 3: 최종 조합

브랜드 이미지 + SEO 원고 + Disclaimer를 하나의 HTML로 합칩니다.

```bash
python scripts/compose_final.py \
  --branded-dir output/{slug}/branded/png \
  --seo-content output/{slug}/seo/content/seo-content.md \
  --seo-images-dir output/{slug}/seo/images/ \
  --output-dir output/{slug}/final/ \
  --brand-name "{브랜드명}" \
  --keyword "{키워드}"
```

## 최종 게시물 구조

```
[브랜드 이미지] Hook → Intro → Pain → Bridge → Why → Solution → Proof → CTA
[SEO 텍스트]   소제목 + 본문 + Gemini 이미지 (원고 기반 자동 배치)
[Disclaimer]   면책 조항 (맨 하단)
```

## 최종 파일 네이밍

```
{YYMMDD}_{브랜드명}_{키워드}.html
예: 260319_바디핏한의원_웨스턴돔다이어트.html
```

## 출력 폴더 구조

```
output/
└── {keyword-slug}/
    ├── branded/              ← blog-image-generator 결과
    │   ├── html/
    │   └── png/
    ├── seo/                  ← blog-seo-writer 결과
    │   ├── analysis/
    │   ├── content/
    │   └── images/
    └── final/                ← 최종 HTML
        └── {YYMMDD}_{브랜드명}_{키워드}.html
```

## 환경변수

| 변수 | 용도 | 필수 |
|------|------|------|
| `NAVER_CLIENT_ID` | 네이버 검색 API | 필수 |
| `NAVER_CLIENT_SECRET` | 네이버 검색 API | 필수 |
| `GOOGLE_API_KEY` | Gemini 이미지 생성 | 필수 |

## 프로젝트 구조

```
blog-post-generator/
├── SKILL.md                          ← 통합 워크플로우 (이 파일)
├── requirements.txt
├── .gitignore
├── skills/
│   ├── image-generator/
│   │   ├── SKILL.md                  ← 브랜드 이미지 상세 스펙
│   │   ├── assets/
│   │   │   └── base-styles.css
│   │   └── references/
│   │       ├── content-guide.md
│   │       ├── content-template.md
│   │       ├── variant-templates.md
│   │       └── medical-ad-compliance.md
│   └── seo-writer/
│       ├── SKILL.md                  ← SEO 원고 상세 스펙
│       └── references/
│           ├── seo-writing-guide.md
│           ├── naver-ranking-factors.md
│           ├── image-prompt-templates.md
│           └── medical-ad-compliance.md
├── scripts/
│   ├── utils.py                      ← 공유 유틸리티
│   ├── fetch_competitors.py          ← Step 1: 네이버 상위글 크롤링
│   ├── analyze_competitors.py        ← Step 1: 패턴 분석 (텍스트만)
│   ├── generate_seo_content.py       ← Step 2: SEO 원고 생성 (내부 검증+자동수정)
│   ├── generate_brand_html.py        ← Step 3: 브랜드 HTML 생성
│   ├── render_chrome.py              ← Step 3: HTML→PNG 렌더링
│   ├── insert_image_markers.py       ← Step 4: 원고 기반 이미지 마커 삽입
│   ├── build_prompts.py              ← Step 4: 마커 → prompts.json
│   ├── generate_images.py            ← Step 4: Gemini 이미지 생성
│   ├── validate_seo.py               ← Step 2 내부 검증 + Step 5 최종 검증
│   └── compose_final.py              ← Step 6: 최종 HTML 조합
└── output/                           ← 실행 시 생성
```
