"""
블로그 이미지 렌더링 스크립트 (Selenium + 자동 크롭)

Usage:
  python render_chrome.py <input_dir> <output_dir> [--width 680] [--padding 20]

- Selenium + Chrome headless로 HTML → PNG 변환
- 콘텐츠 실제 높이를 측정하여 정확한 크기로 캡처
- 하단 빈 여백 없는 딱 맞는 이미지 생성
"""

import sys
import os
import glob
import argparse
from pathlib import Path
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def create_driver(width=680):
    """Chrome headless 드라이버 생성"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--window-size={width},5000")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--force-device-scale-factor=1")
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"ERROR: Chrome 드라이버 생성 실패: {e}")
        print("  → Chrome 브라우저와 chromedriver가 설치되어 있는지 확인하세요.")
        print("  → pip install webdriver-manager 로 자동 관리할 수도 있습니다.")
        sys.exit(1)
    return driver


def render_html_to_png(driver, html_path, output_path, width=680, padding=20):
    """HTML 파일을 콘텐츠 높이에 맞춰 PNG로 변환"""
    file_url = Path(html_path).resolve().as_uri()
    driver.get(file_url)

    # 메인 요소 캡처 (여러 셀렉터 시도 후 body fallback)
    main_el = None
    for selector in ["body > div", "body > section", "body > main"]:
        try:
            main_el = driver.find_element(By.CSS_SELECTOR, selector)
            break
        except Exception:
            continue
    if main_el is None:
        main_el = driver.find_element(By.TAG_NAME, "body")

    main_el.screenshot(output_path)

    img = Image.open(output_path)
    return img.size[1]


def main():
    parser = argparse.ArgumentParser(description="블로그 이미지 렌더링")
    parser.add_argument("input_dir", help="HTML 파일 디렉토리 (예: output/ilsan/html)")
    parser.add_argument("output_dir", help="PNG 출력 디렉토리 (예: output/ilsan/png)")
    parser.add_argument("--width", type=int, default=680, help="이미지 너비 (기본: 680)")
    parser.add_argument("--padding", type=int, default=20, help="하단 패딩 (기본: 20)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    html_files = sorted(glob.glob(os.path.join(args.input_dir, "*.html")))
    if not html_files:
        print("HTML 파일이 없습니다.")
        sys.exit(1)

    print("=" * 50)
    print("  블로그 이미지 렌더링 (Selenium + 자동 크롭)")
    print("=" * 50)
    print(f"입력: {args.input_dir}")
    print(f"출력: {args.output_dir}")
    print(f"너비: {args.width}px / 패딩: {args.padding}px")
    print("-" * 50)

    driver = create_driver(args.width)
    success = 0
    failed = 0

    try:
        for html_file in html_files:
            name = Path(html_file).stem
            output_path = os.path.join(args.output_dir, f"{name}.png")

            print(f"[{success + failed + 1}] {name} ... ", end="", flush=True)

            try:
                height = render_html_to_png(
                    driver, html_file, output_path, args.width, args.padding
                )
                size_kb = os.path.getsize(output_path) / 1024
                print(f"OK ({args.width}x{height}, {size_kb:.0f}KB)")
                success += 1
            except Exception as e:
                print(f"FAIL: {e}")
                failed += 1
    finally:
        driver.quit()

    print("-" * 50)
    print(f"완료: {success}/{success + failed} 성공")
    if failed:
        print(f"실패: {failed}개")
    print(f"출력: {args.output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
