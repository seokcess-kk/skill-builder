#!/bin/bash
# 다이트한의원 블로그 이미지 렌더링 스크립트
# Usage: bash render.sh <input_dir> <output_dir> [width]
#
# input_dir:  HTML 파일이 있는 디렉토리
# output_dir: PNG 파일이 저장될 디렉토리
# width:      이미지 너비 (기본값: 680)

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-./output}"
WIDTH="${3:-680}"

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 카운터
total=0
success=0
failed=0

echo "============================================"
echo "  다이트한의원 블로그 이미지 렌더링"
echo "============================================"
echo "입력: $INPUT_DIR"
echo "출력: $OUTPUT_DIR"
echo "너비: ${WIDTH}px"
echo "--------------------------------------------"

# HTML 파일 순서대로 처리
for html_file in "$INPUT_DIR"/*.html; do
  [ -f "$html_file" ] || continue
  
  total=$((total + 1))
  filename=$(basename "$html_file" .html)
  output_file="$OUTPUT_DIR/${filename}.png"
  
  echo -n "[$total] $filename ... "
  
  # wkhtmltoimage로 변환
  result=$(wkhtmltoimage \
    --width "$WIDTH" \
    --quality 95 \
    --enable-local-file-access \
    --encoding utf-8 \
    "$html_file" \
    "$output_file" 2>&1)
  
  if [ -f "$output_file" ]; then
    filesize=$(ls -lh "$output_file" | awk '{print $5}')
    dimensions=$(identify "$output_file" 2>/dev/null | awk '{print $3}' || echo "unknown")
    echo "✓ ($filesize, $dimensions)"
    success=$((success + 1))
  else
    echo "✗ FAILED"
    echo "  Error: $result"
    failed=$((failed + 1))
  fi
done

echo "--------------------------------------------"
echo "완료: $success/$total 성공"
[ $failed -gt 0 ] && echo "실패: $failed개 파일"
echo "출력 위치: $OUTPUT_DIR"
echo "============================================"
