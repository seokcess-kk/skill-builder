---
name: blog-seo-writer
description: "네이버 키워드 검색 상위글 분석 기반으로 SEO 최적화 블로그 텍스트와 이미지를 생성하는 스킬. blog-image-generator 스킬의 브랜드 이미지 섹션과 결합하여 완성된 블로그 포스트를 만듭니다. 'SEO 블로그', '네이버 SEO', '블로그 글 작성', '블로그 텍스트', '상위노출', '키워드 분석', '네이버 블로그 글쓰기' 등의 키워드가 포함된 요청에 이 스킬을 사용하세요."
---

# 네이버 블로그 SEO 콘텐츠 생성기

네이버 검색 상위글을 분석하고, SEO 최적화된 텍스트 원고 + 이미지를 생성합니다.
`blog-image-generator` 스킬의 브랜드 이미지와 결합하여 완성된 블로그 게시물을 만들 수 있습니다.

**Input**: 타겟 키워드
**Output**: SEO 텍스트 원고 + 생성 이미지 + 최종 게시물 (HTML/MD)

---

## 두 스킬 연동 워크플로우

두 스킬을 함께 사용하면 **브랜드 이미지 + SEO 원고**가 결합된 완성 게시물을 생성합니다.

### 사용자 입력

| 스킬 | 필수 입력 | 용도 |
|------|----------|------|
| **blog-image-generator** | 브랜드 원고(또는 키워드/주제) + 홈페이지 URL | 브랜드 섹션 이미지 (Hook~CTA + Disclaimer) |
| **blog-seo-writer** | 타겟 키워드 | SEO 최적화 텍스트 + 본문 이미지 |

### 실행 순서

```
1. blog-image-generator 실행
   입력: 브랜드 원고 + 홈페이지 URL
   출력: 섹션별 PNG (01-hook ~ 07-cta, 10-disclaimer)

2. blog-seo-writer 실행
   입력: 타겟 키워드 + (위 PNG 경로)
   출력: SEO 텍스트 + Gemini 이미지 + 최종 HTML

3. compose_final.py 조합
   → 브랜드 이미지(disclaimer 제외) + SEO 원고 + Disclaimer(맨 하단)
```

### 최종 게시물 구조

```
[브랜드 이미지] Hook → Intro → Pain → Bridge → Why → Solution → Proof → CTA
[SEO 텍스트]   소제목 + 본문 + Gemini 이미지 (7~8장)
[Disclaimer]   면책 조항 (맨 하단)
```

---

## Step 0: 사용자 입력 수집

| 항목 | 설명 | 미제공 시 |
|------|------|-----------|
| ★ 타겟 키워드 | 네이버 검색 키워드 | 필수 |
| 브랜드 이미지 경로 | blog-image-generator output/png 경로 | 없으면 텍스트+이미지만 |
| 브랜드 컬러 | HEX 코드 | 이미지 톤 통일용 (선택) |

### 블로그 타입

**정보성 글만 작성합니다.** 객관적 정보 전달, 전문 지식 공유 목적.
- 톤: 격식/해요체, 전문적
- 구조: 문제 제기 → 원인 → 해결법 → 정리
- 후기성 글은 허위/과장 광고 리스크가 있어 생성하지 않습니다.

키워드에서 자동 추론하는 항목:
- **브랜드명** — 키워드에 포함된 업체/서비스명 (예: "일산다이어트한의원" → "일산다이어트한의원")
- **업종** — 키워드 맥락에서 추론 (한의원→medical, 피부과→medical, 학원→education 등)
- **타겟 페르소나** — 상위글 분석에서 추론

**API 키 확인**:
- `NAVER_CLIENT_ID` + `NAVER_CLIENT_SECRET` — 상위글 검색용 (필수)
- `GOOGLE_API_KEY` — 이미지 생성용 (필수)

---

## Step 1: 네이버 검색 상위글 분석

### 1-1. 상위글 수집 (스크립트)

네이버 검색 API + 모바일 블로그 크롤링으로 상위글을 수집합니다:

