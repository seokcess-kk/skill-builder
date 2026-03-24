# 섹션 변형 HTML 템플릿 레퍼런스

> Claude가 블로그 이미지 HTML 파일을 생성할 때 참조하는 섹션별 변형(A/B/C/D/E) 템플릿 모음입니다.
> 각 템플릿은 `base-styles.css`의 실제 클래스명을 사용합니다.
> 테마 클래스(`theme-*`)는 `<body>` 태그에 적용하며, 섹션 `<div>`에는 포함하지 않습니다.
> 전문가 사진/이미지(`photo-box`, `img` 태그) 삽입은 금지합니다.

---

## 01 Hook (훅 — 첫인상 섹션)

### Hook-A: 중앙 정렬 인용문 + 세로라인 + 코너장식 (클래식 에디토리얼)

**선택 기준:** 신뢰감·권위가 핵심인 콘텐츠(의료·법률·금융 등). 정제된 인상을 줘야 할 때. 짧고 강한 선언형 문장이 있을 때.

```html
<div class="hook hook-a">
  <div class="corner-tl"></div>
  <div class="corner-br"></div>
  <div class="quote-deco">&ldquo;</div>
  <p class="quote-text">{quote_front}<em>{quote_highlight}</em>{quote_back}</p>
  <div class="quote-line"></div>
  <p class="quote-source">{quote_source}</p>
</div>
```

---

### Hook-B: 전면 다크 배경 + 흰 대형 Serif 타이포 + 하단 브랜드 태그 (임팩트)

**선택 기준:** 강렬한 첫 인상이 필요한 콘텐츠. 감정적 자극·문제 제기형 헤드라인. "충격적 사실"이나 "반전 메시지"를 전달할 때.

```html
<div class="hook hook-b">
  <p class="hb-label">{label_text}</p>
  <p class="quote-text">{quote_front}<em>{quote_accent}</em>{quote_back}</p>
  <div class="hb-divider"></div>
  <div class="hb-tag">
    <span class="hb-tag-text">{brand_tag_text}</span>
  </div>
</div>
```

---

### Hook-C: 좌측 대형 인용기호 + 우측 정렬 문구 + accent 라인 (비대칭)

**선택 기준:** 전문가 인용구나 고객 증언으로 시작하는 콘텐츠. 비대칭 레이아웃으로 시각적 긴장감을 원할 때. 인용 주체(전문가·브랜드)를 강조할 때.

```html
<div class="hook hook-c">
  <div class="hc-inner">
    <div class="hc-quote-mark">&ldquo;</div>
    <div class="hc-content">
      <div class="hc-accent-line"></div>
      <p class="quote-text">{quote_front}<em>{quote_highlight}</em>{quote_back}</p>
      <p class="quote-source">{quote_source}</p>
    </div>
  </div>
</div>
```

---

### Hook-D: 분할형 — 좌측 1/3 컬러 밴드 + 우측 2/3 대형 타이포 (모던)

**선택 기준:** 브랜드 정체성을 강하게 각인시키면서 정돈된 모던함을 원할 때. 좌측 컬러 밴드가 브랜드를 상징하고 우측 텍스트가 메시지를 전달. 시각적 분할로 기존 중앙 정렬 레이아웃과 확실히 차별화할 때.

```html
<div class="hook hook-d">
  <div class="hd-band">
    <span class="hd-brand-vertical">{brand_name}</span>
  </div>
  <div class="hd-content">
    <p class="hook-eyebrow">{eyebrow_text}</p>
    <h1 class="hook-headline">{headline_front}<em>{headline_highlight}</em>{headline_back}</h1>
    <div class="hd-accent-line"></div>
    <p class="hook-subline">{subline_text}</p>
  </div>
</div>
```

---

### Hook-E: 극미니멀 — 넓은 여백 + 단일 문장 중앙 (여백형)

**선택 기준:** 과도한 장식 없이 문장의 힘으로만 승부할 때. 고급 브랜드나 감성적 메시지에 적합. 넓은 여백이 문장에 무게감을 부여. 이전 포스트가 장식 과다했을 때 대비 효과.

```html
<div class="hook hook-e">
  <div class="he-content">
    <h1 class="hook-headline he-single">{headline_front}<em>{headline_highlight}</em>{headline_back}</h1>
  </div>
  <div class="he-bottom-line"></div>
</div>
```

---

## 02 Intro (전문가/브랜드 소개 섹션)

### Intro-A: 상단 컬러밴드 + 숫자 하이라이트 + 자격 태그 + 스피치 카드

**선택 기준:** 정량적 실적(경력, 시술 건수, 수강생 수 등)으로 신뢰를 줄 수 있을 때. 숫자가 시선을 끌고 자격 리스트가 뒷받침할 때.

