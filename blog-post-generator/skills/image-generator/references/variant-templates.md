# 섹션 변형 HTML 템플릿 레퍼런스

> Claude가 블로그 이미지 HTML 파일을 생성할 때 참조하는 섹션별 변형(A/B/C) 템플릿 모음입니다.
> 각 템플릿은 필수 클래스명, HTML 구조, 플레이스홀더 마커를 포함합니다.

---

## 01 Hook (훅 — 첫인상 섹션)

### Hook-A: 중앙 정렬 + 코너장식 + 세로라인 (클래식)

**선택 기준:** 신뢰감·권위가 핵심인 콘텐츠(의료·법률·금융 등). 정제된 인상을 줘야 할 때. 짧고 강한 선언형 문장이 있을 때.

```html
<div class="hook hook-a theme-classic">
  <!-- 코너 장식 -->
  <div class="corner-decoration top-left"></div>
  <div class="corner-decoration top-right"></div>
  <div class="corner-decoration bottom-left"></div>
  <div class="corner-decoration bottom-right"></div>

  <!-- 세로 라인 -->
  <div class="vertical-line left"></div>
  <div class="vertical-line right"></div>

  <!-- 중앙 콘텐츠 -->
  <div class="hook-content center">
    <p class="hook-eyebrow">{eyebrow_text}</p>
    <h1 class="hook-headline">{headline_text}</h1>
    <p class="hook-subline">{subline_text}</p>
  </div>
</div>
```

---

### Hook-B: 다크 배경 전면 + 흰 대형 타이포 (임팩트)

**선택 기준:** 강렬한 첫 인상이 필요한 콘텐츠. 감정적 자극·문제 제기형 헤드라인. "충격적 사실"이나 "반전 메시지"를 전달할 때.

```html
<div class="hook hook-b theme-editorial">
  <!-- 다크 풀스크린 배경 -->
  <div class="dark-overlay"></div>

  <!-- 대형 타이포 콘텐츠 -->
  <div class="hook-content fullbleed">
    <p class="hook-eyebrow light">{eyebrow_text}</p>
    <h1 class="hook-headline display-xl light">{headline_text}</h1>
    <p class="hook-subline light">{subline_text}</p>
  </div>

  <!-- 하단 액센트 라인 -->
  <div class="accent-line bottom"></div>
</div>
```

---

### Hook-C: 좌측 인용기호 + 우측 정렬 (비대칭)

**선택 기준:** 전문가 인용구나 고객 증언으로 시작하는 콘텐츠. 비대칭 레이아웃으로 시각적 긴장감을 원할 때. 인용 주체(전문가·브랜드)를 강조할 때.

```html
<div class="hook hook-c theme-asymmetric">
  <!-- 대형 인용 기호 -->
  <div class="quote-mark large">&ldquo;</div>

  <!-- 우측 정렬 텍스트 블록 -->
  <div class="hook-content align-right">
    <blockquote class="hook-quote">{quote_text}</blockquote>
    <p class="hook-attribution">— {expert_name}, {expert_title}</p>
  </div>

  <!-- 좌측 하단 브랜드 표기 -->
  <div class="brand-tag bottom-left">{brand_name}</div>
</div>
```

---

### Hook-D: 분할형 — 좌측 컬러 밴드 + 우측 대형 타이포 (모던)

**선택 기준:** 브랜드 정체성을 강하게 각인시키면서 정돈된 모던함을 원할 때. 좌측 컬러 밴드가 브랜드를 상징하고 우측 텍스트가 메시지를 전달. 시각적 분할로 기존 중앙 정렬 레이아웃과 확실히 차별화할 때.

```html
<div class="hook hook-d theme-split">
  <!-- 좌측 컬러 밴드 -->
  <div class="hd-band">
    <p class="hd-brand-vertical">{brand_name}</p>
  </div>

  <!-- 우측 타이포 영역 -->
  <div class="hd-content">
    <p class="hook-eyebrow">{eyebrow_text}</p>
    <h1 class="hook-headline display-lg">{headline_text}</h1>
    <div class="hd-accent-line"></div>
    <p class="hook-subline">{subline_text}</p>
  </div>
</div>
```

---

### Hook-E: 극미니멀 — 대형 여백 + 단일 문장 (여백형)

**선택 기준:** 과도한 장식 없이 문장의 힘으로만 승부할 때. 고급 브랜드나 감성적 메시지에 적합. 넓은 여백이 문장에 무게감을 부여. 이전 포스트가 장식 과다했을 때 대비 효과.

```html
<div class="hook hook-e theme-whitespace">
  <!-- 극미니멀: 여백이 핵심 -->
  <div class="he-content">
    <h1 class="hook-headline he-single">{headline_text}</h1>
  </div>

  <!-- 하단 미세 라인 -->
  <div class="he-bottom-line"></div>
</div>
```

---

## 02 Intro (전문가 소개 섹션)

### Intro-A: 상단 밴드 + 숫자 하이라이트 + 자격 + 스피치

**선택 기준:** 정량적 실적(경력, 시술 건수, 수강생 수 등)으로 신뢰를 줄 수 있을 때. 숫자가 시선을 끌고 자격 리스트가 뒷받침할 때.