```bash
python scripts/fetch_competitors.py \
  --keyword "{타겟 키워드}" \
  --output-dir output/{keyword-slug}/seo/analysis/ \
  --count 7
```

수집 항목:
- 전체 텍스트 (글자수 측정용)
- 소제목 구조 (SE3 인용구/H2/H3)
- 이미지 정보 (개수, alt 텍스트)
- 작성일

**출력**: `output/{keyword-slug}/seo/analysis/competitor-pages.json`

### 1-2. 패턴 분석 (스크립트)

```bash
python scripts/analyze_competitors.py \
  --input output/{keyword-slug}/seo/analysis/competitor-pages.json \
  --keyword "{타겟 키워드}" \
  --output-dir output/{keyword-slug}/seo/analysis/
```

분석 항목:
- **구조**: 평균 글자수, 문단수, 소제목수, 공통 소제목 키워드
- **키워드**: 밀도, 출현 횟수, 제목 포함률, 첫 등장 위치
- **이미지**: 평균 수, 유형 분포 (실사/일러스트/인포그래픽)
- **톤/스타일**: 문체 분포 (격식/반말), 전달 방식 (나열/스토리/Q&A)

상세 분석 기준 → `references/naver-ranking-factors.md` 참조

**출력 파일:**
- `competitor-analysis.json` — 상세 분석 데이터
- `analysis-summary.md` — 사람이 읽을 수 있는 요약

### 1-5. 분석 결과 보고

`analysis-summary.md`를 기반으로 사용자에게 요약 보고합니다:
- "상위 7개 글 평균: 2,400자, 이미지 6장, 소제목 4개"
- "공통 구조: 도입(공감) → 원인 설명 → 해결 방법 → 후기/사례 → 마무리"
- "이미지 유형: 실사 사진 60%, 텍스트카드 25%, 인포그래픽 15%"

사용자 확인 후 다음 단계로 진행합니다.

---

## Step 2: SEO 텍스트 작성

### 2-1. 가이드 로드

- `references/seo-writing-guide.md` 로드
- `output/{keyword-slug}/analysis/analysis-summary.md` 로드 (상위글 패턴)
- 규제 업종(의료) 감지 시 `references/medical-ad-compliance.md` 로드

### 2-2. 텍스트 원고 작성

상위글 분석 결과를 기반으로 SEO 최적화된 **정보성** 텍스트를 작성합니다.

**필수 충족 기준 (이 기준을 반드시 만족해야 합니다):**

| 항목 | 기준 | 비고 |
|------|------|------|
| 글자수 | 상위글 평균 × 1.2 이상, 최소 2,000자 | 공백 제외 |
| 키워드 밀도 | 1.5~3% | 키워드 길이에 따라 출현 횟수 조정 |
| 첫 키워드 위치 | 100자 이내 (50자 이내 이상적) | 도입부 첫 2문장 내 |
| 소제목 | 3~5개, 키워드 포함 2개 이상 | H2 사용 |
| 이미지 마커 | 상위글 평균 이상, 최소 7장 | 200~400자 간격 |
| 마무리 키워드 | 마지막 문단에 키워드 1회 | 자연스럽게 |
| 문단 길이 | 80~150자 (최대 200자) | 모바일 가독성 |
| 롱테일 키워드 | 키워드 변형 2~3개 자연 삽입 | 지역명+서비스 등 |

**작성 순서:**
1. 도입부: 독자 공감 + 키워드 자연 삽입 (100자 이내)
2. 본론 1: 문제 원인/배경 + [이미지]
3. 본론 2: 해결 방법/솔루션 + [이미지]
4. 본론 3: 상세 정보/비교 + [이미지]
5. 본론 4: 주의사항/팁 + [이미지] (글자수 보강)
6. 정리: 핵심 요약 + 키워드 + [이미지]

### 2-3. 이미지 마커 삽입

텍스트 내 이미지가 필요한 위치에 마커를 삽입합니다:
```
[IMAGE: {filename} | {type} - {description}]
```

