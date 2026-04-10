"""
Blog Post Generator — Streamlit UI

네이버 블로그 포스트 자동 생성 도구
브랜드 이미지 + SEO 최적화 원고를 결합하여 완성된 블로그 게시물을 생성합니다.
"""

import streamlit as st
import subprocess
import sys
import os
import json
import re
import html as html_lib
import shutil
from pathlib import Path
from datetime import date

# 프로젝트 루트 경로
ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
OUTPUT = ROOT / "output"

# .env 파일에서 환경변수 로드
_env_file = ROOT / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


# ─── Page Config ───
st.set_page_config(
    page_title="Blog Post Generator",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS (ui-ux-pro-max: Soft UI + SaaS Tool) ───
st.markdown("""
<style>
    /* ── Design tokens ── */
    :root {
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
    }

    /* ── Base: Soft UI Evolution ── */
    .stApp {
        background-color: #F8F9FB;
        font-family: 'Pretendard', 'Noto Sans CJK KR', -apple-system, BlinkMacSystemFont, system-ui, 'Malgun Gothic', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    section[data-testid="stSidebar"] .stMarkdown h1 {
        font-size: 1.15rem;
        color: #111827;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    section[data-testid="stSidebar"] .stMarkdown h5 {
        font-size: 0.78rem;
        color: #6B7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 4px;
    }

    /* ── Metric cards (결과 카드) ── */
    .metric-row {
        display: flex;
        gap: 12px;
        margin: 16px 0;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px 16px;
        flex: 1;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 200ms ease;
    }
    .metric-card:hover {
        box-shadow: var(--shadow-md);
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.72rem;
        color: #6B7280;
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* ── Status cards ── */
    .status-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: var(--shadow-sm);
    }
    .status-card.success { border-left: 3px solid #22C55E; }
    .status-card.running { border-left: 3px solid #3B82F6; }
    .status-card.pending { border-left: 3px solid #D1D5DB; }
    .status-card.error   { border-left: 3px solid #EF4444; }

    .phase-header {
        font-size: 0.7rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .phase-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 6px;
    }
    .phase-detail {
        font-size: 0.82rem;
        color: #6B7280;
        line-height: 1.6;
    }

    /* ── Hide streamlit chrome ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #6B7280;
    }
    .empty-state-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    .empty-state-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }
    .empty-state-desc {
        font-size: 0.85rem;
    }

    /* ── Tag chips ── */
    .tag-chip {
        display: inline-block;
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #93C5FD;
        border-radius: 16px;
        padding: 4px 12px;
        margin: 3px 2px;
        font-size: 0.82rem;
        font-weight: 500;
    }

    /* ── Tag frequency bar ── */
    .tag-freq-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 2px 0;
    }
    .tag-freq-name {
        min-width: 120px;
        font-size: 0.82rem;
    }
    .tag-freq-bar {
        background: #DBEAFE;
        border-radius: 4px;
        height: 16px;
    }
    .tag-freq-count {
        font-size: 0.75rem;
        color: #6B7280;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: all 200ms ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    .stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 10px 20px;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* ── Progress bar color ── */
    .stProgress > div > div > div {
        background: #3B82F6;
    }

    /* ── Reduced motion (UUPM checklist) ── */
    @media (prefers-reduced-motion: reduce) {
        .metric-card,
        .stButton > button,
        .stButton > button:hover,
        .stButton > button:active {
            transition: none !important;
            transform: none !important;
        }
    }

    /* ── Responsive metric cards ── */
    @media (max-width: 640px) {
        .metric-row {
            flex-wrap: wrap;
        }
        .metric-card {
            flex: 1 1 calc(50% - 8px);
            min-width: 120px;
        }
    }

    /* ── Focus-visible for keyboard navigation ── */
    .stButton > button:focus-visible {
        outline: 2px solid #3B82F6;
        outline-offset: 2px;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
    }
    .stTabs [data-baseweb="tab"]:focus-visible {
        outline: 2px solid #3B82F6;
        outline-offset: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ───

def _extract_file_text(uploaded_file):
    """업로드된 파일에서 텍스트를 추출합니다."""
    name = uploaded_file.name.lower()

    if name.endswith((".txt", ".md")):
        raw = uploaded_file.read()
        for enc in ("utf-8", "cp949", "euc-kr"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")

    if name.endswith(".docx"):
        try:
            import docx
            from io import BytesIO
            doc = docx.Document(BytesIO(uploaded_file.read()))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            st.warning("docx 지원을 위해 `pip install python-docx`가 필요합니다.")
            return None

    if name.endswith(".pdf"):
        try:
            import fitz  # PyMuPDF
            from io import BytesIO
            pdf = fitz.open(stream=BytesIO(uploaded_file.read()), filetype="pdf")
            return "\n\n".join(page.get_text() for page in pdf)
        except ImportError:
            st.warning("PDF 지원을 위해 `pip install PyMuPDF`가 필요합니다.")
            return None

    return None


def run_script(script_name, args, cwd=None, timeout=300):
    """Python 스크립트 실행 및 결과 반환 (기본 timeout: 300초)"""
    cmd = [sys.executable, str(SCRIPTS / script_name)] + args
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd or str(ROOT),
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        class _Timeout:
            returncode = -1
            stdout = ""
            stderr = "타임아웃: 제한 시간을 초과했습니다."
        return _Timeout()
    return result


def slugify(text):
    """키워드를 폴더명으로 변환"""
    text = re.sub(r'[^\w가-힣]', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text.lower() if text.isascii() else text


def get_output_dir(keyword_slug):
    return OUTPUT / keyword_slug


def status_card(phase, title, detail, status="pending"):
    """상태 카드 HTML (XSS 방어: 사용자 입력 escape)"""
    safe_phase = html_lib.escape(str(phase))
    safe_title = html_lib.escape(str(title))
    safe_detail = html_lib.escape(str(detail))
    safe_status = html_lib.escape(str(status))
    st.markdown(f"""
    <div class="status-card {safe_status}" role="status" aria-label="{safe_phase} — {safe_title}: {safe_detail}">
        <div class="phase-header">{safe_phase}</div>
        <div class="phase-title">{safe_title}</div>
        <div class="phase-detail">{safe_detail}</div>
    </div>
    """, unsafe_allow_html=True)


def check_env_vars():
    """필수 환경변수 확인"""
    missing = []
    if not os.environ.get("NAVER_CLIENT_ID"):
        missing.append("NAVER_CLIENT_ID")
    if not os.environ.get("NAVER_CLIENT_SECRET"):
        missing.append("NAVER_CLIENT_SECRET")
    return missing


def check_optional_env():
    """선택 환경변수 확인 (이미지 생성용)"""
    warnings = []
    if not os.environ.get("GOOGLE_API_KEY"):
        warnings.append("GOOGLE_API_KEY (SEO 이미지 생성에 필요)")
    if not shutil.which("claude.cmd") and not shutil.which("claude"):
        warnings.append("claude CLI (원고/브랜드 이미지 생성에 필요)")
    return warnings


# ─── Session State ───

if "phase" not in st.session_state:
    st.session_state.phase = "input"
if "seo_result" not in st.session_state:
    st.session_state.seo_result = None
if "validation_result" not in st.session_state:
    st.session_state.validation_result = None
if "running" not in st.session_state:
    st.session_state.running = False


# ─── Sidebar ───

with st.sidebar:
    st.markdown("# ✏️ Blog Post Generator")
    st.caption("네이버 블로그 포스트 자동 생성")

    st.divider()

    st.markdown("##### SEO 원고 (seo-writer)")
    keyword = st.text_input(
        "타겟 키워드 *",
        placeholder="예: 웨스턴돔다이어트",
        help="네이버 검색 상위노출을 노리는 키워드",
    )

    st.divider()

    st.markdown("##### 브랜드 이미지 (image-generator)")
    brand_name = st.text_input(
        "브랜드명 *",
        placeholder="예: 바디핏한의원",
        help="브랜드 섹션 이미지에 표시될 이름",
    )
    homepage_url = st.text_input(
        "홈페이지 URL",
        placeholder="예: https://example.com",
        help="브랜드 색상/톤 자동 추출",
    )

    # 파일 업로드 → session_state에 저장하여 text_area에 반영
    uploaded_file = st.file_uploader(
        "원고 파일 첨부",
        type=["txt", "md", "docx", "pdf"],
        help="원고 파일을 업로드하면 텍스트를 자동 추출합니다.",
    )
    if uploaded_file:
        file_text = _extract_file_text(uploaded_file)
        if file_text:
            st.session_state["_uploaded_manuscript"] = file_text
            st.success(f"{uploaded_file.name} — {len(file_text):,}자 추출")
    elif "_uploaded_manuscript" in st.session_state and not uploaded_file:
        # 파일이 제거되면 업로드 텍스트도 초기화
        del st.session_state["_uploaded_manuscript"]

    _default_manuscript = st.session_state.get("_uploaded_manuscript", "")
    brand_manuscript = st.text_area(
        "브랜드 원고 / 주제",
        value=_default_manuscript,
        placeholder="브랜드 소개, 서비스 특장점, 원고 등을 입력하세요.\n\n예:\n- 체질 분석 기반 맞춤 다이어트\n- 식단 + 운동 + 모니터링 통합 관리\n- 일산 웨스턴돔 4층",
        height=200,
        help="브랜드 이미지 섹션(Hook~CTA) 내용의 소재. 키워드/주제만 입력해도 됩니다.",
    )

    st.divider()

    st.markdown("##### 옵션")
    blog_count = st.slider("상위글 분석 수", 3, 10, 7)

    st.divider()

    # 환경변수 상태 표시
    missing_env = check_env_vars()
    optional_env = check_optional_env()
    if missing_env:
        st.error(f"필수 환경변수 미설정: {', '.join(missing_env)}")
    else:
        st.success("필수 환경변수 OK")
    if optional_env:
        st.warning(f"선택: {', '.join(optional_env)}")

    st.divider()

    # 입력 검증
    seo_ready = keyword and not missing_env
    brand_ready = bool(brand_name)
    inputs_ready = seo_ready and brand_ready

    # 🚀 실행 버튼 (사이드바 하단)
    run_clicked = st.button(
        "🚀 원스톱 생성",
        use_container_width=True,
        type="primary",
        disabled=not inputs_ready or st.session_state.running,
    )
    if not inputs_ready:
        missing = []
        if not keyword:
            missing.append("타겟 키워드")
        if not brand_name:
            missing.append("브랜드명")
        if missing_env:
            missing += missing_env
        st.caption(f"필요: {', '.join(missing)}")


# ─── Main Content ───

# Header
st.markdown("## 네이버 블로그 포스트 생성")
st.caption("SEO 최적화 원고 + 브랜드 이미지 → 완성 게시물")

if not inputs_ready:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">&#9997;&#65039;</div>
        <div class="empty-state-title">좌측 사이드바에서 정보를 입력하세요</div>
        <div class="empty-state-desc">타겟 키워드와 브랜드명을 입력한 후<br><b>원스톱 생성</b> 버튼을 클릭하면 자동으로 블로그 포스트가 생성됩니다.<br><span style="color:#6B7280;font-size:0.85em">홈페이지 URL은 선택 사항입니다 (입력 시 브랜드 컬러/톤 자동 추출)</span></div>
    </div>
    """, unsafe_allow_html=True)
else:
    slug = slugify(keyword)
    out_dir = get_output_dir(slug)

    # 경로 정의
    analysis_dir = out_dir / "seo" / "analysis"
    content_dir = out_dir / "seo" / "content"
    images_dir = out_dir / "seo" / "images"
    final_dir = out_dir / "final"
    branded_dir = out_dir / "branded" / "png"

    competitor_pages = analysis_dir / "competitor-pages.json"
    analysis_json = analysis_dir / "competitor-analysis.json"
    analysis_summary_path = analysis_dir / "analysis-summary.md"
    seo_content_path = content_dir / "seo-content.md"
    prompts_json = images_dir / "prompts.json"

    # ─── 원스톱 실행 (사이드바 버튼에 의해 트리거) ───

    if run_clicked:
        st.session_state.running = True
        progress = st.progress(0, text="준비 중...")
        log = st.empty()
        error_occurred = False

        try:
            # ── Step 1: 크롤링 + 분석 ──
            progress.progress(5, text="Step 1/7 — 상위글 수집 중...")
            log.info(f"'{keyword}' 상위 {blog_count}개 블로그 크롤링 중...")
            analysis_dir.mkdir(parents=True, exist_ok=True)
            result = run_script("fetch_competitors.py", [
                "--keyword", keyword,
                "--output-dir", str(analysis_dir),
                "--count", str(blog_count),
            ])
            if result.returncode != 0:
                st.error("Step 1 실패: 상위글 수집")
                st.code(result.stderr[-500:] if result.stderr else "Unknown error")
                error_occurred = True

            if not error_occurred and competitor_pages.exists():
                progress.progress(10, text="Step 1/7 — 패턴 분석 중...")
                result = run_script("analyze_competitors.py", [
                    "--input", str(competitor_pages),
                    "--keyword", keyword,
                    "--output-dir", str(analysis_dir),
                ])
                if result.returncode != 0:
                    st.error("Step 1 실패: 패턴 분석")
                    error_occurred = True

            # ── Step 2: SEO 원고 작성 (내부 검증+자동수정 포함) ──
            if not error_occurred and analysis_json.exists():
                progress.progress(18, text="Step 2/7 — AI 원고 작성 중...")
                log.info("Claude가 SEO 원고를 작성 중...")
                content_dir.mkdir(parents=True, exist_ok=True)
                result = run_script("generate_seo_content.py", [
                    "--keyword", keyword,
                    "--analysis", str(analysis_json),
                    "--output-dir", str(content_dir),
                ], timeout=600)
                if result.returncode != 0:
                    st.error("Step 2 실패: 원고 생성")
                    st.code(result.stderr[-500:] if result.stderr else result.stdout[-500:] if result.stdout else "Unknown error")
                    error_occurred = True

            # ── Step 3: SEO 검증 (이미지 삽입 전 — skip_images) ──
            if not error_occurred and seo_content_path.exists():
                progress.progress(28, text="Step 3/7 — SEO 검증 중...")
                v_args = [
                    "--content", str(seo_content_path),
                    "--keyword", keyword,
                    "--skip-images",
                ]
                if analysis_json.exists():
                    v_args += ["--analysis", str(analysis_json)]
                run_script("validate_seo.py", v_args)

            # ── Step 4: SEO 이미지 (마커 삽입 + 프롬프트 + Gemini) ──
            if not error_occurred and seo_content_path.exists():
                # 4-1: 원고 기반 이미지 마커 삽입
                progress.progress(35, text="Step 4/7 — AI 이미지 배치 중...")
                log.info("Claude가 원고에 맞는 이미지를 배치 중...")
                img_marker_args = [
                    "--seo-content", str(seo_content_path),
                    "--keyword", keyword,
                ]
                if analysis_json.exists():
                    img_marker_args += ["--analysis", str(analysis_json)]
                result = run_script("insert_image_markers.py", img_marker_args, timeout=600)
                if result.returncode != 0:
                    st.warning("이미지 마커 삽입 실패. 이미지 없이 진행합니다.")
                else:
                    # 4-2: 프롬프트 생성
                    progress.progress(45, text="Step 4/7 — 이미지 프롬프트 생성 중...")
                    images_dir.mkdir(parents=True, exist_ok=True)
                    result = run_script("build_prompts.py", [
                        "--seo-content", str(seo_content_path),
                        "--output-dir", str(images_dir),
                    ])
                    if result.returncode == 0 and prompts_json.exists():
                        # 4-3: Gemini 이미지 생성
                        progress.progress(50, text="Step 4/7 — Gemini 이미지 생성 중...")
                        log.info("Gemini SEO 이미지 생성 중... (1장당 약 10초)")
                        run_script("generate_images.py", [
                            "--prompts-file", str(prompts_json),
                            "--output-dir", str(images_dir),
                        ])

            # ── Step 5: SEO 최종 검증 (이미지 포함) ──
            if not error_occurred and seo_content_path.exists():
                progress.progress(62, text="Step 5/7 — SEO 최종 검증 중...")
                v_args = ["--content", str(seo_content_path), "--keyword", keyword]
                if analysis_json.exists():
                    v_args += ["--analysis", str(analysis_json)]
                run_script("validate_seo.py", v_args)
                validation_json_path = content_dir / "seo-validation.json"
                if validation_json_path.exists():
                    st.session_state.validation_result = json.loads(validation_json_path.read_text(encoding="utf-8"))

            # ── Step 5-1: SEO 단독 HTML 생성 ──
            if not error_occurred and seo_content_path.exists():
                seo_html_args = [
                    "--seo-content", str(seo_content_path),
                    "--output-dir", str(content_dir),
                    "--brand-name", brand_name,
                    "--keyword", keyword,
                    "--seo-only",
                ]
                # 제목
                seo_meta_path = content_dir / "seo-meta.json"
                if seo_meta_path.exists():
                    try:
                        _title = json.loads(seo_meta_path.read_text(encoding="utf-8")).get("title", "")
                        if _title:
                            seo_html_args += ["--title", _title]
                    except (json.JSONDecodeError, OSError):
                        pass
                # 디자인 플랜에서 컬러/폰트 (있으면)
                _plan_path = out_dir / "branded" / "html" / "_design_plan.json"
                if _plan_path.exists():
                    try:
                        _dp = json.loads(_plan_path.read_text(encoding="utf-8"))
                        seo_html_args += ["--primary-color", _dp.get("primary_color", "#333333")]
                        seo_html_args += ["--font-pairing", _dp.get("font_pairing", "serif-classic")]
                    except (json.JSONDecodeError, OSError):
                        pass
                # SEO 이미지 디렉토리
                if images_dir.exists():
                    seo_html_args += ["--seo-images-dir", str(images_dir)]
                run_script("compose_final.py", seo_html_args)

            # ── Step 6: 브랜드 섹션 이미지 (HTML + PNG) ──
            if not error_occurred:
                progress.progress(68, text="Step 6/7 — 브랜드 섹션 이미지 생성 중...")
                log.info("Claude가 브랜드 섹션 HTML을 생성 중... (약 5~10분)")
                branded_html_dir = out_dir / "branded" / "html"
                branded_html_dir.mkdir(parents=True, exist_ok=True)

                gen_args = [
                    "--keyword", keyword,
                    "--brand-name", brand_name,
                    "--output-dir", str(branded_html_dir),
                ]
                if homepage_url:
                    gen_args += ["--homepage", homepage_url]
                if brand_manuscript:
                    gen_args += ["--manuscript", brand_manuscript]

                result = run_script("generate_brand_html.py", gen_args, timeout=1800)

                has_brand_htmls = any(branded_html_dir.glob("*.html"))

                if result.returncode != 0:
                    if result.returncode == -1:
                        st.warning("브랜드 이미지 생성 타임아웃. (개별 실행 탭에서 재시도 가능)")
                    else:
                        st.warning("브랜드 이미지 생성 실패.")
                    error_detail = ""
                    if result.stdout:
                        error_detail += f"STDOUT:\n{result.stdout[-800:]}\n"
                    if result.stderr:
                        error_detail += f"STDERR:\n{result.stderr[-500:]}"
                    if error_detail:
                        with st.expander("오류 상세"):
                            st.code(error_detail[:1500])

                # HTML이 1개라도 있으면 PNG 렌더링 시도
                if has_brand_htmls:
                    progress.progress(88, text="Step 6/7 — PNG 렌더링 중...")
                    log.info("HTML → PNG 변환 중...")
                    branded_dir.mkdir(parents=True, exist_ok=True)
                    result = run_script("render_chrome.py", [
                        str(branded_html_dir), str(branded_dir), "--width", "680",
                    ])
                    if result.returncode != 0:
                        st.warning("PNG 렌더링 실패 (HTML은 생성됨).")
                elif result.returncode != 0:
                    st.info("SEO 원고만으로 진행합니다.")

            # ── Step 7: 최종 HTML 조합 ──
            if not error_occurred and seo_content_path.exists():
                progress.progress(94, text="Step 7/7 — 최종 HTML 조합 중...")
                final_dir.mkdir(parents=True, exist_ok=True)
                c_args = [
                    "--seo-content", str(seo_content_path),
                    "--output-dir", str(final_dir),
                    "--brand-name", brand_name,
                    "--keyword", keyword,
                ]
                has_branded = branded_dir.exists() and any(branded_dir.glob("*.png"))
                if has_branded:
                    c_args += ["--branded-dir", str(branded_dir)]
                if images_dir.exists():
                    c_args += ["--seo-images-dir", str(images_dir)]
                # 제목 전달
                seo_meta_path = content_dir / "seo-meta.json"
                if seo_meta_path.exists():
                    try:
                        _title = json.loads(seo_meta_path.read_text(encoding="utf-8")).get("title", "")
                        if _title:
                            c_args += ["--title", _title]
                    except (json.JSONDecodeError, OSError):
                        pass

                result = run_script("compose_final.py", c_args)
                if result.returncode != 0:
                    st.error("Step 7 실패: 최종 HTML 생성")
                    st.code(result.stderr[-500:] if result.stderr else "Unknown error")
                    error_occurred = True

            # 완료
            if not error_occurred:
                progress.progress(100, text="완료!")
                log.empty()
                st.balloons()
                st.success("블로그 포스트 생성 완료!")
                st.rerun()
            else:
                progress.progress(100, text="오류 발생 — 아래 로그를 확인하세요")
                log.empty()
        except Exception as e:
            st.error(f"예기치 않은 오류: {e}")
        finally:
            st.session_state.running = False

    st.divider()

    # ─── 결과 표시 + 개별 Step 제어 ───

    tab_result, tab_steps, tab_preview = st.tabs(["📊 결과", "🔧 개별 실행", "👁️ 미리보기"])

    # ── 결과 탭 ──
    with tab_result:
        # 브랜드 이미지 누락 경고
        has_branded_pngs = branded_dir.exists() and any(branded_dir.glob("*.png"))
        if not has_branded_pngs and (final_dir.exists() and any(final_dir.glob("*.html"))):
            st.warning(
                "⚠️ 브랜드 섹션 이미지가 생성되지 않았습니다. "
                "최종 HTML에 브랜드 이미지가 포함되지 않았을 수 있습니다.\n\n"
                "**개별 실행** 탭에서 **Step 3 (브랜드 섹션 이미지)**을 다시 실행해보세요."
            )

        # SEO 제목/태그 메타
        seo_meta_path = content_dir / "seo-meta.json"
        if seo_meta_path.exists():
            try:
                seo_meta = json.loads(seo_meta_path.read_text(encoding="utf-8"))
                seo_title = seo_meta.get("title", "")
                seo_tags = seo_meta.get("tags", [])
                title_candidates = seo_meta.get("title_candidates", [])

                if title_candidates and len(title_candidates) > 1:
                    st.markdown("**제목 선택**")
                    options = [f"{i+1}. {t}" for i, t in enumerate(title_candidates)]
                    selected = st.radio(
                        "제목을 선택하세요",
                        options=options,
                        index=0,
                        label_visibility="collapsed",
                        key="title_select",
                    )
                    selected_idx = options.index(selected)
                    chosen_title = title_candidates[selected_idx]
                    if chosen_title != seo_meta.get("title", ""):
                        seo_meta["title"] = chosen_title
                        seo_meta_path.write_text(
                            json.dumps(seo_meta, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                elif seo_title:
                    st.markdown("**제목**")
                    st.code(seo_title, language=None)

                if seo_tags:
                    st.markdown(f"**생성 태그** ({len(seo_tags)}개)")
                    chips = " ".join(
                        f'<span class="tag-chip">#{html_lib.escape(t)}</span>'
                        for t in seo_tags
                    )
                    st.markdown(chips, unsafe_allow_html=True)
                    st.code(", ".join(seo_tags), language=None)
            except (json.JSONDecodeError, KeyError):
                pass

        # SEO 검증 결과
        validation_json = content_dir / "seo-validation.json"
        if validation_json.exists():
            data = json.loads(validation_json.read_text(encoding="utf-8"))
            grade = data.get("grade", "?")
            grade_colors = {"A": "green", "B": "blue", "C": "orange", "D": "red"}
            st.markdown(f"""
            <div class="metric-row" role="group" aria-label="SEO 검증 결과">
                <div class="metric-card" role="group" aria-label="SEO 등급 {grade}">
                    <div class="metric-value" style="color: {grade_colors.get(grade, 'gray')}">{grade}</div>
                    <div class="metric-label">SEO 등급</div>
                </div>
                <div class="metric-card" role="group" aria-label="글자수 {data.get('char_count', 0):,}자">
                    <div class="metric-value">{data.get('char_count', 0):,}</div>
                    <div class="metric-label">글자수</div>
                </div>
                <div class="metric-card" role="group" aria-label="키워드 밀도 {data.get('keyword_density_pct', 0)}%">
                    <div class="metric-value">{data.get('keyword_density_pct', 0)}%</div>
                    <div class="metric-label">키워드 밀도</div>
                </div>
                <div class="metric-card" role="group" aria-label="이미지 {data.get('image_count', 0)}장">
                    <div class="metric-value">{data.get('image_count', 0)}</div>
                    <div class="metric-label">이미지</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if data.get("issues"):
                st.warning(f"수정 필요 ({len(data['issues'])}건): " + " / ".join(data["issues"]))

        # 생성된 이미지 표시
        if images_dir.exists():
            pngs = sorted(images_dir.glob("seo-img-*.png"))
            if pngs:
                st.markdown(f"**생성된 이미지: {len(pngs)}장**")
                cols = st.columns(min(len(pngs), 4))
                for i, png in enumerate(pngs):
                    with cols[i % 4]:
                        st.image(str(png), caption=png.stem, use_container_width=True)

        # 최종 HTML 다운로드
        html_files = list(final_dir.glob("*.html")) if final_dir.exists() else []
        if html_files:
            html_path = html_files[0]
            st.divider()
            st.success(f"최종 파일: `{html_path.name}`")
            html_content = html_path.read_text(encoding="utf-8")
            st.download_button(
                label="📥 HTML 다운로드",
                data=html_content,
                file_name=html_path.name,
                mime="text/html",
                use_container_width=True,
            )
        elif not validation_json.exists():
            st.info("사이드바에서 정보를 입력하고 '원스톱 생성' 버튼을 클릭하세요.")

        # 추천 태그
        if analysis_json.exists():
            try:
                analysis_data = json.loads(analysis_json.read_text(encoding="utf-8"))
                avg_data = analysis_data.get("averages", {})
                rec_tags = avg_data.get("recommended_tags", [])
                tag_freq = avg_data.get("tag_frequency", {})

                if rec_tags or tag_freq:
                    st.divider()
                    st.markdown("**추천 태그**")
                    st.caption("상위글에서 2회 이상 사용된 태그 (빈도순)")

                    if rec_tags:
                        # 태그 칩 표시 (외부 크롤링 데이터 escape)
                        chips_html = " ".join(
                            f'<span class="tag-chip">#{html_lib.escape(t)}</span>'
                            for t in rec_tags
                        )
                        st.markdown(chips_html, unsafe_allow_html=True)

                        # 복사용 텍스트
                        copy_text = ", ".join(rec_tags)
                        st.code(copy_text, language=None)

                    if tag_freq:
                        with st.expander("전체 태그 빈도"):
                            for tag, cnt in tag_freq.items():
                                bar_width = min(int(cnt) * 20, 100)
                                safe_tag = html_lib.escape(str(tag))
                                st.markdown(
                                    f'<div class="tag-freq-row">'
                                    f'<span class="tag-freq-name">#{safe_tag}</span>'
                                    f'<div class="tag-freq-bar" style="width:{bar_width}px;"></div>'
                                    f'<span class="tag-freq-count">{int(cnt)}회</span>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )
            except (json.JSONDecodeError, KeyError):
                pass

        # 원고 수정
        if seo_content_path.exists():
            with st.expander("📝 원고 보기 / 수정"):
                existing_content = seo_content_path.read_text(encoding="utf-8")
                edited = st.text_area("SEO 원고", value=existing_content, height=400, key="seo_editor")
                if st.button("💾 수정 저장", use_container_width=True):
                    seo_content_path.write_text(edited, encoding="utf-8")
                    st.success("저장 완료")
                    st.rerun()

    # ── 개별 실행 탭 ──
    with tab_steps:
        st.caption("개별 Step을 수동으로 실행할 수 있습니다.")

        # Step 1
        st.markdown("#### Step 1. 상위글 크롤링 + 분석")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 상위글 수집", use_container_width=True, key="manual_fetch"):
                analysis_dir.mkdir(parents=True, exist_ok=True)
                with st.spinner(f"'{keyword}' 상위 {blog_count}개 크롤링 중..."):
                    r = run_script("fetch_competitors.py", [
                        "--keyword", keyword, "--output-dir", str(analysis_dir), "--count", str(blog_count),
                    ])
                st.success("완료") if r.returncode == 0 else st.error("실패")
        with c2:
            if st.button("📊 패턴 분석", use_container_width=True, key="manual_analyze",
                          disabled=not competitor_pages.exists()):
                with st.spinner("분석 중..."):
                    r = run_script("analyze_competitors.py", [
                        "--input", str(competitor_pages), "--keyword", keyword, "--output-dir", str(analysis_dir),
                    ])
                st.success("완료") if r.returncode == 0 else st.error("실패")

        if analysis_summary_path.exists():
            with st.expander("📈 분석 결과"):
                st.markdown(analysis_summary_path.read_text(encoding="utf-8"))

        st.divider()

        # Step 2
        st.markdown("#### Step 2. SEO 원고 생성")
        if st.button("✨ AI 원고 작성", use_container_width=True, key="manual_seo",
                      disabled=not analysis_json.exists()):
            content_dir.mkdir(parents=True, exist_ok=True)
            with st.spinner("Claude 원고 작성 중..."):
                r = run_script("generate_seo_content.py", [
                    "--keyword", keyword, "--analysis", str(analysis_json), "--output-dir", str(content_dir),
                ], timeout=600)
            if r.returncode == 0:
                st.success("완료")
                st.rerun()
            else:
                st.error("실패")
                st.code(r.stderr[-500:] if r.stderr else r.stdout[-500:] if r.stdout else "")

        st.divider()

        # Step 3: 브랜드 이미지
        st.markdown("#### Step 3. 브랜드 섹션 이미지")
        c5, c6 = st.columns(2)
        with c5:
            if st.button("✨ 브랜드 HTML 생성", use_container_width=True, key="manual_brand_html"):
                branded_html_dir = out_dir / "branded" / "html"
                branded_html_dir.mkdir(parents=True, exist_ok=True)
                gen_args = ["--keyword", keyword, "--brand-name", brand_name, "--output-dir", str(branded_html_dir)]
                if homepage_url:
                    gen_args += ["--homepage", homepage_url]
                if brand_manuscript:
                    gen_args += ["--manuscript", brand_manuscript]
                with st.spinner("Claude 브랜드 HTML 생성 중..."):
                    r = run_script("generate_brand_html.py", gen_args, timeout=1800)
                if r.returncode == 0:
                    st.success("완료")
                else:
                    st.error("브랜드 HTML 생성 실패")
                    error_detail = ""
                    if r.stdout:
                        error_detail += f"STDOUT:\n{r.stdout[-500:]}\n"
                    if r.stderr:
                        error_detail += f"STDERR:\n{r.stderr[-500:]}"
                    if error_detail:
                        st.code(error_detail[:1000])
        with c6:
            branded_html_dir = out_dir / "branded" / "html"
            has_brand_html = branded_html_dir.exists() and any(branded_html_dir.glob("*.html"))
            if st.button("🖼️ PNG 렌더링", use_container_width=True, key="manual_brand_png",
                          disabled=not has_brand_html):
                branded_dir.mkdir(parents=True, exist_ok=True)
                with st.spinner("HTML → PNG 변환 중..."):
                    r = run_script("render_chrome.py", [str(branded_html_dir), str(branded_dir), "--width", "680"])
                if r.returncode == 0:
                    st.success("완료")
                else:
                    st.error("실패")
                    st.code(r.stderr[-300:] if r.stderr else "")

        st.divider()

        # Step 4
        st.markdown("#### Step 4. SEO 이미지 생성")
        c3a, c3b, c4 = st.columns(3)
        with c3a:
            if st.button("📍 이미지 배치", use_container_width=True, key="manual_markers",
                          disabled=not seo_content_path.exists()):
                img_marker_args = [
                    "--seo-content", str(seo_content_path), "--keyword", keyword,
                ]
                if analysis_json.exists():
                    img_marker_args += ["--analysis", str(analysis_json)]
                with st.spinner("Claude 이미지 배치 중..."):
                    r = run_script("insert_image_markers.py", img_marker_args, timeout=600)
                if r.returncode == 0:
                    st.success("완료")
                    st.rerun()
                else:
                    st.error("실패")
                    st.code(r.stderr[-500:] if r.stderr else r.stdout[-500:] if r.stdout else "")
        with c3b:
            if st.button("🎨 프롬프트 생성", use_container_width=True, key="manual_prompt",
                          disabled=not seo_content_path.exists()):
                images_dir.mkdir(parents=True, exist_ok=True)
                with st.spinner("생성 중..."):
                    r = run_script("build_prompts.py", [
                        "--seo-content", str(seo_content_path), "--output-dir", str(images_dir),
                    ])
                st.success("완료") if r.returncode == 0 else st.error("실패")
        with c4:
            if st.button("🖼️ Gemini 이미지", use_container_width=True, key="manual_images",
                          disabled=not prompts_json.exists()):
                with st.spinner("이미지 생성 중..."):
                    r = run_script("generate_images.py", [
                        "--prompts-file", str(prompts_json), "--output-dir", str(images_dir),
                    ])
                st.code(r.stdout or r.stderr, language="text")

        st.divider()

        # Step 5
        st.markdown("#### Step 5. SEO 최종 검증")
        if st.button("✅ SEO 검증", use_container_width=True, key="manual_validate",
                      disabled=not seo_content_path.exists()):
            args = ["--content", str(seo_content_path), "--keyword", keyword]
            if analysis_json.exists():
                args += ["--analysis", str(analysis_json)]
            with st.spinner("검증 중..."):
                r = run_script("validate_seo.py", args)
            st.code(r.stdout or r.stderr, language="text")

        st.divider()

        # Step 6
        st.markdown("#### Step 6. 최종 HTML 생성")
        if st.button("📄 최종 HTML", use_container_width=True, type="primary", key="manual_compose",
                      disabled=not seo_content_path.exists()):
            final_dir.mkdir(parents=True, exist_ok=True)
            args = ["--seo-content", str(seo_content_path), "--output-dir", str(final_dir),
                     "--brand-name", brand_name, "--keyword", keyword]
            has_branded = branded_dir.exists() and any(branded_dir.glob("*.png"))
            if has_branded:
                args += ["--branded-dir", str(branded_dir)]
            if images_dir.exists():
                args += ["--seo-images-dir", str(images_dir)]
            with st.spinner("조합 중..."):
                r = run_script("compose_final.py", args)
            if r.returncode == 0:
                st.success("완료!")
                st.rerun()
            else:
                st.error("실패")
                st.code(r.stderr[-500:] if r.stderr else "")


    # ── 미리보기 탭 ──
    with tab_preview:
        html_files = list(final_dir.glob("*.html")) if final_dir.exists() else []

        if html_files:
            html_path = html_files[0]
            html_content = html_path.read_text(encoding="utf-8")

            st.markdown(f"**{html_path.name}**")
            st.components.v1.html(html_content, height=2000, scrolling=True)
        else:
            st.info("아직 생성된 게시물이 없습니다. '원스톱 생성' 버튼을 클릭하세요.")