```html
<div class="intro intro-a theme-band">
  <!-- 상단 컬러 밴드 -->
  <div class="intro-band top">
    <p class="brand-label">{brand_name}</p>
  </div>

  <!-- 전문가 정보 -->
  <div class="intro-info">
    <h2 class="expert-name">{expert_name}</h2>
    <p class="expert-title">{expert_title}</p>
  </div>

  <!-- 숫자 하이라이트 (3열) -->
  <div class="stat-row">
    <div class="stat-item">
      <span class="stat-number">{stat_number_1}</span>
      <span class="stat-label">{stat_label_1}</span>
    </div>
    <div class="stat-item">
      <span class="stat-number">{stat_number_2}</span>
      <span class="stat-label">{stat_label_2}</span>
    </div>
    <div class="stat-item">
      <span class="stat-number">{stat_number_3}</span>
      <span class="stat-label">{stat_label_3}</span>
    </div>
  </div>

  <!-- 자격 리스트 -->
  <ul class="expert-credentials">
    <li>{credential_1}</li>
    <li>{credential_2}</li>
    <li>{credential_3}</li>
  </ul>

  <!-- 스피치 버블 -->
  <div class="speech-bubble">
    <p>{speech_text}</p>
  </div>
</div>
```

---

### Intro-B: 아이콘 그리드 + 자격 + 스피치

**선택 기준:** 핵심 강점을 아이콘/이모지 그리드로 시각화할 때. 자격과 차별점을 동시에 보여주고 싶을 때.

```html
<div class="intro intro-b theme-split">
  <!-- 브랜드 헤더 -->
  <div class="intro-header">
    <p class="brand-label">{brand_name}</p>
    <h2 class="expert-name">{expert_name}</h2>
    <p class="expert-title">{expert_title}</p>
  </div>

  <!-- 강점 그리드 (2x2 또는 3열) -->
  <div class="strength-grid">
    <div class="strength-item">
      <span class="strength-icon">{icon_1}</span>
      <p class="strength-text">{strength_1}</p>
    </div>
    <div class="strength-item">
      <span class="strength-icon">{icon_2}</span>
      <p class="strength-text">{strength_2}</p>
    </div>
    <div class="strength-item">
      <span class="strength-icon">{icon_3}</span>
      <p class="strength-text">{strength_3}</p>
    </div>
    <div class="strength-item">
      <span class="strength-icon">{icon_4}</span>
      <p class="strength-text">{strength_4}</p>
    </div>
  </div>

  <!-- 스피치 버블 -->
  <div class="speech-bubble">
    <p>{speech_text}</p>
  </div>
</div>
```

---

### Intro-C: 브랜드 카드 + 인용 블록

**선택 기준:** 심플하고 모던한 분위기를 원할 때. 핵심 메시지 하나를 강하게 전달하고 싶을 때. 브랜드 컬러 배경으로 시각적 밀도를 확보할 때.

```html
<div class="intro intro-c theme-minimal">
  <!-- 브랜드 컬러 배경 카드 -->
  <div class="intro-card bg-primary">
    <p class="brand-label">{brand_name}</p>
    <h2 class="expert-name">{expert_name}</h2>
    <p class="expert-title">{expert_title}</p>
  </div>

  <!-- 인용 블록 (액센트 좌측 보더 + 배경) -->
  <blockquote class="intro-quote accent-border">
    <p class="quote-text">{quote_text}</p>
    <cite class="quote-source">— {expert_name}</cite>
  </blockquote>

  <!-- 핵심 키워드 태그 -->
  <div class="keyword-tags">
    <span class="keyword-tag">{keyword_tag_1}</span>
    <span class="keyword-tag">{keyword_tag_2}</span>
    <span class="keyword-tag">{keyword_tag_3}</span>
  </div>
</div>
```

---

## 03 Pain (고통/문제 섹션)

### Pain-A: Voice Card 3장 (보더 컬러) + 내러티브

**선택 기준:** 세 가지 독립적인 고객 고통 포인트가 있을 때. 각 문제를 카드 형태로 명확히 구분하고 싶을 때. "이런 분들께"식 나열 구조일 때.

```html
<div class="pain pain-a theme-cards">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{pain_section_title}</h2>
  </div>

  <!-- Voice Card 3장 -->
  <div class="voice-cards grid-3">
    <div class="voice-card border-accent">
      <p class="voice-text">{pain_voice_1}</p>
      <span class="voice-tag">{pain_tag_1}</span>
    </div>
    <div class="voice-card border-accent">
      <p class="voice-text">{pain_voice_2}</p>
      <span class="voice-tag">{pain_tag_2}</span>
    </div>
    <div class="voice-card border-accent">
      <p class="voice-text">{pain_voice_3}</p>
      <span class="voice-tag">{pain_tag_3}</span>
    </div>
  </div>

  <!-- 내러티브 문단 -->
  <div class="pain-narrative">
    <p>{pain_narrative_text}</p>
  </div>
</div>
```

---

### Pain-B: Q&A 형식 (질문 블록 + 답변)