```html
<div class="intro intro-a">
  <!-- 상단 컬러 밴드 -->
  <div class="intro-top">
    <div class="label-row">
      <span class="label-line"></span>
      <span class="label-text">{label_text}</span>
    </div>
    <p class="intro-top-name">{brand_name}</p>
    <p class="intro-top-role">{brand_role}</p>
  </div>

  <!-- 프로필 바디 -->
  <div class="profile-body">
    <!-- 숫자 하이라이트 (3열) -->
    <div class="stats-row">
      <div class="stat-item">
        <span class="stat-value">{stat_value_1}</span>
        <span class="stat-unit">{stat_unit_1}</span>
        <p class="stat-label">{stat_label_1}</p>
      </div>
      <div class="stat-item">
        <span class="stat-value">{stat_value_2}</span>
        <span class="stat-unit">{stat_unit_2}</span>
        <p class="stat-label">{stat_label_2}</p>
      </div>
      <div class="stat-item">
        <span class="stat-value">{stat_value_3}</span>
        <span class="stat-unit">{stat_unit_3}</span>
        <p class="stat-label">{stat_label_3}</p>
      </div>
    </div>

    <!-- 자격 태그 -->
    <div class="credentials">
      <span class="cred-item">{credential_1}</span>
      <span class="cred-item">{credential_2}</span>
      <span class="cred-item">{credential_3}</span>
    </div>
  </div>

  <!-- 스피치 카드 -->
  <div class="intro-speech">
    <p class="speech-line">{speech_front}<span class="speech-highlight">{speech_highlight}</span>{speech_back}</p>
  </div>
</div>
```

---

### Intro-B: 브랜드 헤더 + 자격 태그 + 스피치 카드

**선택 기준:** 핵심 강점과 자격을 한눈에 보여주고 싶을 때. 사진 없이 텍스트 기반으로 브랜드를 소개할 때.

```html
<div class="intro intro-b">
  <!-- 상단 정보 영역 -->
  <div class="ib-top">
    <div class="ib-info">
      <p class="ib-name">{brand_name}</p>
      <p class="ib-role">{brand_role}</p>
      <div class="ib-creds">
        <span class="cred-item">{credential_1}</span>
        <span class="cred-item">{credential_2}</span>
        <span class="cred-item">{credential_3}</span>
      </div>
    </div>
  </div>

  <!-- 스피치 카드 -->
  <div class="ib-speech">
    <div class="intro-speech">
      <p class="speech-line">{speech_front}<span class="speech-highlight">{speech_highlight}</span>{speech_back}</p>
    </div>
  </div>
</div>
```

---

### Intro-C: 미니멀 중앙 — 상단 라인 + 이름/직함 + 자격 + 스피치

**선택 기준:** 심플하고 모던한 분위기를 원할 때. 핵심 메시지 하나를 강하게 전달하고 싶을 때.

```html
<div class="intro intro-c">
  <div class="ic-top-line"></div>
  <p class="ic-name">{brand_name}</p>
  <p class="ic-role">{brand_role}</p>
  <div class="ic-creds">
    <span class="cred-item">{credential_1}</span>
    <span class="cred-item">{credential_2}</span>
    <span class="cred-item">{credential_3}</span>
  </div>
  <div class="ic-divider"></div>
  <div class="intro-speech">
    <p class="speech-line">{speech_front}<span class="speech-highlight">{speech_highlight}</span>{speech_back}</p>
  </div>
</div>
```

---

## 03 Pain (문제 제기 섹션)

### Pain-A: 좌측 컬러 보더 Voice Card 3장 + 내러티브

**선택 기준:** 세 가지 독립적인 고객 고통 포인트가 있을 때. 각 문제를 카드 형태로 명확히 구분하고 싶을 때. "이런 분들께"식 나열 구조일 때.

```html
<div class="pain pain-a">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{pain_section_title}</h2>

  <div class="pain-voices">
    <div class="voice-card">
      <p class="voice-text">{pain_voice_1}</p>
      <p class="voice-meta">{voice_meta_1}</p>
    </div>
    <div class="voice-card">
      <p class="voice-text">{pain_voice_2}</p>
      <p class="voice-meta">{voice_meta_2}</p>
    </div>
    <div class="voice-card">
      <p class="voice-text">{pain_voice_3}</p>
      <p class="voice-meta">{voice_meta_3}</p>
    </div>
  </div>

  <p class="narrator">{narrator_text}</p>
</div>
```

---

### Pain-B: Q&A 형식 — 질문 블록(다크) + 답변(라이트) + 브릿지 문장

**선택 기준:** 독자가 스스로 공감하도록 질문형 구조가 효과적일 때. "혹시 이런 경험 있으신가요?" 스타일. 고통을 대화 형식으로 풀어낼 때.

```html
<div class="pain pain-b">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{pain_section_title}</h2>

  <div class="pb-qa">
    <div class="pb-q">
      <p class="pb-q-label">QUESTION</p>
      <p class="pb-q-text">{pain_question}</p>
    </div>
    <div class="pb-a">
      <p class="pb-a-label">ANSWER</p>
      <p class="pb-a-text">{pain_answer}</p>
    </div>
  </div>

  <p class="pb-bridge">{bridge_front}<em>{bridge_highlight}</em>{bridge_back}</p>
</div>
```

