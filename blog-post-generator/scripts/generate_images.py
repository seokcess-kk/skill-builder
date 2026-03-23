"""
Gemini 이미지 생성 스크립트

Usage:
  python generate_images.py --prompts-file prompts.json --output-dir ./images/

환경변수:
  GOOGLE_API_KEY: Gemini API 키 (필수)
"""

import os
import sys
import io
import json
import time
import argparse
from pathlib import Path


def generate_images(prompts_file, output_dir, delay=3):
    """prompts.json의 각 항목에 대해 Gemini 이미지를 생성합니다."""
    try:
        from google import genai
        from google.genai import types
        from PIL import Image
    except ImportError:
        print("ERROR: 필요 패키지가 없습니다.")
        print("  pip install google-genai Pillow")
        sys.exit(1)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        print("  set GOOGLE_API_KEY=your-api-key")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    os.makedirs(output_dir, exist_ok=True)

    with open(prompts_file, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    model_name = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

    # negative_prompt 지원 여부를 사전 판별
    no_text_negative = (
        "text, words, letters, numbers, labels, captions, watermarks, "
        "signatures, typography, writing, Korean characters, English characters, "
        "fonts, titles, subtitles, headings, annotations"
    )
    use_negative_prompt = True
    try:
        types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            negative_prompt=no_text_negative,
        )
    except (TypeError, ValueError):
        use_negative_prompt = False

    # ImageConfig(aspect_ratio) 지원 여부를 사전 판별
    use_image_config = hasattr(types, "ImageConfig")
    if use_image_config:
        try:
            types.ImageConfig(aspect_ratio="4:3")
        except (TypeError, ValueError):
            use_image_config = False

    print("=" * 50)
    print("  Gemini 이미지 생성")
    print("=" * 50)
    print(f"모델: {model_name}")
    print(f"negative_prompt: {'활성' if use_negative_prompt else '미지원 — 프롬프트 지시에 의존'}")
    print(f"aspect_ratio: {'ImageConfig' if use_image_config else '프롬프트 텍스트 방식'}")
    print(f"생성 대상: {len(prompts)}개 이미지")
    print(f"출력: {output_dir}")
    print("-" * 50)

    success = 0
    failed = 0
    results = []

    for i, item in enumerate(prompts):
        img_id = item.get("id", f"img-{i+1:02d}")
        img_type = item.get("type", "unknown")
        prompt = item["prompt"]
        filename = item.get("filename", f"{img_id}.png")
        output_path = os.path.join(output_dir, filename)

        aspect_label = item.get("aspect_ratio", "default")
        print(f"[{i+1}/{len(prompts)}] {img_id} ({img_type}, {aspect_label}) ... ", end="", flush=True)

        try:
            aspect_ratio = item.get("aspect_ratio")

            config_kwargs = {
                "response_modalities": ["IMAGE"],
            }
            # ImageConfig 지원 시 aspect_ratio를 API 파라미터로 전달
            if aspect_ratio and use_image_config:
                config_kwargs["image_config"] = types.ImageConfig(aspect_ratio=aspect_ratio)
            if use_negative_prompt:
                config_kwargs["negative_prompt"] = no_text_negative

            # ImageConfig 미지원 시 프롬프트 텍스트에 aspect ratio 지시 추가
            effective_prompt = prompt
            if aspect_ratio and not use_image_config:
                ratio_desc = {
                    "1:1": "square (1:1)",
                    "4:3": "landscape 4:3",
                    "3:4": "portrait 3:4",
                    "16:9": "wide landscape 16:9",
                    "9:16": "tall portrait 9:16",
                }.get(aspect_ratio, aspect_ratio)
                effective_prompt = f"Generate this image in {ratio_desc} aspect ratio. {prompt}"

            response = client.models.generate_content(
                model=model_name,
                contents=[effective_prompt],
                config=types.GenerateContentConfig(**config_kwargs),
            )

            saved = False
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data is not None:
                        img = Image.open(io.BytesIO(part.inline_data.data))
                        img.save(output_path)
                        size_kb = os.path.getsize(output_path) / 1024
                        print(f"OK ({size_kb:.0f}KB, {img.size[0]}x{img.size[1]})")
                        saved = True
                        success += 1
                        results.append({
                            "id": img_id,
                            "type": img_type,
                            "filename": filename,
                            "status": "success",
                            "size_kb": round(size_kb),
                            "resolution": f"{img.size[0]}x{img.size[1]}",
                        })
                        break
                if saved:
                    break

            if not saved:
                print("FAIL (이미지 없음 - 안전 필터 차단 가능)")
                failed += 1
                results.append({
                    "id": img_id,
                    "type": img_type,
                    "filename": filename,
                    "status": "blocked",
                })

        except Exception as e:
            print(f"FAIL ({str(e)[:80]})")
            failed += 1
            results.append({
                "id": img_id,
                "type": img_type,
                "filename": filename,
                "status": "error",
                "error": str(e)[:200],
            })

        # API 속도 제한 대응
        if i < len(prompts) - 1:
            time.sleep(delay)

    # 결과 요약 저장
    results_path = os.path.join(output_dir, "generation-results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": model_name,
            "total": len(prompts),
            "success": success,
            "failed": failed,
            "images": results,
        }, f, ensure_ascii=False, indent=2)

    print("-" * 50)
    print(f"완료: {success}/{len(prompts)} 성공")
    if failed:
        print(f"실패: {failed}개")
    print(f"결과: {results_path}")
    print("=" * 50)

    return success, failed


def main():
    parser = argparse.ArgumentParser(description="Gemini 이미지 생성")
    parser.add_argument("--prompts-file", required=True, help="프롬프트 JSON 파일")
    parser.add_argument("--output-dir", required=True, help="이미지 출력 디렉토리")
    parser.add_argument("--delay", type=int, default=3, help="요청 간 딜레이 초 (기본: 3)")
    args = parser.parse_args()

    generate_images(args.prompts_file, args.output_dir, args.delay)


if __name__ == "__main__":
    main()
