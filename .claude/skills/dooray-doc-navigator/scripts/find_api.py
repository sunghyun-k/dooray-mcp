#!/usr/bin/env python3
"""
Dooray API 문서에서 API 엔드포인트를 검색하는 스크립트

사용법:
    python3 find_api.py [검색어] [--method METHOD] [--file FILE]

예시:
    python3 find_api.py                          # 모든 API 목록 출력
    python3 find_api.py projects                 # "projects" 포함된 API 검색
    python3 find_api.py --method GET             # GET 메서드만 검색
    python3 find_api.py posts --method POST      # "posts" 포함된 POST API 검색
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict


def extract_apis(file_path: str) -> List[Tuple[str, str, int, str]]:
    """
    문서에서 모든 API 엔드포인트를 추출합니다.

    Args:
        file_path: 마크다운 파일 경로

    Returns:
        (method, endpoint, line_number, section_title) 튜플의 리스트
    """
    apis = []
    current_section = ""

    # API 패턴: ### GET /path/to/endpoint
    api_pattern = re.compile(r'^###\s+(GET|POST|PUT|DELETE|PATCH)\s+(/[\w\-/{}\?=&,]+)', re.IGNORECASE)

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # 섹션 제목 추적 (## 레벨)
            section_match = re.match(r'^##\s+(.+)$', line.strip())
            if section_match:
                current_section = section_match.group(1).strip()

            # API 엔드포인트 매칭
            api_match = api_pattern.match(line.strip())
            if api_match:
                method = api_match.group(1).upper()
                endpoint = api_match.group(2)
                apis.append((method, endpoint, line_num, current_section))

    return apis


def filter_apis(apis: List[Tuple[str, str, int, str]], query: str = None, method: str = None) -> List[Tuple[str, str, int, str]]:
    """
    API 목록을 필터링합니다.

    Args:
        apis: API 목록
        query: 검색어 (엔드포인트 또는 섹션에 포함)
        method: HTTP 메서드 필터

    Returns:
        필터링된 API 목록
    """
    filtered = apis

    if method:
        method = method.upper()
        filtered = [(m, e, l, s) for m, e, l, s in filtered if m == method]

    if query:
        query_lower = query.lower()
        filtered = [
            (m, e, l, s) for m, e, l, s in filtered
            if query_lower in e.lower() or query_lower in s.lower()
        ]

    return filtered


def group_by_section(apis: List[Tuple[str, str, int, str]]) -> Dict[str, List[Tuple[str, str, int]]]:
    """
    API를 섹션별로 그룹화합니다.

    Args:
        apis: API 목록

    Returns:
        섹션별로 그룹화된 API 딕셔너리
    """
    grouped = {}

    for method, endpoint, line_num, section in apis:
        if section not in grouped:
            grouped[section] = []
        grouped[section].append((method, endpoint, line_num))

    return grouped


def format_api_list(apis: List[Tuple[str, str, int, str]], group_by_sec: bool = True) -> str:
    """
    API 목록을 포맷팅합니다.

    Args:
        apis: API 목록
        group_by_sec: 섹션별로 그룹화 여부

    Returns:
        포맷팅된 문자열
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"Dooray API 엔드포인트 목록 (총 {len(apis)}개)")
    lines.append("=" * 80)
    lines.append("")

    if group_by_sec:
        # 섹션별로 그룹화
        grouped = group_by_section(apis)

        for section in sorted(grouped.keys()):
            lines.append(f"## {section}")
            lines.append("")

            for method, endpoint, line_num in sorted(grouped[section], key=lambda x: (x[1], x[0])):
                method_color = {
                    'GET': '🔵',
                    'POST': '🟢',
                    'PUT': '🟡',
                    'DELETE': '🔴',
                    'PATCH': '🟣'
                }.get(method, '⚪')

                lines.append(f"  {method_color} {method:6s} {endpoint:50s} (Line {line_num})")

            lines.append("")
    else:
        # 메서드별로 정렬
        for method, endpoint, line_num, section in sorted(apis, key=lambda x: (x[0], x[1])):
            method_color = {
                'GET': '🔵',
                'POST': '🟢',
                'PUT': '🟡',
                'DELETE': '🔴',
                'PATCH': '🟣'
            }.get(method, '⚪')

            lines.append(f"{method_color} {method:6s} {endpoint:50s} [{section}] (Line {line_num})")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def format_api_summary(apis: List[Tuple[str, str, int, str]]) -> str:
    """
    API 통계 정보를 생성합니다.

    Args:
        apis: API 목록

    Returns:
        통계 문자열
    """
    method_counts = {}
    for method, _, _, _ in apis:
        method_counts[method] = method_counts.get(method, 0) + 1

    lines = []
    lines.append("=" * 80)
    lines.append("API 통계")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"총 API 수: {len(apis)}")
    lines.append("")
    lines.append("메서드별 분포:")

    for method in sorted(method_counts.keys()):
        count = method_counts[method]
        bar = "█" * (count // 2)
        lines.append(f"  {method:6s}: {count:3d} {bar}")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Dooray API 문서에서 API 엔드포인트를 검색합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'query',
        type=str,
        nargs='?',
        help='검색할 키워드 (엔드포인트 또는 섹션명)'
    )

    parser.add_argument(
        '--method',
        type=str,
        choices=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'get', 'post', 'put', 'delete', 'patch'],
        help='HTTP 메서드 필터'
    )

    parser.add_argument(
        '--file',
        type=str,
        default='references/dooray-doc.md',
        help='문서 파일 경로 (기본값: references/dooray-doc.md)'
    )

    parser.add_argument(
        '--no-group',
        action='store_true',
        help='섹션별로 그룹화하지 않음'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='통계 정보만 표시'
    )

    args = parser.parse_args()

    # 파일 경로 확인
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 오류: 파일을 찾을 수 없습니다: {file_path}", file=sys.stderr)
        sys.exit(1)

    # API 추출
    apis = extract_apis(str(file_path))

    # 필터링
    filtered_apis = filter_apis(apis, args.query, args.method)

    if not filtered_apis:
        print(f"검색 결과가 없습니다.")
        sys.exit(0)

    # 결과 출력
    if args.summary:
        print(format_api_summary(filtered_apis))
    else:
        print(format_api_list(filtered_apis, group_by_sec=not args.no_group))


if __name__ == '__main__':
    main()