**예시:**
```
[IMAGE: seo-img-01-consultation.png | real_photo - 한의원 상담 장면]
[IMAGE: seo-img-02-process.png | infographic - 치료 흐름을 나타내는 아이콘과 화살표 구성]
```

> **주의**: description은 시각적 장면만 묘사합니다. "4단계", "수치", "차트", "번호" 등 텍스트/숫자를 암시하는 표현 금지 — AI 이미지에서 한글·영문이 깨지므로 텍스트 없이 아이콘/도형/색상만으로 구성합니다.

이미지 유형과 개수는 상위글 분석의 이미지 패턴을 따릅니다.

### 2-4. SEO 검증 (스크립트)

작성 후 반드시 검증 스크립트를 실행합니다:

```bash
python scripts/validate_seo.py \
  --content output/{keyword-slug}/seo/content/seo-content.md \
  --keyword "{타겟 키워드}" \
  --analysis output/{keyword-slug}/seo/analysis/competitor-analysis.json
```

**등급 기준:**
- **A**: 수정사항 0건, 경고 0건
- **B**: 수정사항 0건, 경고만 있음
- **C**: 수정사항 1~2건
- **D**: 수정사항 3건 이상

**B 등급 이상이 될 때까지 원고를 수정합니다.**

### 2-5. 규제 업종 검수

의료 업종인 경우 `medical-ad-compliance.md` 기준으로 텍스트를 검수합니다.
SEO 텍스트는 브랜드 무관한 정보성이지만, 시술/약효 언급 시 주의가 필요합니다.

### 2-6. 저장

`output/{keyword-slug}/seo/content/seo-content.md`에 저장합니다.

---

## Step 3: 이미지 생성 (Gemini API)

### 3-1. 프롬프트 구성

텍스트의 이미지 마커에서 생성할 이미지 목록을 추출하고,
`references/image-prompt-templates.md`의 유형별 템플릿을 참조하여
Gemini 프롬프트를 구성합니다.

**프롬프트 작성 원칙** (Gemini 공식 가이드라인):
- 장면을 구체적으로 묘사 (키워드 나열 X)
- 사진 용어 활용 (렌즈, 조명, 각도)
- 스타일/색상 팔레트 명시
- "Korean" 키워드로 한국적 맥락 반영
- **텍스트 삽입 절대 금지** — AI 이미지 생성 시 한글/영문 텍스트가 오타·깨짐 발생하므로 모든 프롬프트에 "no text, no words, no letters, no labels" 명시. 텍스트가 필요한 이미지는 HTML→PNG 방식으로 별도 생성

### 3-2. prompts.json 생성 (스크립트)

```bash
python scripts/build_prompts.py \
  --seo-content output/{keyword-slug}/seo/content/seo-content.md \
  --output-dir output/{keyword-slug}/seo/images/ \
  --keyword "{타겟 키워드}"
```

SEO 텍스트의 `[IMAGE: ...]` 마커를 자동 추출하고, `references/image-prompt-templates.md` 기반으로 Gemini 프롬프트를 생성합니다.

**업종 자동 감지**: 키워드에서 업종을 추론합니다 (한의원→medical, 학원→education 등)

**비율 가이드 (유형별 기본값):**
| 유형 | 기본 비율 |
|------|----------|
| real_photo | 4:3 |
| facility_photo | 16:9 |
| product_photo | 1:1 |
| illustration | 4:3 |
| infographic | 3:4 |
| lifestyle_photo | 4:3 |
| concept_comparison | 4:3 |
| mood_photo | 16:9 |

### 3-3. 이미지 생성 실행

```bash
python scripts/generate_images.py \
  --prompts-file output/{keyword-slug}/seo/images/prompts.json \
  --output-dir output/{keyword-slug}/seo/images/
```

모델: `gemini-3.1-flash-image-preview`
생성된 이미지를 확인하고, 안전 필터에 차단된 경우 프롬프트를 수정하여 재시도합니다.