**선택 기준:** 독자가 스스로 공감하도록 질문형 구조가 효과적일 때. "혹시 이런 경험 있으신가요?" 스타일. 고통을 대화 형식으로 풀어낼 때.

```html
<div class="pain pain-b theme-qa">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{pain_section_title}</h2>
  </div>

  <!-- Q&A 블록 반복 -->
  <div class="qa-block">
    <div class="question-block">
      <span class="qa-label q">Q</span>
      <p class="question-text">{pain_question_1}</p>
    </div>
    <div class="answer-block">
      <span class="qa-label a">A</span>
      <p class="answer-text">{pain_answer_1}</p>
    </div>
  </div>

  <div class="qa-block">
    <div class="question-block">
      <span class="qa-label q">Q</span>
      <p class="question-text">{pain_question_2}</p>
    </div>
    <div class="answer-block">
      <span class="qa-label a">A</span>
      <p class="answer-text">{pain_answer_2}</p>
    </div>
  </div>
</div>
```

---

### Pain-C: 스토리텔링 (내러티브 + 이탤릭 인용)

**선택 기준:** 독자의 감정 이입을 극대화해야 할 때. 고통을 이야기 형식으로 서술할 때. 실제 고객 사례나 경험담이 있을 때.

```html
<div class="pain pain-c theme-story">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{pain_section_title}</h2>
  </div>

  <!-- 스토리 내러티브 -->
  <div class="story-narrative">
    <p>{pain_story_paragraph_1}</p>
    <p>{pain_story_paragraph_2}</p>
  </div>

  <!-- 이탤릭 인용 강조 -->
  <blockquote class="pain-quote italic">
    <p>"{pain_italic_quote}"</p>
    <cite>— {pain_quote_source}</cite>
  </blockquote>
</div>
```

---

## Bridge (전환 섹션 03b/04b)

### Bridge-A: 라이트 + 수평선 + Serif 문장

**선택 기준:** 부드럽고 자연스러운 섹션 전환이 필요할 때. 라이트 톤의 콘텐츠 흐름에서 전환점을 표시할 때. 희망적이거나 긍정적인 메시지로 넘어갈 때.

```html
<div class="bridge bridge-a theme-light">
  <!-- 상단 수평선 -->
  <hr class="bridge-line top" />

  <!-- Serif 전환 문장 -->
  <div class="bridge-content center">
    <p class="bridge-sentence serif">{bridge_sentence}</p>
  </div>

  <!-- 하단 수평선 -->
  <hr class="bridge-line bottom" />
</div>
```

---

### Bridge-B: 다크 풀밴드 + 흰 텍스트

**선택 기준:** 강한 섹션 구분이 필요할 때. 다크 톤으로 분위기 전환을 강조하고 싶을 때. 임팩트 있는 전환 메시지를 전달할 때.

```html
<div class="bridge bridge-b theme-dark fullband">
  <!-- 다크 풀밴드 배경은 CSS로 처리 -->

  <!-- 흰 텍스트 콘텐츠 -->
  <div class="bridge-content center">
    <p class="bridge-sentence light display">{bridge_sentence}</p>
    <p class="bridge-subtext light">{bridge_subtext}</p>
  </div>
</div>
```

---

### Bridge-C: 점 장식 + 이탤릭

**선택 기준:** 가볍고 우아한 전환이 필요할 때. 장식적 요소로 시각적 리듬을 줄 때. 이탤릭 문체로 감성적인 브리지를 만들 때.

```html
<div class="bridge bridge-c theme-dotted">
  <!-- 점 장식 -->
  <div class="dot-decoration">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>

  <!-- 이탤릭 전환 문장 -->
  <div class="bridge-content center">
    <p class="bridge-sentence italic">{bridge_sentence}</p>
  </div>

  <!-- 점 장식 (하단) -->
  <div class="dot-decoration">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>
</div>
```

---

## 04 Why (이유/차별화 섹션)

### Why-A: 다크 + 2열 카드 그리드 + 통계

**선택 기준:** 수치·통계 데이터가 있고 이를 강조하고 싶을 때. 두 가지 대비 또는 네 가지 이유를 2×2 그리드로 보여줄 때. 신뢰도 높은 근거 기반 콘텐츠일 때.

```html
<div class="why why-a theme-dark">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title light">{why_section_title}</h2>
  </div>

  <!-- 2열 카드 그리드 -->
  <div class="why-grid grid-2">
    <div class="why-card dark-card">
      <div class="card-stat">{stat_number_1}<span class="stat-unit">{stat_unit_1}</span></div>
      <h3 class="card-title light">{why_title_1}</h3>
      <p class="card-desc light">{why_desc_1}</p>
    </div>
    <div class="why-card dark-card">
      <div class="card-stat">{stat_number_2}<span class="stat-unit">{stat_unit_2}</span></div>
      <h3 class="card-title light">{why_title_2}</h3>
      <p class="card-desc light">{why_desc_2}</p>
    </div>
    <div class="why-card dark-card">
      <div class="card-stat">{stat_number_3}<span class="stat-unit">{stat_unit_3}</span></div>
      <h3 class="card-title light">{why_title_3}</h3>
      <p class="card-desc light">{why_desc_3}</p>
    </div>
    <div class="why-card dark-card">
      <div class="card-stat">{stat_number_4}<span class="stat-unit">{stat_unit_4}</span></div>
      <h3 class="card-title light">{why_title_4}</h3>
      <p class="card-desc light">{why_desc_4}</p>
    </div>
  </div>
</div>
```