---

### Pain-C: 스토리텔링 — 내러티브 본문 + 이탤릭 인용 강조 박스 + 하단 전환

**선택 기준:** 독자의 감정 이입을 극대화해야 할 때. 고통을 이야기 형식으로 서술할 때. 실제 고객 사례나 경험담이 있을 때.

```html
<div class="pain pain-c">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{pain_section_title}</h2>

  <p class="pc-narrative">{narrative_text}</p>

  <div class="pc-quote-box">
    <p class="pc-quote-text">{italic_quote_text}</p>
  </div>

  <p class="pc-transition">{transition_front}<em>{transition_highlight}</em>{transition_back}</p>
</div>
```

---

## Bridge (전환 섹션)

### Bridge-A: 라이트 배경 + 중앙 Serif 문장 + 상하 수평선

**선택 기준:** 부드럽고 자연스러운 섹션 전환이 필요할 때. 라이트 톤의 콘텐츠 흐름에서 전환점을 표시할 때. 희망적이거나 긍정적인 메시지로 넘어갈 때.

```html
<div class="bridge bridge-a">
  <div class="ba-rule"></div>
  <p class="bridge-text">{bridge_front}<em>{bridge_highlight}</em>{bridge_back}</p>
  <div class="ba-rule ba-rule-bottom"></div>
</div>
```

---

### Bridge-B: 풀너비 다크 컬러 밴드 + 흰 텍스트 + radial glow

**선택 기준:** 강한 섹션 구분이 필요할 때. 다크 톤으로 분위기 전환을 강조하고 싶을 때. 임팩트 있는 전환 메시지를 전달할 때.

```html
<div class="bridge bridge-b">
  <p class="bridge-text">{bridge_front}<em>{bridge_highlight}</em>{bridge_back}</p>
</div>
```

---

### Bridge-C: 라이트 배경 + 점(· · ·) 장식 + 이탤릭 Serif 문장

**선택 기준:** 가볍고 우아한 전환이 필요할 때. 장식적 요소로 시각적 리듬을 줄 때. 이탤릭 문체로 감성적인 브리지를 만들 때.

```html
<div class="bridge bridge-c">
  <div class="bc-dots">· · ·</div>
  <p class="bridge-text">{bridge_front}<em>{bridge_highlight}</em>{bridge_back}</p>
  <div class="bc-dots bc-dots-bottom">· · ·</div>
</div>
```

---

## 04 Why (원인 분석 섹션)

### Why-A: 다크 배경 + 2열 원인 카드 그리드 + 통계 블록 + 전환 문장

**선택 기준:** 수치·통계 데이터가 있고 이를 강조하고 싶을 때. 두 가지 대비 또는 네 가지 이유를 2x2 그리드로 보여줄 때. 신뢰도 높은 근거 기반 콘텐츠일 때.

```html
<div class="why why-a">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title tag-title">{why_section_title}</h2>
  <p class="tag-sub">{why_subtitle}</p>

  <!-- 2열 카드 그리드 -->
  <div class="cause-row">
    <div class="cause-card">
      <div class="cause-num">{cause_num_1}</div>
      <p class="cause-title">{cause_title_1}</p>
      <p class="cause-desc">{cause_desc_1}</p>
    </div>
    <div class="cause-card">
      <div class="cause-num">{cause_num_2}</div>
      <p class="cause-title">{cause_title_2}</p>
      <p class="cause-desc">{cause_desc_2}</p>
    </div>
  </div>
  <div class="cause-row">
    <div class="cause-card">
      <div class="cause-num">{cause_num_3}</div>
      <p class="cause-title">{cause_title_3}</p>
      <p class="cause-desc">{cause_desc_3}</p>
    </div>
    <div class="cause-card">
      <div class="cause-num">{cause_num_4}</div>
      <p class="cause-title">{cause_title_4}</p>
      <p class="cause-desc">{cause_desc_4}</p>
    </div>
  </div>

  <!-- 통계 블록 -->
  <div class="stat-block">
    <p class="stat-label">{stat_label}</p>
    <p class="stat-value">{stat_value}</p>
    <p class="stat-note">{stat_note}</p>
  </div>

  <!-- 전환 문장 -->
  <div class="transition">
    <p class="transition-text">{transition_front}<em>{transition_highlight}</em>{transition_back}</p>
  </div>
</div>
```

---

### Why-B: 라이트 배경 + 아이콘+텍스트 카드 세로 나열 + 인사이트 강조 박스

**선택 기준:** 밝고 친근한 톤이 필요할 때. 아이콘/이모지와 함께 이유를 나열할 때. 3~4개의 이유를 수직으로 시각화할 때.

