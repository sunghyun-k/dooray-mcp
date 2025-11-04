#!/usr/bin/env python3
"""
Dooray API 문서에서 특정 섹션을 검색하고 내용을 출력하는 스크립트

사용법:
    python3 search_section.py "검색어" [--file FILE] [--context LINES]

예시:
    python3 search_section.py "Members"
    python3 search_section.py "GET /project" --context 20
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


def find_sections(file_path: str, query: str, case_sensitive: bool = False) -> List[Tuple[int, str, int, str]]:
    """
    문서에서 쿼리와 매칭되는 섹션을 찾습니다.

    Args:
        file_path: 마크다운 파일 경로
        query: 검색어
        case_sensitive: 대소문자 구분 여부

    Returns:
        (level, title, line_number, content) 튜플의 리스트
    """
    results = []
    current_section = None
    current_content = []

    flags = 0 if case_sensitive else re.IGNORECASE

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        # 헤더 체크
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())

        if header_match:
            # 이전 섹션 저장
            if current_section:
                level, title, start_line = current_section
                content = ''.join(current_content)
                results.append((level, title, start_line, content))

            # 새 섹션 시작
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # 쿼리 매칭 체크
            if re.search(query, title, flags):
                current_section = (level, title, line_num)
                current_content = []
            else:
                current_section = None
                current_content = []
        elif current_section:
            # 현재 섹션의 내용 수집
            current_content.append(line)

    # 마지막 섹션 저장
    if current_section:
        level, title, start_line = current_section
        content = ''.join(current_content)
        results.append((level, title, start_line, content))

    return results


def extract_section_with_context(file_path: str, line_number: int, context_lines: int = 50) -> str:
    """
    특정 라인부터 컨텍스트를 포함한 섹션 내용을 추출합니다.

    Args:
        file_path: 마크다운 파일 경로
        line_number: 시작 라인 번호
        context_lines: 출력할 라인 수

    Returns:
        섹션 내용
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 섹션의 끝을 찾음 (다음 같은 레벨 또는 상위 레벨 헤더)
    start_idx = line_number - 1
    header_match = re.match(r'^(#{1,6})\s+', lines[start_idx])

    if not header_match:
        return ""

    start_level = len(header_match.group(1))
    end_idx = len(lines)

    for i in range(start_idx + 1, len(lines)):
        next_header = re.match(r'^(#{1,6})\s+', lines[i])
        if next_header and len(next_header.group(1)) <= start_level:
            end_idx = i
            break

    # context_lines 적용
    if context_lines > 0:
        end_idx = min(end_idx, start_idx + context_lines)

    return ''.join(lines[start_idx:end_idx])


def format_results(results: List[Tuple[int, str, int, str]], file_path: str, show_content: bool = True, max_content_lines: int = 30) -> str:
    """
    검색 결과를 포맷팅합니다.

    Args:
        results: 검색 결과 리스트
        file_path: 파일 경로
        show_content: 내용 표시 여부
        max_content_lines: 표시할 최대 라인 수

    Returns:
        포맷팅된 결과 문자열
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"검색 결과: {len(results)}개 섹션 발견")
    lines.append("=" * 80)
    lines.append("")

    for idx, (level, title, line_num, content) in enumerate(results, 1):
        indent = "  " * (level - 1)
        lines.append(f"{idx}. {indent}{title}")
        lines.append(f"   라인: {line_num}")
        lines.append(f"   레벨: {'#' * level}")

        if show_content:
            lines.append("")
            lines.append("   내용:")
            lines.append("   " + "-" * 76)

            content_lines = content.split('\n')[:max_content_lines]
            for content_line in content_lines:
                if content_line.strip():
                    lines.append(f"   {content_line.rstrip()}")

            total_lines = len(content.split('\n'))
            if total_lines > max_content_lines:
                omitted_lines = total_lines - max_content_lines
                lines.append(f"   ... ({omitted_lines} 라인 생략)")

            lines.append("")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Dooray API 문서에서 섹션을 검색합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'query',
        type=str,
        help='검색할 키워드 (정규표현식 지원)'
    )

    parser.add_argument(
        '--file',
        type=str,
        default='references/dooray-doc.md',
        help='문서 파일 경로 (기본값: references/dooray-doc.md)'
    )

    parser.add_argument(
        '--case-sensitive',
        action='store_true',
        help='대소문자 구분'
    )

    parser.add_argument(
        '--no-content',
        action='store_true',
        help='내용을 표시하지 않음'
    )

    parser.add_argument(
        '--max-lines',
        type=int,
        default=30,
        help='표시할 최대 내용 라인 수 (기본값: 30)'
    )

    args = parser.parse_args()

    # 파일 경로 확인
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_path}", file=sys.stderr)
        sys.exit(1)

    # 섹션 검색
    results = find_sections(
        str(file_path),
        args.query,
        args.case_sensitive
    )

    if not results:
        print(f"검색 결과가 없습니다: '{args.query}'")
        sys.exit(0)

    # 결과 출력
    output = format_results(
        results,
        str(file_path),
        show_content=not args.no_content,
        max_content_lines=args.max_lines
    )
    print(output)


if __name__ == '__main__':
    main()
