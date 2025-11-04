#!/usr/bin/env python3
"""
Dooray API 문서에서 목차를 추출하는 스크립트

사용법:
    python3 extract_toc.py [--level LEVEL] [--file FILE]

옵션:
    --level LEVEL   표시할 헤더 레벨 (1-4, 기본값: 3)
    --file FILE     문서 파일 경로 (기본값: docs/dooray-doc.md)
"""

import re
import sys
import argparse
from pathlib import Path


def extract_toc(file_path: str, max_level: int = 3) -> list:
    """
    마크다운 파일에서 목차를 추출합니다.

    Args:
        file_path: 마크다운 파일 경로
        max_level: 추출할 최대 헤더 레벨

    Returns:
        (level, title, line_number) 튜플의 리스트
    """
    toc = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # 마크다운 헤더 매칭
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()

                if level <= max_level:
                    toc.append((level, title, line_num))

    return toc


def format_toc(toc: list, show_line_numbers: bool = True) -> str:
    """
    목차를 포맷팅된 문자열로 변환합니다.

    Args:
        toc: (level, title, line_number) 튜플의 리스트
        show_line_numbers: 라인 번호 표시 여부

    Returns:
        포맷팅된 목차 문자열
    """
    lines = []
    lines.append("=" * 80)
    lines.append("Dooray API 문서 목차")
    lines.append("=" * 80)
    lines.append("")

    for level, title, line_num in toc:
        indent = "  " * (level - 1)
        marker = "•" if level > 1 else "▶"

        if show_line_numbers:
            lines.append(f"{indent}{marker} {title} (Line {line_num})")
        else:
            lines.append(f"{indent}{marker} {title}")

    lines.append("")
    lines.append(f"총 {len(toc)}개 항목")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Dooray API 문서에서 목차를 추출합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--level',
        type=int,
        default=3,
        choices=[1, 2, 3, 4, 5, 6],
        help='표시할 최대 헤더 레벨 (기본값: 3)'
    )

    parser.add_argument(
        '--file',
        type=str,
        default='references/dooray-doc.md',
        help='문서 파일 경로 (기본값: references/dooray-doc.md)'
    )

    parser.add_argument(
        '--no-line-numbers',
        action='store_true',
        help='라인 번호를 표시하지 않음'
    )

    args = parser.parse_args()

    # 파일 경로 확인
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_path}", file=sys.stderr)
        sys.exit(1)

    # 목차 추출
    toc = extract_toc(str(file_path), args.level)

    # 결과 출력
    result = format_toc(toc, show_line_numbers=not args.no_line_numbers)
    print(result)


if __name__ == '__main__':
    main()