```html
<div class="why why-b">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{why_section_title}</h2>

  <div class="wb-cards">
    <div class="wb-card">
      <div class="wb-icon">{icon_1}</div>
      <div class="wb-content">
        <p class="wb-title">{why_title_1}</p>
        <p class="wb-desc">{why_desc_1}</p>
      </div>
    </div>
    <div class="wb-card">
      <div class="wb-icon">{icon_2}</div>
      <div class="wb-content">
        <p class="wb-title">{why_title_2}</p>
        <p class="wb-desc">{why_desc_2}</p>
      </div>
    </div>
    <div class="wb-card">
      <div class="wb-icon">{icon_3}</div>
      <div class="wb-content">
        <p class="wb-title">{why_title_3}</p>
        <p class="wb-desc">{why_desc_3}</p>
      </div>
    </div>
  </div>

  <div class="wb-insight">
    <p class="wb-insight-text">{insight_front}<em>{insight_highlight}</em>{insight_back}</p>
  </div>
</div>
```

---

### Why-C: 다크 배경 + 세로 타임라인형(넘버 dot + 카드) + 결론 강조 박스

**선택 기준:** 이유들이 시간 순서나 단계적 논리를 가질 때. "첫째→둘째→셋째"의 인과관계를 보여줄 때. 스토리 흐름이 있는 근거 제시에 적합.

```html
<div class="why why-c">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title tag-title">{why_section_title}</h2>

  <div class="wc-timeline">
    <div class="wc-item">
      <div class="wc-dot">1</div>
      <p class="wc-title">{why_title_1}</p>
      <p class="wc-desc">{why_desc_1}</p>
    </div>
    <div class="wc-item">
      <div class="wc-dot">2</div>
      <p class="wc-title">{why_title_2}</p>
      <p class="wc-desc">{why_desc_2}</p>
    </div>
    <div class="wc-item">
      <div class="wc-dot">3</div>
      <p class="wc-title">{why_title_3}</p>
      <p class="wc-desc">{why_desc_3}</p>
    </div>
  </div>

  <div class="wc-conclusion">
    <p class="wc-conclusion-text">{conclusion_front}<em>{conclusion_highlight}</em>{conclusion_back}</p>
  </div>
</div>
```

---

## 05 Solution (솔루션 섹션)

### Solution-A: 타임라인 + 비교 테이블 + 클로징 인용

**선택 기준:** 단계별 접근 방식과 경쟁 비교가 모두 필요할 때. 과정을 설명하고 타사와의 차이를 표로 보여줄 때. 풍부한 콘텐츠 구조일 때.

```html
<div class="solution solution-a">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{solution_section_title}</h2>
  <p class="tag-sub">{solution_subtitle}</p>

  <!-- 타임라인 -->
  <div class="timeline">
    <div class="step">
      <div class="step-dot">01</div>
      <p class="step-title">{step_title_1}</p>
      <p class="step-desc">{step_desc_1}</p>
    </div>
    <div class="step">
      <div class="step-dot">02</div>
      <p class="step-title">{step_title_2}</p>
      <p class="step-desc">{step_desc_2}</p>
    </div>
    <div class="step">
      <div class="step-dot">03</div>
      <p class="step-title">{step_title_3}</p>
      <p class="step-desc">{step_desc_3}</p>
    </div>
  </div>

  <!-- 비교 테이블 -->
  <div class="compare">
    <table>
      <thead>
        <tr>
          <th>{compare_label_general}</th>
          <th>{brand_name}</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>{compare_item_1_general}</td><td>{compare_item_1_brand}</td></tr>
        <tr><td>{compare_item_2_general}</td><td>{compare_item_2_brand}</td></tr>
        <tr><td>{compare_item_3_general}</td><td>{compare_item_3_brand}</td></tr>
      </tbody>
    </table>
  </div>

  <!-- 클로징 -->
  <div class="closing">
    <p class="closing-text">{closing_front}<em>{closing_highlight}</em>{closing_back}</p>
  </div>
</div>
```

---

### Solution-B: 아이콘+텍스트 어프로치 카드 나열 + 체크리스트 + 클로징

**선택 기준:** 구체적인 방법론이나 접근 방식을 카드로 보여줄 때. 독자가 확인해야 할 항목을 체크리스트로 제공할 때. 실행 중심의 솔루션 콘텐츠일 때.

```html
<div class="solution solution-b">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{solution_section_title}</h2>

  <!-- 어프로치 카드 -->
  <div class="sb-approaches">
    <div class="approach-card">
      <div class="approach-icon">{approach_icon_1}</div>
      <div class="approach-content">
        <p class="approach-title">{approach_title_1}</p>
        <p class="approach-desc">{approach_desc_1}</p>
      </div>
    </div>
    <div class="approach-card">
      <div class="approach-icon">{approach_icon_2}</div>
      <div class="approach-content">
        <p class="approach-title">{approach_title_2}</p>
        <p class="approach-desc">{approach_desc_2}</p>
      </div>
    </div>
  </div>

  <!-- 체크리스트 -->
  <div class="sb-checklist">
    <p class="sb-checklist-title">{checklist_title}</p>
    <div class="check-item">
      <span class="check-icon">✓</span>
      <span class="check-text">{checklist_item_1}</span>
    </div>
    <div class="check-item">
      <span class="check-icon">✓</span>
      <span class="check-text">{checklist_item_2}</span>
    </div>
    <div class="check-item">
      <span class="check-icon">✓</span>
      <span class="check-text">{checklist_item_3}</span>
    </div>
  </div>

  <!-- 클로징 -->
  <div class="closing">
    <p class="closing-text">{closing_front}<em>{closing_highlight}</em>{closing_back}</p>
  </div>
</div>
```