---

### Why-B: 라이트 + 세로 아이콘 카드 나열

**선택 기준:** 밝고 친근한 톤이 필요할 때. 아이콘/이모지와 함께 이유를 나열할 때. 3~4개의 이유를 수직으로 시각화할 때.

```html
<div class="why why-b theme-light">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{why_section_title}</h2>
  </div>

  <!-- 세로 아이콘 카드 나열 -->
  <div class="why-list vertical">
    <div class="why-item icon-card">
      <div class="item-icon">{icon_1}</div>
      <div class="item-text">
        <h3 class="item-title">{why_title_1}</h3>
        <p class="item-desc">{why_desc_1}</p>
      </div>
    </div>
    <div class="why-item icon-card">
      <div class="item-icon">{icon_2}</div>
      <div class="item-text">
        <h3 class="item-title">{why_title_2}</h3>
        <p class="item-desc">{why_desc_2}</p>
      </div>
    </div>
    <div class="why-item icon-card">
      <div class="item-icon">{icon_3}</div>
      <div class="item-text">
        <h3 class="item-title">{why_title_3}</h3>
        <p class="item-desc">{why_desc_3}</p>
      </div>
    </div>
  </div>
</div>
```

---

### Why-C: 다크 + 타임라인형

**선택 기준:** 이유들이 시간 순서나 단계적 논리를 가질 때. "첫째→둘째→셋째"의 인과관계를 보여줄 때. 스토리 흐름이 있는 근거 제시에 적합.

```html
<div class="why why-c theme-dark timeline">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title light">{why_section_title}</h2>
  </div>

  <!-- 타임라인 -->
  <div class="timeline-wrap">
    <div class="timeline-line vertical"></div>

    <div class="timeline-item">
      <div class="timeline-node">{step_number_1}</div>
      <div class="timeline-content">
        <h3 class="timeline-title light">{why_title_1}</h3>
        <p class="timeline-desc light">{why_desc_1}</p>
      </div>
    </div>

    <div class="timeline-item">
      <div class="timeline-node">{step_number_2}</div>
      <div class="timeline-content">
        <h3 class="timeline-title light">{why_title_2}</h3>
        <p class="timeline-desc light">{why_desc_2}</p>
      </div>
    </div>

    <div class="timeline-item">
      <div class="timeline-node">{step_number_3}</div>
      <div class="timeline-content">
        <h3 class="timeline-title light">{why_title_3}</h3>
        <p class="timeline-desc light">{why_desc_3}</p>
      </div>
    </div>
  </div>
</div>
```

---

## 05 Solution (솔루션 섹션)

### Solution-A: 타임라인 + 비교표 + 클로징

**선택 기준:** 단계별 접근 방식과 경쟁 비교가 모두 필요할 때. 과정을 설명하고 타사와의 차이를 표로 보여줄 때. 풍부한 콘텐츠 구조일 때.

```html
<div class="solution solution-a theme-timeline-table">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{solution_section_title}</h2>
  </div>

  <!-- 타임라인 (단계별 접근) -->
  <div class="solution-timeline">
    <div class="step-item">
      <div class="step-number">01</div>
      <div class="step-content">
        <h3 class="step-title">{step_title_1}</h3>
        <p class="step-desc">{step_desc_1}</p>
      </div>
    </div>
    <div class="step-item">
      <div class="step-number">02</div>
      <div class="step-content">
        <h3 class="step-title">{step_title_2}</h3>
        <p class="step-desc">{step_desc_2}</p>
      </div>
    </div>
    <div class="step-item">
      <div class="step-number">03</div>
      <div class="step-content">
        <h3 class="step-title">{step_title_3}</h3>
        <p class="step-desc">{step_desc_3}</p>
      </div>
    </div>
  </div>

  <!-- 비교표 -->
  <div class="comparison-table">
    <table>
      <thead>
        <tr>
          <th>{comparison_feature_label}</th>
          <th class="brand-col">{brand_name}</th>
          <th>{competitor_label}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{feature_1}</td>
          <td class="brand-col check">✓</td>
          <td class="cross">✗</td>
        </tr>
        <tr>
          <td>{feature_2}</td>
          <td class="brand-col check">✓</td>
          <td class="cross">✗</td>
        </tr>
        <tr>
          <td>{feature_3}</td>
          <td class="brand-col check">✓</td>
          <td>{competitor_value_3}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- 클로징 메시지 -->
  <div class="solution-closing">
    <p>{solution_closing_text}</p>
  </div>
</div>
```

---

### Solution-B: 어프로치 카드 + 체크리스트

**선택 기준:** 구체적인 방법론이나 접근 방식을 카드로 보여줄 때. 독자가 확인해야 할 항목을 체크리스트로 제공할 때. 실행 중심의 솔루션 콘텐츠일 때.

