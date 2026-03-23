"""
네이버 상위글 수집 스크립트

1단계: 네이버 검색 API로 블로그 URL 수집
2단계: 각 URL의 본문을 크롤링하여 구조화

Usage:
  python fetch_competitors.py \
    --keyword "웨스턴돔다이어트" \
    --output-dir output/westerndom-diet/analysis/ \
    --count 7

환경변수:
  NAVER_CLIENT_ID: 네이버 개발자 Client ID (필수)
  NAVER_CLIENT_SECRET: 네이버 개발자 Client Secret (필수)
"""

import os
import re
import sys
import json
import time
import argparse
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup


SEARCH_API_URL = "https://openapi.naver.com/v1/search/blog.json"
HEADERS_MOBILE = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
HEADERS_PC = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def search_blogs(keyword, count, client_id, client_secret):
    """네이버 검색 API로 블로그 포스트 URL을 수집합니다."""
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {
        "query": keyword,
        "display": min(count, 100),
        "start": 1,
        "sort": "sim",  # sim: 정확도순, date: 최신순
    }

    print(f"[검색 API] '{keyword}' 검색 중...")
    resp = requests.get(SEARCH_API_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("items", []):
        title = BeautifulSoup(item["title"], "html.parser").get_text()
        description = BeautifulSoup(item["description"], "html.parser").get_text()
        link = item["link"]
        blog_url = item.get("bloggerlink", "")
        posted = item.get("postdate", "")

        results.append({
            "title": title,
            "description": description,
            "link": link,
            "blog_url": blog_url,
            "postdate": posted,
        })

    print(f"  → {len(results)}개 블로그 포스트 발견")
    return results


def parse_naver_blog_url(url):
    """네이버 블로그 URL에서 blogId와 logNo를 추출합니다."""
    # blog.naver.com/blogId/logNo 형태
    match = re.search(r'blog\.naver\.com/([^/?\s]+)/(\d+)', url)
    if match:
        return match.group(1), match.group(2)

    # blog.naver.com/PostView.naver?blogId=xxx&logNo=yyy 형태
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    blog_id = qs.get("blogId", [None])[0]
    log_no = qs.get("logNo", [None])[0]
    if blog_id and log_no:
        return blog_id, log_no

    return None, None


def fetch_blog_tags(blog_id, log_no):
    """PC URL에서 태그를 별도 크롤링합니다.

    모바일 SSR에는 태그가 포함되지 않으므로 PC 버전에서 추출합니다.
    """
    pc_url = f"https://blog.naver.com/{blog_id}/{log_no}"
    try:
        resp = requests.get(pc_url, headers=HEADERS_PC, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        tags = []
        # 방법 1: tag 클래스 링크
        for tag_el in soup.find_all("a", class_=re.compile("tag")):
            t = tag_el.get_text(strip=True).lstrip("#")
            if t and len(t) < 30:
                tags.append(t)

        # 방법 2: og:tag meta (fallback)
        if not tags:
            for meta in soup.find_all("meta", property="og:tag"):
                t = meta.get("content", "").strip()
                if t:
                    tags.append(t)

        # 방법 3: script/JSON 내 태그 추출 (PC 페이지는 iframe 구조라 HTML에 태그가 없을 수 있음)
        if not tags:
            page_text = resp.text
            # "tagList":["태그1","태그2"] 패턴
            taglist_match = re.search(r'"tagList"\s*:\s*\[([^\]]*)\]', page_text)
            if taglist_match:
                tag_matches = re.findall(r'"([^"]+)"', taglist_match.group(1))
                tags.extend(t for t in tag_matches if len(t) < 30)
            # "tag":"태그" 개별 패턴 (fallback)
            if not tags:
                tag_matches = re.findall(r'"tag"\s*:\s*"([^"]+)"', page_text)
                tags.extend(t for t in tag_matches if len(t) < 30)

        return list(dict.fromkeys(tags))  # 중복 제거, 순서 유지
    except Exception:
        return []


def fetch_blog_content(url):
    """블로그 포스트 본문을 크롤링합니다.

    네이버 블로그는 iframe + SPA 구조이므로,
    모바일 PostView를 직접 요청하여 서버사이드 렌더링된 본문을 추출합니다.
    """
    blog_id, log_no = parse_naver_blog_url(url)

    if blog_id and log_no:
        # 모바일 PostView (SSR로 본문이 포함됨)
        mobile_url = (
            f"https://m.blog.naver.com/PostView.naver"
            f"?blogId={blog_id}&logNo={log_no}&proxyReferer=&noTrackingCode=true"
        )
        try:
            resp = requests.get(mobile_url, headers=HEADERS_MOBILE, timeout=15, allow_redirects=True)
            resp.raise_for_status()
            result = parse_blog_html(resp.text, blog_id, log_no)
            if len(re.sub(r'\s', '', result.get("text", ""))) > 50:
                # PC URL에서 태그 별도 크롤링 (모바일 SSR에는 태그 미포함)
                tags = fetch_blog_tags(blog_id, log_no)
                if tags:
                    result["tags"] = tags
                return result
        except requests.RequestException as e:
            print(f"\n    [WARN] 모바일 크롤링 실패 ({blog_id}/{log_no}): {e}")
        except Exception as e:
            print(f"\n    [WARN] 파싱 실패 ({blog_id}/{log_no}): {e}")

    # 일반 URL (티스토리 등 다른 블로그)
    try:
        resp = requests.get(url, headers=HEADERS_MOBILE, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        return parse_generic_html(resp.text)
    except Exception as e:
        return {"error": str(e)}


def parse_blog_html(html, blog_id, log_no):
    """네이버 블로그 HTML에서 본문을 추출합니다.

    SE3(SmartEditor3) 구조 기반:
    - 텍스트: se-text-paragraph 클래스
    - 소제목: se-quotation 컴포넌트 또는 h2/h3
    - 이미지: se-image 또는 data-lazy-src/postfiles 이미지
    """
    soup = BeautifulSoup(html, "html.parser")

    # SE3 메인 컨테이너 찾기
    container = (
        soup.find("div", class_="se-main-container")
        or soup.find("div", id="postViewArea")
        or soup.find("div", class_="post_ct")
    )

    if not container:
        container = soup.find("body") or soup

    # 1. 텍스트 추출 (se-text-paragraph)
    paras = container.find_all(["p", "span"], class_=re.compile("se-text-paragraph"))
    texts = []
    seen = set()
    for p in paras:
        t = p.get_text(strip=True)
        if t and t not in seen and len(t) > 2:
            seen.add(t)
            texts.append(t)

    full_text = "\n\n".join(texts)

    # fallback: se-text-paragraph가 없으면 일반 추출
    if len(re.sub(r'\s', '', full_text)) < 100:
        full_text = container.get_text(separator="\n", strip=True)

    # 2. 소제목 추출
    headings = []

    # h2/h3 태그
    for h in container.find_all(["h2", "h3"]):
        ht = h.get_text(strip=True)
        if ht and len(ht) < 100:
            headings.append(ht)

    # SE3 인용구(se-quotation) — 네이버 블로그에서 소제목 대용으로 자주 사용
    if not headings:
        for comp in container.find_all("div", class_=re.compile("se-quotation")):
            ht = comp.get_text(strip=True)
            if ht and len(ht) < 100:
                headings.append(ht)

    # SE3 section-title
    if not headings:
        for comp in container.find_all("div", class_=re.compile("se-section-title")):
            ht = comp.get_text(strip=True)
            if ht and len(ht) < 100:
                headings.append(ht)

    # 3. 이미지 추출 (의미 있는 이미지만)
    # SE3 이미지 컴포넌트: se-image-resource 클래스
    valid_images = container.find_all("img", class_=re.compile("se-image-resource"))

    # fallback: se-image-resource가 없으면 mblogthumb URL 패턴으로 필터
    if not valid_images:
        for img in container.find_all("img"):
            src = img.get("data-lazy-src", "") or img.get("src", "")
            width = img.get("width", "")
            if width and width.isdigit() and int(width) < 100:
                continue
            if any(skip in src for skip in ["icon", "emoji", "1x1", "blank", "spacer"]):
                continue
            if src and ("mblogthumb" in src or "postfiles" in src or "blogpfthumb" in src
                         or "storep" in src):
                valid_images.append(img)

    image_alts = [img.get("alt", "") for img in valid_images]

    # 이미지 상세 정보 (유형 분류에 활용)
    image_details = []
    for img in valid_images:
        src = img.get("data-lazy-src", "") or img.get("src", "")
        alt = img.get("alt", "")
        width = img.get("width", "")
        height = img.get("height", "")

        # 주변 문맥: 이미지가 속한 SE3 컴포넌트의 이전 텍스트 컴포넌트
        context = ""
        parent_comp = img.find_parent("div", class_=re.compile("se-component"))
        if parent_comp:
            prev_comp = parent_comp.find_previous_sibling(
                "div", class_=re.compile("se-component")
            )
            if prev_comp:
                context = prev_comp.get_text(strip=True)[:100]

        image_details.append({
            "alt": alt,
            "src": src,
            "width": width,
            "height": height,
            "context": context,
        })

    return {
        "text": full_text,
        "headings": headings,
        "image_count": len(valid_images),
        "image_alts": image_alts,
        "image_details": image_details,
        "tags": [],  # 태그는 fetch_blog_tags()에서 PC URL로 별도 크롤링
    }


def parse_generic_html(html):
    """일반 블로그 HTML에서 본문을 추출합니다."""
    soup = BeautifulSoup(html, "html.parser")

    # article 또는 main 태그 우선
    content = soup.find("article") or soup.find("main") or soup.find("body")

    full_text = content.get_text(separator="\n", strip=True) if content else ""
    headings = [h.get_text(strip=True) for h in (content or soup).find_all(["h2", "h3"])]
    images = (content or soup).find_all("img")
    image_alts = [img.get("alt", "") for img in images]

    # 이미지 상세 정보
    image_details = []
    for img in images:
        src = img.get("data-lazy-src", "") or img.get("src", "")
        alt = img.get("alt", "")
        width = img.get("width", "")
        height = img.get("height", "")

        # 주변 문맥: 이전 텍스트 요소 (div 제외 — 레이아웃 div 오매칭 방지)
        context = ""
        prev = img.find_previous(["p", "h2", "h3", "figcaption", "span"])
        if prev:
            prev_text = prev.get_text(strip=True)
            if len(prev_text) >= 5:  # 의미 있는 텍스트만
                context = prev_text[:100]

        image_details.append({
            "alt": alt,
            "src": src,
            "width": width,
            "height": height,
            "context": context,
        })

    return {
        "text": full_text,
        "headings": headings,
        "image_count": len(images),
        "image_alts": image_alts,
        "image_details": image_details,
        "tags": [],
    }


def main():
    parser = argparse.ArgumentParser(description="네이버 상위글 수집")
    parser.add_argument("--keyword", required=True, help="타겟 키워드")
    parser.add_argument("--output-dir", required=True, help="출력 디렉토리")
    parser.add_argument("--count", type=int, default=7, help="수집할 블로그 수 (기본: 7)")
    args = parser.parse_args()

    # API 키 확인
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("ERROR: 네이버 API 키가 필요합니다.")
        print("  환경변수 설정:")
        print("    set NAVER_CLIENT_ID=your-client-id")
        print("    set NAVER_CLIENT_SECRET=your-client-secret")
        print()
        print("  발급: https://developers.naver.com/apps/#/register")
        print("  → 검색 API 선택 → 등록")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    # Step 1: 검색 API로 URL 수집
    search_results = search_blogs(args.keyword, args.count, client_id, client_secret)
    if not search_results:
        print("검색 결과가 없습니다.")
        sys.exit(1)

    # Step 2: 각 URL 본문 크롤링
    print(f"\n[크롤링] {len(search_results)}개 포스트 본문 수집 중...")
    print("-" * 50)

    pages = []
    for i, item in enumerate(search_results):
        url = item["link"]
        title = item["title"]
        print(f"[{i+1}/{len(search_results)}] {title[:40]}... ", end="", flush=True)

        content = fetch_blog_content(url)
        if "error" in content:
            print(f"FAIL ({content['error'][:40]})")
            continue

        text_len = len(re.sub(r'\s', '', content.get("text", "")))
        img_count = content.get("image_count", 0)
        print(f"OK ({text_len}자, 이미지 {img_count}개)")

        # 본문이 너무 짧으면 스킵
        if text_len < 50:
            print(f"  → 본문 부족, 스킵")
            continue

        pages.append({
            "url": url,
            "title": title,
            "text": content.get("text", ""),
            "headings": content.get("headings", []),
            "image_count": img_count,
            "image_alts": content.get("image_alts", []),
            "image_details": content.get("image_details", []),
            "tags": content.get("tags", []),
            "postdate": item.get("postdate", ""),
        })

        # 요청 간 딜레이
        if i < len(search_results) - 1:
            time.sleep(1)

    # 저장
    output_path = os.path.join(args.output_dir, "competitor-pages.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    print("-" * 50)
    print(f"수집 완료: {len(pages)}/{len(search_results)}개 성공")
    print(f"저장: {output_path}")

    if pages:
        avg_chars = sum(len(re.sub(r'\s', '', p["text"])) for p in pages) // len(pages)
        avg_imgs = sum(p["image_count"] for p in pages) // len(pages)
        print(f"평균 글자수: {avg_chars}자, 평균 이미지: {avg_imgs}개")

    print()
    print("다음 단계:")
    print(f"  python scripts/analyze_competitors.py \\")
    print(f"    --input {output_path} \\")
    print(f"    --keyword \"{args.keyword}\" \\")
    print(f"    --output-dir {args.output_dir}")


if __name__ == "__main__":
    main()