---

### Solution-C: 비교 테이블 우선(상단) + USP 배지 3개(가로) + 클로징

**선택 기준:** 경쟁사와의 차별점이 콘텐츠의 핵심일 때. 비교표를 전면에 내세우고 USP(고유 판매 포인트)를 배지로 강조할 때. 전환 목적이 강한 광고성 콘텐츠에 적합.

```html
<div class="solution solution-c">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{solution_section_title}</h2>

  <!-- 비교 테이블 -->
  <div class="compare">
    <table>
      <thead>
        <tr>
          <th>{compare_label_general}</th>
          <th>{brand_name}</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>{compare_item_1_general}</td><td>{compare_item_1_brand}</td></tr>
        <tr><td>{compare_item_2_general}</td><td>{compare_item_2_brand}</td></tr>
        <tr><td>{compare_item_3_general}</td><td>{compare_item_3_brand}</td></tr>
      </tbody>
    </table>
  </div>

  <!-- USP 배지 3개 -->
  <div class="sc-usp-row">
    <div class="sc-usp">
      <div class="sc-usp-icon">{usp_icon_1}</div>
      <p class="sc-usp-label">{usp_label_1}</p>
      <p class="sc-usp-desc">{usp_desc_1}</p>
    </div>
    <div class="sc-usp">
      <div class="sc-usp-icon">{usp_icon_2}</div>
      <p class="sc-usp-label">{usp_label_2}</p>
      <p class="sc-usp-desc">{usp_desc_2}</p>
    </div>
    <div class="sc-usp">
      <div class="sc-usp-icon">{usp_icon_3}</div>
      <p class="sc-usp-label">{usp_label_3}</p>
      <p class="sc-usp-desc">{usp_desc_3}</p>
    </div>
  </div>

  <!-- 클로징 -->
  <div class="closing">
    <p class="closing-text">{closing_front}<em>{closing_highlight}</em>{closing_back}</p>
  </div>
</div>
```

---

### Solution-D: 매거진 그리드 — 2x2 USP 카드 + 핵심 메시지 배너

**선택 기준:** USP가 4개이고 모두 동등한 비중을 가질 때. 매거진 스타일의 정돈된 그리드 레이아웃. 시각적 균형과 정보 밀도를 동시에 달성하고 싶을 때. 타임라인이나 리스트 형태가 아닌 새로운 구조가 필요할 때.

```html
<div class="solution solution-d">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{solution_section_title}</h2>

  <!-- 2x2 USP 그리드 -->
  <div class="sd-grid">
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_1}</div>
      <p class="sd-card-title">{usp_title_1}</p>
      <p class="sd-card-desc">{usp_desc_1}</p>
    </div>
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_2}</div>
      <p class="sd-card-title">{usp_title_2}</p>
      <p class="sd-card-desc">{usp_desc_2}</p>
    </div>
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_3}</div>
      <p class="sd-card-title">{usp_title_3}</p>
      <p class="sd-card-desc">{usp_desc_3}</p>
    </div>
    <div class="sd-card">
      <div class="sd-card-icon">{usp_icon_4}</div>
      <p class="sd-card-title">{usp_title_4}</p>
      <p class="sd-card-desc">{usp_desc_4}</p>
    </div>
  </div>

  <!-- 핵심 메시지 배너 -->
  <div class="sd-banner">
    <p class="sd-banner-text">{banner_front}<em>{banner_highlight}</em>{banner_back}</p>
  </div>

  <!-- 클로징 -->
  <div class="closing">
    <p class="closing-text">{closing_front}<em>{closing_highlight}</em>{closing_back}</p>
  </div>
</div>
```

---

## 06 Proof (증거/신뢰 섹션)

### Proof-A: 3분할 통계 수치 행 + 인용 리뷰 카드 2장 + 면책 고지

**선택 기준:** 수치 기반 증거와 고객 리뷰를 함께 보여줄 때. 통계 3개와 리뷰 1~2개를 균형 있게 구성할 때. 신뢰도 극대화가 필요한 콘텐츠.