```html
<div class="solution solution-b theme-approach">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{solution_section_title}</h2>
  </div>

  <!-- 어프로치 카드 -->
  <div class="approach-cards grid-2">
    <div class="approach-card">
      <div class="approach-icon">{approach_icon_1}</div>
      <h3 class="approach-title">{approach_title_1}</h3>
      <p class="approach-desc">{approach_desc_1}</p>
    </div>
    <div class="approach-card">
      <div class="approach-icon">{approach_icon_2}</div>
      <h3 class="approach-title">{approach_title_2}</h3>
      <p class="approach-desc">{approach_desc_2}</p>
    </div>
  </div>

  <!-- 체크리스트 -->
  <div class="checklist-wrap">
    <h3 class="checklist-title">{checklist_title}</h3>
    <ul class="checklist">
      <li class="checklist-item"><span class="check-icon">✓</span>{checklist_item_1}</li>
      <li class="checklist-item"><span class="check-icon">✓</span>{checklist_item_2}</li>
      <li class="checklist-item"><span class="check-icon">✓</span>{checklist_item_3}</li>
      <li class="checklist-item"><span class="check-icon">✓</span>{checklist_item_4}</li>
    </ul>
  </div>
</div>
```

---

### Solution-C: 비교표 우선 + USP 배지

**선택 기준:** 경쟁사와의 차별점이 콘텐츠의 핵심일 때. 비교표를 전면에 내세우고 USP(고유 판매 포인트)를 배지로 강조할 때. 전환 목적이 강한 광고성 콘텐츠에 적합.

```html
<div class="solution solution-c theme-comparison-first">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{solution_section_title}</h2>
  </div>

  <!-- 비교표 (우선 배치) -->
  <div class="comparison-table primary">
    <table>
      <thead>
        <tr>
          <th>{comparison_feature_label}</th>
          <th class="brand-col highlight">{brand_name}</th>
          <th>{competitor_label}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{feature_1}</td>
          <td class="brand-col check">✓</td>
          <td class="cross">✗</td>
        </tr>
        <tr>
          <td>{feature_2}</td>
          <td class="brand-col">{brand_value_2}</td>
          <td>{competitor_value_2}</td>
        </tr>
        <tr>
          <td>{feature_3}</td>
          <td class="brand-col check">✓</td>
          <td class="cross">✗</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- USP 배지 그룹 -->
  <div class="usp-badges">
    <span class="usp-badge accent">{usp_badge_1}</span>
    <span class="usp-badge accent">{usp_badge_2}</span>
    <span class="usp-badge accent">{usp_badge_3}</span>
  </div>
</div>
```

---

### Solution-D: 매거진 그리드 — 2×2 USP 카드 + 핵심 메시지

**선택 기준:** USP가 4개이고 모두 동등한 비중을 가질 때. 매거진 스타일의 정돈된 그리드 레이아웃. 시각적 균형과 정보 밀도를 동시에 달성하고 싶을 때. 타임라인이나 리스트 형태가 아닌 새로운 구조가 필요할 때.

```html
<div class="solution solution-d theme-magazine-grid">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{solution_section_title}</h2>
  </div>

  <!-- 2×2 USP 그리드 -->
  <div class="sd-grid">
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_1}</div>
      <h3 class="sd-card-title">{usp_title_1}</h3>
      <p class="sd-card-desc">{usp_desc_1}</p>
    </div>
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_2}</div>
      <h3 class="sd-card-title">{usp_title_2}</h3>
      <p class="sd-card-desc">{usp_desc_2}</p>
    </div>
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_3}</div>
      <h3 class="sd-card-title">{usp_title_3}</h3>
      <p class="sd-card-desc">{usp_desc_3}</p>
    </div>
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_4}</div>
      <h3 class="sd-card-title">{usp_title_4}</h3>
      <p class="sd-card-desc">{usp_desc_4}</p>
    </div>
  </div>

  <!-- 핵심 메시지 배너 -->
  <div class="sd-banner">
    <p class="sd-banner-text">{solution_core_message}</p>
  </div>

  <!-- 클로징 -->
  <div class="solution-closing">
    <p>{solution_closing_text}</p>
  </div>
</div>
```

---

## 06 Proof (증거/신뢰 섹션)

### Proof-A: 통계 3분할 + 리뷰 카드

**선택 기준:** 수치 기반 증거와 고객 리뷰를 함께 보여줄 때. 통계 3개와 리뷰 1~2개를 균형 있게 구성할 때. 신뢰도 극대화가 필요한 콘텐츠.