---

## Step 4: 최종 게시물 조합

### 4-1. 조합 실행

```bash
python scripts/compose_final.py \
  --branded-dir output/{keyword-slug}/branded/png \
  --seo-content output/{keyword-slug}/seo/content/seo-content.md \
  --seo-images-dir output/{keyword-slug}/seo/images/ \
  --output-dir output/{keyword-slug}/final/ \
  --brand-name "{브랜드명}" \
  --keyword "{타겟 키워드}"
```

브랜드 이미지 경로가 없으면 `--branded-dir` 생략 (SEO 콘텐츠만 조합).

### 4-2. 최종 게시물 구조

```
[브랜드 이미지 섹션 — blog-image-generator 결과물]
  01-hook.png
  02-intro.png
  03-pain.png
  03b-bridge.png
  04-why.png
  04b-bridge.png
  05-solution.png
  06-proof.png
  07-cta.png

[SEO 텍스트 섹션 — 이 스킬 결과물]
  소제목 1
  텍스트...
  [seo-img-01.png]

  소제목 2
  텍스트...
  [seo-img-02.png]
  ...

[Disclaimer — 맨 하단]
  10-disclaimer.png
```

> **Disclaimer 배치**: blog-image-generator의 disclaimer 이미지는 SEO 원고 하단에 자동 배치됩니다.

---

## Step 5: 결과물 전달

사용자에게 아래 정보와 함께 전달합니다:

- **최종 게시물 파일**: `{YYMMDD}_{브랜드명}_{키워드}.html` (네이버 붙여넣기용)
- **이미지 목록**: 브랜드 이미지 N개 + SEO 이미지 N개
- **SEO 지표**:
  - 총 글자수
  - 키워드 밀도
  - 이미지 수
  - 소제목 수
- **네이버 포스팅 가이드**: 제목 추천, 태그 추천, 발행 시간 추천

---

## 폴더 구조

```
output/
└── {keyword-slug}/
    ├── branded/                  ← blog-image-generator 결과
    │   ├── html/
    │   └── png/
    ├── seo/                      ← blog-seo-writer 결과
    │   ├── analysis/
    │   │   ├── competitor-pages.json
    │   │   ├── competitor-analysis.json
    │   │   └── analysis-summary.md
    │   ├── content/
    │   │   ├── seo-content.md
    │   │   └── seo-validation.json
    │   └── images/
    │       ├── prompts.json
    │       ├── seo-img-01-xxx.png
    │       └── generation-results.json
    └── final/
        └── {YYMMDD}_{브랜드명}_{키워드}.html
```

---

## 참조 파일

- `references/seo-writing-guide.md` — SEO 텍스트 작성 규칙
- `references/naver-ranking-factors.md` — 네이버 상위노출 요인
- `references/image-prompt-templates.md` — Gemini 이미지 프롬프트 템플릿
- `references/medical-ad-compliance.md` — 의료광고법 가이드 (의료 업종 시)

---

## 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 상위글 크롤링 0건 | 네이버 API 키 미설정 | `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 환경변수 확인 |
| 본문 크롤링 0자 | 네이버 블로그 HTML 구조 변경 | `fetch_competitors.py`의 `parse_blog_html` 파서 업데이트 |
| Gemini 이미지 차단 | 안전 필터 | 프롬프트에서 민감 표현 제거 후 재시도 |
| GOOGLE_API_KEY 없음 | 환경변수 미설정 | `set GOOGLE_API_KEY=xxx` 안내 |
| 한글 텍스트 깨짐 | AI 이미지 생성 시 텍스트 오타·깨짐 필연 | **모든 SEO 이미지에 텍스트 삽입 금지** — 프롬프트에 "no text" 반드시 포함 |
| API 속도 제한 | 단시간 다수 요청 | --delay 값 증가 (기본 3초) |
| 상위글 분석 부정확 | 크롤링 데이터 불완전 | 분석 가능한 글만으로 패턴 추출, 사용자 검토 |