```html
<div class="proof proof-a">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{proof_section_title}</h2>

  <!-- 통계 3분할 -->
  <div class="stats-row">
    <div class="stat-item">
      <span class="stat-value">{stat_value_1}</span>
      <span class="stat-unit">{stat_unit_1}</span>
      <p class="stat-label">{stat_label_1}</p>
    </div>
    <div class="stat-item">
      <span class="stat-value">{stat_value_2}</span>
      <span class="stat-unit">{stat_unit_2}</span>
      <p class="stat-label">{stat_label_2}</p>
    </div>
    <div class="stat-item">
      <span class="stat-value">{stat_value_3}</span>
      <span class="stat-unit">{stat_unit_3}</span>
      <p class="stat-label">{stat_label_3}</p>
    </div>
  </div>

  <!-- 리뷰 헤더 + 카드 -->
  <div class="review-header">{review_header_text}</div>
  <div class="review">
    <div class="review-qm">&ldquo;</div>
    <p class="review-text">{review_text_1}</p>
    <div class="review-meta">
      <span class="review-dot"></span>
      <span class="review-info">{review_info_1}</span>
    </div>
  </div>
  <div class="review">
    <div class="review-qm">&ldquo;</div>
    <p class="review-text">{review_text_2}</p>
    <div class="review-meta">
      <span class="review-dot"></span>
      <span class="review-info">{review_info_2}</span>
    </div>
  </div>

  <!-- 면책 고지 -->
  <div class="disclaimer">{disclaimer_text}</div>
</div>
```

---

### Proof-B: Q&A 스피치 카드 + 인용 리뷰 카드 + 면책

**선택 기준:** 전문가의 Q&A 형식으로 신뢰를 쌓고 리뷰로 마무리할 때. 의료·법률·금융처럼 전문적 답변이 설득력 있는 분야. 콘텐츠가 대화형 구조일 때.

```html
<div class="proof proof-b">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{proof_section_title}</h2>

  <!-- Q&A 카드 -->
  <div class="pb-qa-card">
    <p class="pb-qa-q">{proof_question}</p>
    <p class="pb-qa-a">{proof_answer}</p>
  </div>

  <!-- 리뷰 카드 -->
  <div class="review">
    <div class="review-qm">&ldquo;</div>
    <p class="review-text">{review_text_1}</p>
    <div class="review-meta">
      <span class="review-dot"></span>
      <span class="review-info">{review_info_1}</span>
    </div>
  </div>

  <!-- 면책 고지 -->
  <div class="disclaimer">{disclaimer_text}</div>
</div>
```

---

### Proof-C: 별점/태그형 리뷰 카드(상단 별점 + 태그 + 텍스트) + 면책

**선택 기준:** 시각적으로 임팩트 있는 리뷰 중심 콘텐츠일 때. 별점과 키워드 태그를 함께 보여줄 때. 고객 만족도를 직관적으로 전달하고 싶을 때.

```html
<div class="proof proof-c">
  <div class="section-tag">
    <span class="tag-num">{tag_num}</span>
    <span class="tag-line"></span>
  </div>
  <h2 class="section-title">{proof_section_title}</h2>

  <div class="pc-reviews">
    <div class="pc-review-card">
      <div class="pc-stars">★★★★★</div>
      <div class="pc-tags">
        <span class="pc-tag">{tag_1}</span>
        <span class="pc-tag">{tag_2}</span>
      </div>
      <p class="pc-review-text">{review_text_1}</p>
      <p class="pc-review-meta">{review_meta_1}</p>
    </div>
    <div class="pc-review-card">
      <div class="pc-stars">★★★★★</div>
      <div class="pc-tags">
        <span class="pc-tag">{tag_3}</span>
        <span class="pc-tag">{tag_4}</span>
      </div>
      <p class="pc-review-text">{review_text_2}</p>
      <p class="pc-review-meta">{review_meta_2}</p>
    </div>
  </div>

  <!-- 면책 고지 -->
  <div class="disclaimer">{disclaimer_text}</div>
</div>
```

---

## 07 CTA (행동 유도 섹션)

### CTA-A: 다크 배경 + 코너장식 + Serif 클로징 + 아웃라인 버튼 + 브랜드 라벨

**선택 기준:** 클래식하고 권위 있는 분위기에서 전환을 유도할 때. 아웃라인 버튼으로 세련된 인상을 줄 때. 코너 장식으로 Hook-A와 시각적 일관성을 유지할 때.

```html
<div class="cta cta-a">
  <div class="corner-tl"></div>
  <div class="corner-br"></div>
  <p class="cta-label">{label_text}</p>
  <p class="cta-main">{cta_main_front}<em>{cta_main_highlight}</em>{cta_main_back}</p>
  <p class="cta-sub">{cta_sub_text}</p>
  <div class="cta-divider"></div>
  <div class="cta-info">
    <p class="info-line">{info_front}<span class="accent">{info_accent}</span>{info_back}</p>
    <p class="info-line">{info_line_2}</p>
  </div>
  <div class="cta-button">{cta_button_text}</div>
  <p class="goodbye">{goodbye_text}</p>
</div>
```

---

### CTA-B: 라이트 배경 + 상단 accent 라인 + 클로징 + 풀컬러 CTA 버튼 + 연락처

**선택 기준:** 밝고 친근한 톤으로 행동을 유도할 때. 브랜드 컬러 버튼으로 강한 시각적 CTA를 줄 때. 부드러운 설득이 필요한 콘텐츠에 적합.