```html
<div class="proof proof-a theme-stats-review">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{proof_section_title}</h2>
  </div>

  <!-- 통계 3분할 -->
  <div class="stats-row grid-3">
    <div class="stat-item">
      <div class="stat-number">{stat_number_1}</div>
      <p class="stat-label">{stat_label_1}</p>
    </div>
    <div class="stat-item">
      <div class="stat-number">{stat_number_2}</div>
      <p class="stat-label">{stat_label_2}</p>
    </div>
    <div class="stat-item">
      <div class="stat-number">{stat_number_3}</div>
      <p class="stat-label">{stat_label_3}</p>
    </div>
  </div>

  <!-- 리뷰 카드 -->
  <div class="review-cards">
    <div class="review-card">
      <p class="review-text">"{review_text_1}"</p>
      <div class="review-meta">
        <span class="reviewer-name">{reviewer_name_1}</span>
        <span class="reviewer-info">{reviewer_info_1}</span>
      </div>
    </div>
    <div class="review-card">
      <p class="review-text">"{review_text_2}"</p>
      <div class="review-meta">
        <span class="reviewer-name">{reviewer_name_2}</span>
        <span class="reviewer-info">{reviewer_info_2}</span>
      </div>
    </div>
  </div>
</div>
```

---

### Proof-B: Q&A 코멘트 + 리뷰

**선택 기준:** 전문가의 Q&A 형식으로 신뢰를 쌓고 리뷰로 마무리할 때. 의료·법률·금융처럼 전문적 답변이 설득력 있는 분야. 콘텐츠가 대화형 구조일 때.

```html
<div class="proof proof-b theme-qa-review">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{proof_section_title}</h2>
  </div>

  <!-- Q&A 코멘트 블록 -->
  <div class="qa-comment-block">
    <div class="comment-q">
      <span class="comment-label">Q</span>
      <p class="comment-text">{proof_question}</p>
    </div>
    <div class="comment-a expert">
      <span class="comment-label expert-label">A</span>
      <div class="comment-content">
        <p class="comment-text">{proof_answer}</p>
        <span class="expert-badge">{expert_name} · {expert_title}</span>
      </div>
    </div>
  </div>

  <!-- 리뷰 카드 -->
  <div class="review-cards">
    <div class="review-card">
      <p class="review-text">"{review_text_1}"</p>
      <div class="review-meta">
        <span class="reviewer-name">{reviewer_name_1}</span>
        <span class="reviewer-info">{reviewer_info_1}</span>
      </div>
    </div>
  </div>
</div>
```

---

### Proof-C: 별점/태그 리뷰 카드

**선택 기준:** 시각적으로 임팩트 있는 리뷰 중심 콘텐츠일 때. 별점과 키워드 태그를 함께 보여줄 때. 고객 만족도를 직관적으로 전달하고 싶을 때.

```html
<div class="proof proof-c theme-star-review">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title">{proof_section_title}</h2>
  </div>

  <!-- 별점 리뷰 카드 -->
  <div class="star-review-cards">
    <div class="star-review-card">
      <div class="star-rating">{star_rating_1} <!-- ★★★★★ --></div>
      <p class="review-text">"{review_text_1}"</p>
      <div class="review-tags">
        <span class="review-tag">{tag_1}</span>
        <span class="review-tag">{tag_2}</span>
      </div>
      <div class="review-meta">
        <span class="reviewer-name">{reviewer_name_1}</span>
        <span class="reviewer-info">{reviewer_info_1}</span>
      </div>
    </div>

    <div class="star-review-card">
      <div class="star-rating">{star_rating_2}</div>
      <p class="review-text">"{review_text_2}"</p>
      <div class="review-tags">
        <span class="review-tag">{tag_3}</span>
        <span class="review-tag">{tag_4}</span>
      </div>
      <div class="review-meta">
        <span class="reviewer-name">{reviewer_name_2}</span>
        <span class="reviewer-info">{reviewer_info_2}</span>
      </div>
    </div>
  </div>
</div>
```

---

## 07 CTA (행동 유도 섹션)

### CTA-A: 다크 + 코너장식 + 아웃라인 버튼

**선택 기준:** 클래식하고 권위 있는 분위기에서 전환을 유도할 때. 아웃라인 버튼으로 세련된 인상을 줄 때. 코너 장식으로 Hook-A와 시각적 일관성을 유지할 때.

```html
<div class="cta cta-a theme-dark">
  <!-- 코너 장식 -->
  <div class="corner-decoration top-left light"></div>
  <div class="corner-decoration top-right light"></div>
  <div class="corner-decoration bottom-left light"></div>
  <div class="corner-decoration bottom-right light"></div>

  <!-- CTA 콘텐츠 -->
  <div class="cta-content center">
    <h2 class="cta-headline light">{cta_headline}</h2>
    <p class="cta-subtext light">{cta_subtext}</p>

    <!-- 아웃라인 버튼 -->
    <a href="{cta_link}" class="cta-button outline-light">{cta_button_text}</a>

    <!-- 부가 정보 -->
    <p class="cta-note light">{cta_note_text}</p>
  </div>
</div>
```

---

### CTA-B: 라이트 + 풀컬러 버튼

**선택 기준:** 밝고 친근한 톤으로 행동을 유도할 때. 브랜드 컬러 버튼으로 강한 시각적 CTA를 줄 때. 부드러운 설득이 필요한 콘텐츠에 적합.

```html
<div class="cta cta-b theme-light">
  <!-- CTA 콘텐츠 -->
  <div class="cta-content center">
    <h2 class="cta-headline">{cta_headline}</h2>
    <p class="cta-subtext">{cta_subtext}</p>

    <!-- 풀컬러 버튼 -->
    <a href="{cta_link}" class="cta-button fullcolor primary">{cta_button_text}</a>

    <!-- 부가 정보 -->
    <p class="cta-note">{cta_note_text}</p>
  </div>
</div>
```

