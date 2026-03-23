# Gemini 이미지 프롬프트 가이드

## 모델 정보

- **모델**: `gemini-3.1-flash-image-preview`
- **SDK**: `google-genai` Python 패키지
- **지원 비율**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9
- **해상도**: 1K (블로그 기본), 2K (고품질 필요 시)

## 프롬프트 작성 원칙

Gemini 공식 가이드라인 기반:

1. **장면을 묘사하라** — 키워드 나열이 아닌 구체적 상황 서술
2. **사진 용어 활용** — 렌즈(85mm portrait), 조명(soft natural light), 각도(eye-level)
3. **스타일 명시** — "professional photography", "flat illustration", "minimal infographic"
4. **색상/분위기 지정** — "warm tone", "clean white background", "muted pastel palette"
5. **텍스트 삽입 절대 금지** — AI 이미지 생성 시 한글·영문 모두 오타/깨짐이 발생하므로 모든 프롬프트에 "no text, no words, no letters, no labels, no watermarks" 를 반드시 포함할 것. 텍스트가 필요한 이미지는 Gemini가 아닌 HTML→PNG 방식으로 별도 생성

---

## 이미지 유형별 프롬프트 템플릿

### 1. 실제 인물 사진 (real_photo)

**용도**: 전문가 진료 장면, 상담, 시술 과정
**비율**: 3:2 또는 4:3

```
A {profession} {action} in a modern Korean {facility_type},
shot with 85mm lens, soft natural lighting from large windows,
clean and minimal interior with white walls,
{specific_details},
professional photography style, warm and trustworthy atmosphere,
Korean setting
```

**예시:**
```
A Korean female dermatologist consulting with a patient in a modern
Korean skin clinic, shot with 85mm portrait lens, soft natural
lighting from large windows, clean white interior with minimal
furniture, both wearing clean professional attire, eye-level angle,
professional medical photography, warm and approachable atmosphere
```

### 2. 시설/공간 사진 (facility_photo)

**용도**: 원내 사진, 진료실, 대기실, 장비
**비율**: 16:9 또는 3:2

```
Interior of a modern Korean {facility_type},
{design_style} design, {color_scheme} color palette,
{specific_elements},
professional architectural photography, wide angle lens,
bright and clean atmosphere, no people
```

**예시:**
```
Interior of a modern Korean traditional medicine clinic waiting room,
minimalist contemporary design with warm wood accents,
neutral beige and white color palette, comfortable seating area
with indoor plants, soft recessed lighting,
professional architectural photography, wide angle 24mm lens,
bright and welcoming atmosphere, no people
```

### 3. 제품/약재 사진 (product_photo)

**용도**: 한약재, 제품, 도구
**비율**: 1:1 또는 4:3

```
{product_description} arranged on {surface_type},
{lighting_style} lighting, {background_style} background,
shot from {angle}, macro detail visible,
professional product photography, {color_tone} tone
```

**예시:**
```
Various traditional Korean herbal medicine ingredients neatly
arranged on a clean white marble surface, soft diffused studio
lighting, minimal white background with subtle shadow,
shot from 45-degree angle, fine detail visible on dried herbs
and roots, professional product photography, warm natural tone
```

### 4. 일러스트레이션 (illustration)

**용도**: 의료 과정 설명, 개념도, 캐릭터 설명
**비율**: 3:2 또는 1:1

```
{style} illustration of {subject},
{color_palette} color palette, {line_style},
{background}, clean composition,
{additional_style_notes}
```

**예시:**
```
Flat vector illustration of a human body showing digestive
system and metabolism process, soft pastel color palette with
mint green and coral accents, clean thin outlines,
white background, modern medical illustration style,
simple and educational, no text labels
```

### 5. 인포그래픽 (infographic)

**용도**: 프로세스 단계, 비교 차트, 데이터 시각화
**비율**: 3:4 또는 9:16 (세로형)

> **주의**: 한글 텍스트가 필요한 인포그래픽은 Gemini 대신 HTML→PNG 방식(blog-image-generator 스킬)으로 생성하는 것을 권장합니다. Gemini는 레이아웃/그래픽 요소만 생성하고 텍스트는 별도 처리합니다.

```
Clean minimal infographic layout showing {content_description},
{number} sections/steps arranged {layout_direction},
{color_scheme} color scheme, flat design style,
{icon_style} icons, white background,
professional data visualization, no text
```

**예시:**
```
Clean minimal infographic layout showing a 4-step health
improvement process, 4 circular icons arranged vertically
with connecting dotted lines, deep purple and gold color scheme,
flat design style, simple geometric icons representing
diagnosis, treatment, coaching, and maintenance,
white background, professional data visualization, no text
```

### 6. 라이프스타일 사진 (lifestyle_photo)

**용도**: 건강한 생활, 운동, 식단, 일상 장면
**비율**: 3:2 또는 16:9

```
{subject} in {setting}, {activity_description},
natural candid photography style, {lighting},
{color_grading}, shot with {lens},
Korean {demographic} model, authentic and relatable
```

**예시:**
```
A Korean woman in her 40s preparing a healthy meal in a bright
modern kitchen, arranging colorful vegetables on a cutting board,
natural candid photography style, warm morning sunlight streaming
through windows, soft warm color grading, shot with 50mm lens,
authentic and relatable everyday moment
```

### 7. 비포/애프터 개념 이미지 (concept_comparison)

> **주의**: 의료 업종에서는 실제 환자 비포/애프터 사진이 아닌, 개념적 비교 이미지만 사용합니다. 의료광고법 준수 필수.

**비율**: 1:1 또는 3:2

```
Split image concept showing contrast between {before_state}
and {after_state}, {visual_metaphor},
{style} style, {color_contrast},
clean composition with clear visual separation,
conceptual and symbolic, not showing real patients
```

### 8. 감성/분위기 사진 (mood_photo)

**용도**: 섹션 구분, 감성적 전환, 배경 이미지
**비율**: 16:9 또는 3:2

```
{mood_description} atmosphere, {subject_or_scene},
{color_grading} color grading, {lighting_style},
{depth_of_field}, soft and dreamy quality,
editorial photography style
```

---

## 블로그 이미지 최적 설정

| 용도 | 비율 | 해상도 | 비고 |
|------|------|--------|------|
| 본문 삽입 이미지 | 3:2 | 1K | 기본값 |
| 세로형 인포그래픽 | 3:4 | 1K | 단계별 프로세스 |
| 썸네일/대표 이미지 | 16:9 | 1K | 네이버 썸네일 |
| 제품/디테일 | 1:1 | 1K | 정방형 |
| 와이드 배경 | 21:9 | 1K | 섹션 구분 |

## 프롬프트 품질 체크리스트

- [ ] 장면이 구체적으로 묘사되었는가 (키워드 나열 X)
- [ ] 카메라/렌즈/조명 정보가 포함되었는가
- [ ] 색상 팔레트가 브랜드와 일관되는가
- [ ] "Korean" 키워드로 한국적 맥락이 반영되었는가
- [ ] **텍스트 삽입 요청이 완전히 제거되었는가** (한글/영문 모두 금지 — 오타·깨짐 발생)
- [ ] 의료 업종이면 규제 표현이 없는가