```html
<div class="cta cta-b">
  <p class="cta-label">{label_text}</p>
  <p class="cta-main">{cta_main_text}</p>
  <p class="cta-sub">{cta_sub_text}</p>
  <div class="cta-button">{cta_button_text}</div>
  <div class="cta-contact">{contact_front}<span class="accent">{contact_accent}</span>{contact_back}</div>
</div>
```

---

### CTA-C: 다크 그라디언트 배경 + 대형 Serif 타이포 + 하단 미니멀 CTA

**선택 기준:** 마지막 섹션에서 강력한 인상으로 마무리할 때. 대형 타이포로 메시지를 압도적으로 전달할 때. 프리미엄 또는 감성 브랜드에 적합.

```html
<div class="cta cta-c">
  <p class="cc-main">{main_front}<em>{main_highlight}</em>{main_back}</p>
  <div class="cc-footer">
    <span class="cc-contact">{contact_text}</span>
    <div class="cc-divider-v"></div>
    <div class="cc-button">{cta_button_text}</div>
  </div>
</div>
```

---

### CTA-D: 분할형 — 좌측 다크(브랜드 메시지) + 우측 라이트(연락처/CTA)

**선택 기준:** 감성적 브랜드 메시지와 실용적 연락처 정보를 동시에 전달할 때. 좌우 대비로 시각적 임팩트와 정보 전달을 균형 있게 구현. 기존 전면 다크/전면 라이트 CTA와 차별화할 때.

```html
<div class="cta cta-d">
  <!-- 좌측: 다크 패널 -->
  <div class="cd-left">
    <p class="cd-label">{brand_eng_name}</p>
    <h2 class="cd-headline">{headline_front}<em>{headline_highlight}</em>{headline_back}</h2>
    <p class="cd-subtext">{cta_subtext}</p>
  </div>

  <!-- 우측: 라이트 패널 -->
  <div class="cd-right">
    <div class="cd-info-block">
      <p class="cd-brand-name">{brand_name}</p>
      <div class="cd-contact-list">
        <p class="cd-contact-item">{contact_phone}</p>
        <p class="cd-contact-item">{contact_address}</p>
        <p class="cd-contact-item">{contact_channel}</p>
      </div>
    </div>
    <div class="cta-button fullcolor">{cta_button_text}</div>
  </div>
</div>
```

---

### CTA-E: 카드 스택형 — 틴트 배경 + 플로팅 카드 (미니멀)

**선택 기준:** 미니멀하고 깔끔한 마무리가 필요할 때. 모던 브랜드에 적합. 장식을 최소화하고 하나의 카드에 모든 정보를 담아 정돈된 인상. 기존 CTA 변형들과 확실히 다른 구조적 느낌.

```html
<div class="cta cta-e">
  <div class="ce-card">
    <p class="ce-label">{brand_eng_name}</p>
    <div class="ce-divider"></div>
    <h2 class="ce-headline">{cta_headline}</h2>
    <p class="ce-subtext">{cta_subtext}</p>
    <div class="ce-contact">
      <p class="ce-contact-item">{brand_name} · {contact_phone}</p>
      <p class="ce-contact-item">{contact_address}</p>
    </div>
    <div class="cta-button ce-button">{cta_button_text}</div>
  </div>
</div>
```

---

## 10 Disclaimer (의료광고 법적 고지 섹션)

### Disclaimer-A: 틴트 배경 + 화이트 카드 3장 + 마지막 카드 accent 좌측 보더

**선택 기준:** 세 가지 독립적인 고지 항목이 있을 때. 각 항목을 카드로 명확히 구분하고 accent 색상으로 중요도를 표시할 때. 의료·금융 규정 준수 콘텐츠.

```html
<div class="disclaimer-section disclaimer-a">
  <div class="disc-header">
    <h2 class="disc-title">{disclaimer_title}</h2>
    <div class="disc-line"></div>
  </div>

  <div class="disc-block">
    <p class="disc-text">{disclaimer_text_1}</p>
  </div>
  <div class="disc-block">
    <p class="disc-text">{disclaimer_text_2}</p>
  </div>
  <div class="disc-block-accent">
    <p class="disc-text"><strong>{disclaimer_strong_3}</strong> {disclaimer_text_3}</p>
  </div>

  <div class="disc-footer">
    <p class="disc-footer-text">{footer_text}</p>
  </div>
</div>
```

---

### Disclaimer-B: 화이트 배경 + 보더 top 구분 + 좌측 넘버 + 브랜드 푸터

**선택 기준:** 고지 항목들이 순서나 우선순위를 가질 때. 넘버링으로 명확한 구분이 필요할 때. 법적 요건이 많아 리스트 형태가 적합할 때.