---

### CTA-C: 다크 그라디언트 + 대형 타이포

**선택 기준:** 마지막 섹션에서 강력한 인상으로 마무리할 때. 대형 타이포로 메시지를 압도적으로 전달할 때. 프리미엄 또는 감성 브랜드에 적합.

```html
<div class="cta cta-c theme-dark-gradient">
  <!-- 그라디언트 배경은 CSS로 처리 -->

  <!-- 대형 타이포 CTA -->
  <div class="cta-content center">
    <h2 class="cta-headline display-xl light">{cta_headline}</h2>
    <p class="cta-subtext light">{cta_subtext}</p>

    <!-- 버튼 -->
    <a href="{cta_link}" class="cta-button gradient-accent">{cta_button_text}</a>

    <!-- 브랜드 서명 -->
    <p class="cta-brand-sig light">{brand_name}</p>
  </div>
</div>
```

---

### CTA-D: 분할형 — 좌 다크(메시지) + 우 라이트(연락처)

**선택 기준:** 감성적 브랜드 메시지와 실용적 연락처 정보를 동시에 전달할 때. 좌우 대비로 시각적 임팩트와 정보 전달을 균형 있게 구현. 기존 전면 다크/전면 라이트 CTA와 차별화할 때.

```html
<div class="cta cta-d theme-split-cta">
  <!-- 좌측: 다크 패널 (브랜드 메시지) -->
  <div class="cd-left">
    <p class="cd-label">{brand_eng_name}</p>
    <h2 class="cd-headline">{cta_headline}</h2>
    <p class="cd-subtext">{cta_subtext}</p>
  </div>

  <!-- 우측: 라이트 패널 (연락처 + CTA) -->
  <div class="cd-right">
    <div class="cd-info-block">
      <p class="cd-brand-name">{brand_name}</p>
      <div class="cd-contact-list">
        <p class="cd-contact-item">{contact_phone}</p>
        <p class="cd-contact-item">{contact_address}</p>
        <p class="cd-contact-item">{contact_channel}</p>
      </div>
    </div>
    <a href="{cta_link}" class="cta-button fullcolor">{cta_button_text}</a>
  </div>
</div>
```

---

### CTA-E: 카드 스택형 — 틴트 배경 + 플로팅 카드

**선택 기준:** 미니멀하고 깔끔한 마무리가 필요할 때. 모던 브랜드에 적합. 장식을 최소화하고 하나의 카드에 모든 정보를 담아 정돈된 인상. 기존 CTA 변형들과 확실히 다른 구조적 느낌.

```html
<div class="cta cta-e theme-card-stack">
  <!-- 틴트 배경 위 플로팅 카드 -->
  <div class="ce-card">
    <p class="ce-label">{brand_eng_name}</p>
    <div class="ce-divider"></div>
    <h2 class="ce-headline">{cta_headline}</h2>
    <p class="ce-subtext">{cta_subtext}</p>

    <!-- 연락처 -->
    <div class="ce-contact">
      <p class="ce-contact-item">{brand_name} · {contact_phone}</p>
      <p class="ce-contact-item">{contact_address}</p>
    </div>

    <!-- 버튼 -->
    <a href="{cta_link}" class="cta-button ce-button">{cta_button_text}</a>
  </div>
</div>
```

---

## 10 Disclaimer (고지사항 섹션)

### Disclaimer-A: 카드 3장 + accent 보더

**선택 기준:** 세 가지 독립적인 고지 항목이 있을 때. 각 항목을 카드로 명확히 구분하고 accent 색상으로 중요도를 표시할 때. 의료·금융 규정 준수 콘텐츠.

```html
<div class="disclaimer disclaimer-a theme-cards">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title small">{disclaimer_section_title}</h2>
  </div>

  <!-- 고지 카드 3장 -->
  <div class="disclaimer-cards grid-3">
    <div class="disclaimer-card accent-border">
      <h3 class="disclaimer-card-title">{disclaimer_title_1}</h3>
      <p class="disclaimer-text">{disclaimer_text_1}</p>
    </div>
    <div class="disclaimer-card accent-border">
      <h3 class="disclaimer-card-title">{disclaimer_title_2}</h3>
      <p class="disclaimer-text">{disclaimer_text_2}</p>
    </div>
    <div class="disclaimer-card accent-border">
      <h3 class="disclaimer-card-title">{disclaimer_title_3}</h3>
      <p class="disclaimer-text">{disclaimer_text_3}</p>
    </div>
  </div>
</div>
```

---

### Disclaimer-B: 보더 구분 + 넘버링

**선택 기준:** 고지 항목들이 순서나 우선순위를 가질 때. 넘버링으로 명확한 구분이 필요할 때. 법적 요건이 많아 리스트 형태가 적합할 때.