```html
<div class="disclaimer-section disclaimer-b">
  <div class="db-header">
    <h2 class="db-title">{disclaimer_title}</h2>
    <p class="db-subtitle">{disclaimer_subtitle}</p>
  </div>

  <div class="db-item">
    <span class="db-num">01</span>
    <div class="db-content">
      <p class="db-item-title">{item_title_1}</p>
      <p class="db-item-text">{item_text_1}</p>
    </div>
  </div>
  <div class="db-item">
    <span class="db-num">02</span>
    <div class="db-content">
      <p class="db-item-title">{item_title_2}</p>
      <p class="db-item-text">{item_text_2}</p>
    </div>
  </div>
  <div class="db-item">
    <span class="db-num">03</span>
    <div class="db-content">
      <p class="db-item-title">{item_title_3}</p>
      <p class="db-item-text">{item_text_3}</p>
    </div>
  </div>

  <div class="db-footer">
    <span class="db-brand"><span class="db-brand-accent">{brand_name}</span> {footer_text}</span>
  </div>
</div>
```

---

### Disclaimer-C: 라이트 배경 + 단일 카드 안에 3항목 (수평선 구분) + 하단 브랜드

**선택 기준:** 고지 사항을 하나의 카드에 통합해서 보여줄 때. 미니멀하게 처리하고 싶을 때. 고지 내용이 간결하고 분량이 적을 때.

```html
<div class="disclaimer-section disclaimer-c">
  <div class="dc-header">
    <h2 class="dc-title">{disclaimer_title}</h2>
    <div class="dc-title-line"></div>
  </div>

  <div class="dc-card">
    <div class="dc-item">
      <p class="dc-item-title">{item_title_1}</p>
      <p class="dc-item-text">{item_text_1}</p>
    </div>
    <div class="dc-item">
      <p class="dc-item-title">{item_title_2}</p>
      <p class="dc-item-text">{item_text_2}</p>
    </div>
    <div class="dc-item">
      <p class="dc-item-title">{item_title_3}</p>
      <p class="dc-item-text">{item_text_3}</p>
    </div>
  </div>

  <p class="dc-brand"><strong>{brand_name}</strong> {footer_text}</p>
</div>
```

---

## 플레이스홀더 마커 목록

| 마커 | 설명 |
|------|------|
| `{brand_name}` | 브랜드/서비스 이름 |
| `{brand_eng_name}` | 브랜드 영문명 (CTA-D/E용) |
| `{brand_role}` | 브랜드 역할/직함 |
| `{label_text}` | 상단 라벨 텍스트 |
| `{quote_text}` | 인용구 본문 |
| `{quote_source}` | 인용 출처 |
| `{quote_highlight}` | 인용구 내 강조 텍스트 (`<em>` 래핑) |
| `{eyebrow_text}` | 헤드라인 위 소제목 (아이브로우) |
| `{headline_text}` | 메인 헤드라인 텍스트 |
| `{subline_text}` | 서브 헤드라인 텍스트 |
| `{credential_N}` | N번째 자격증/학위 등 자격 태그 |
| `{speech_text}` | 스피치 카드 텍스트 |
| `{speech_highlight}` | 스피치 내 강조 텍스트 |
| `{stat_value_N}` | N번째 통계 수치 |
| `{stat_unit_N}` | N번째 통계 단위 |
| `{stat_label_N}` | N번째 통계 레이블 |
| `{pain_voice_N}` | N번째 고통 보이스 카드 텍스트 |
| `{voice_meta_N}` | N번째 보이스 카드 메타 정보 |
| `{narrator_text}` | 내러티브 문단 텍스트 |
| `{bridge_sentence}` | 브리지 전환 문장 |
| `{icon_N}` | N번째 아이콘 (이모지) |
| `{tag_num}` | 섹션 태그 번호 |
| `{review_text_N}` | N번째 리뷰 본문 |
| `{review_info_N}` | N번째 리뷰어 정보 |
| `{review_meta_N}` | N번째 리뷰 메타 텍스트 |
| `{tag_N}` | 리뷰 카드 키워드 태그 |
| `{cta_headline}` | CTA 헤드라인 |
| `{cta_button_text}` | CTA 버튼 텍스트 |
| `{cta_sub_text}` | CTA 서브 텍스트 |
| `{contact_phone}` | 연락처 전화번호 |
| `{contact_address}` | 주소 |
| `{contact_channel}` | 예약/상담 채널 |
| `{goodbye_text}` | 마무리 인사 텍스트 (CTA-A용) |
| `{disclaimer_title}` | 고지사항 섹션 제목 |
| `{disclaimer_text_N}` | N번째 고지 사항 본문 |
| `{item_title_N}` | N번째 고지 항목 제목 |
| `{item_text_N}` | N번째 고지 항목 본문 |
| `{footer_text}` | 푸터 텍스트 |
| `{usp_icon_N}` | N번째 USP 아이콘 |
| `{usp_title_N}` | N번째 USP 제목 |
| `{usp_desc_N}` | N번째 USP 설명 |
| `{usp_label_N}` | N번째 USP 라벨 (Solution-C용) |
| `{compare_label_general}` | 비교표 일반 열 헤더 |
| `{compare_item_N_general}` | N번째 비교 항목 일반 값 |
| `{compare_item_N_brand}` | N번째 비교 항목 브랜드 값 |