```html
<div class="disclaimer disclaimer-b theme-numbered">
  <!-- 섹션 헤더 -->
  <div class="section-header">
    <h2 class="section-title small">{disclaimer_section_title}</h2>
  </div>

  <!-- 넘버 구분 리스트 -->
  <div class="disclaimer-list">
    <div class="disclaimer-item numbered">
      <span class="disclaimer-number">01</span>
      <div class="disclaimer-content">
        <h3 class="disclaimer-item-title">{disclaimer_title_1}</h3>
        <p class="disclaimer-text">{disclaimer_text_1}</p>
      </div>
    </div>
    <hr class="disclaimer-divider" />
    <div class="disclaimer-item numbered">
      <span class="disclaimer-number">02</span>
      <div class="disclaimer-content">
        <h3 class="disclaimer-item-title">{disclaimer_title_2}</h3>
        <p class="disclaimer-text">{disclaimer_text_2}</p>
      </div>
    </div>
    <hr class="disclaimer-divider" />
    <div class="disclaimer-item numbered">
      <span class="disclaimer-number">03</span>
      <div class="disclaimer-content">
        <h3 class="disclaimer-item-title">{disclaimer_title_3}</h3>
        <p class="disclaimer-text">{disclaimer_text_3}</p>
      </div>
    </div>
  </div>
</div>
```

---

### Disclaimer-C: 단일 카드 + 수평선 구분

**선택 기준:** 고지 사항을 하나의 카드에 통합해서 보여줄 때. 미니멀하게 처리하고 싶을 때. 고지 내용이 간결하고 분량이 적을 때.

```html
<div class="disclaimer disclaimer-c theme-single-card">
  <!-- 단일 카드 -->
  <div class="disclaimer-card single">
    <!-- 카드 헤더 -->
    <div class="disclaimer-card-header">
      <h2 class="disclaimer-card-title">{disclaimer_section_title}</h2>
    </div>

    <!-- 수평선 구분 -->
    <hr class="disclaimer-divider" />

    <!-- 고지 내용 블록 반복 -->
    <div class="disclaimer-block">
      <h3 class="disclaimer-block-title">{disclaimer_title_1}</h3>
      <p class="disclaimer-text">{disclaimer_text_1}</p>
    </div>

    <hr class="disclaimer-divider thin" />

    <div class="disclaimer-block">
      <h3 class="disclaimer-block-title">{disclaimer_title_2}</h3>
      <p class="disclaimer-text">{disclaimer_text_2}</p>
    </div>

    <hr class="disclaimer-divider thin" />

    <div class="disclaimer-block">
      <h3 class="disclaimer-block-title">{disclaimer_title_3}</h3>
      <p class="disclaimer-text">{disclaimer_text_3}</p>
    </div>
  </div>
</div>
```

---

## 플레이스홀더 마커 목록

| 마커 | 설명 |
|------|------|
| `{headline_text}` | 메인 헤드라인 텍스트 |
| `{subline_text}` | 서브 헤드라인 텍스트 |
| `{eyebrow_text}` | 헤드라인 위 소제목 (아이브로우) |
| `{quote_text}` | 인용구 본문 |
| `{expert_name}` | 전문가 이름 |
| `{expert_title}` | 전문가 직함/타이틀 |
| `{expert_photo_url}` | 전문가 사진 경로 |
| `{brand_name}` | 브랜드/서비스 이름 |
| `{brand_eng_name}` | 브랜드 영문명 (CTA-D/E용) |
| `{credential_text}` | 자격증/학위 등 자격 태그 |
| `{speech_text}` | 스피치 버블 텍스트 |
| `{pain_voice_N}` | N번째 고통 보이스 카드 텍스트 |
| `{stat_number_N}` | N번째 통계 수치 |
| `{stat_label_N}` | N번째 통계 레이블 |
| `{review_text_N}` | N번째 리뷰 본문 |
| `{reviewer_name_N}` | N번째 리뷰어 이름 |
| `{cta_headline}` | CTA 헤드라인 |
| `{cta_button_text}` | CTA 버튼 텍스트 |
| `{cta_link}` | CTA 버튼 링크 URL |
| `{cta_note_text}` | CTA 하단 부가 설명 |
| `{contact_phone}` | 연락처 전화번호 (CTA-D/E용) |
| `{contact_address}` | 주소 (CTA-D/E용) |
| `{contact_channel}` | 예약/상담 채널 (CTA-D/E용) |
| `{disclaimer_text_N}` | N번째 고지 사항 본문 |
| `{bridge_sentence}` | 브리지 전환 문장 |
| `{icon_N}` | N번째 아이콘 (이모지 또는 SVG) |
| `{step_number_N}` | N번째 단계 번호 |
| `{feature_N}` | 비교표 N번째 기능/항목명 |
| `{usp_badge_N}` | N번째 USP 배지 텍스트 |
| `{usp_icon_N}` | N번째 USP 아이콘 (Solution-D용) |
| `{usp_title_N}` | N번째 USP 제목 (Solution-D용) |
| `{usp_desc_N}` | N번째 USP 설명 (Solution-D용) |
| `{solution_core_message}` | 솔루션 핵심 메시지 배너 (Solution-D용) |
| `{tag_N}` | 리뷰 카드 키워드 태그 |
