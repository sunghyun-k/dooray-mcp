"""유틸리티 함수."""

import re
import urllib.parse
from typing import Optional, Tuple

from .client import DoorayClient, DoorayAPIError


def parse_dooray_url(url: str) -> Optional[Tuple[Optional[str], Optional[str]]]:
    """Dooray 웹 URL 파싱.

    Dooray 웹 UI URL에서 프로젝트 정보와 업무 정보를 추출합니다.

    파싱 규칙:
    1. projects/ 경로 뒤에는 항상 <project-code>/<task-number> 형식
    2. URL 경로의 마지막 부분이 숫자면 task-id 또는 task-number
    3. task/ 바로 다음 19자리 숫자는 project-id

    Args:
        url: Dooray 웹 URL
            예: "https://company.dooray.com/task/1234567890123456789/9876543210987654321"
            또는: "https://company.dooray.com/popup/project/projects/개발팀-업무/123"

    Returns:
        (프로젝트_ID, 업무_ID) 튜플 또는 (프로젝트_코드, 업무_번호) 튜플 또는 None (파싱 실패 시)
        - ID 형식: ('1234567890123456789', '9876543210987654321')
        - 코드/번호 형식: ('개발팀-업무', '123')
        - 업무 ID만: (None, '9876543210987654321')
    """
    # URL 디코딩 (한글 프로젝트명 처리)
    decoded_url = urllib.parse.unquote(url)

    # URL에서 dooray.com 이후 경로 추출
    path_match = re.search(r'dooray\.com(/[^?#]*)', decoded_url)
    if not path_match:
        return None

    path = path_match.group(1)

    # 경로를 슬래시로 분할
    parts = [p for p in path.split('/') if p]  # 빈 문자열 제거

    if not parts:
        return None

    # 19자리 숫자 ID 패턴 (Dooray task/project ID)
    id_pattern = r'^\d{19}$'
    # 일반 숫자 패턴
    number_pattern = r'^\d+$'

    # 규칙 1: projects/ 경로가 있는 경우
    # projects/<project-code>/<task-number> 형식
    for i, part in enumerate(parts):
        if part == 'projects' and i + 2 < len(parts):
            project_code = parts[i + 1]
            task_number = parts[i + 2]
            # task_number가 숫자인지 확인
            if re.match(number_pattern, task_number):
                return project_code, task_number

    # 규칙 2 & 3: 마지막이 숫자인 경우
    last_part = parts[-1]
    if re.match(number_pattern, last_part):
        # 19자리 ID인 경우
        if re.match(id_pattern, last_part):
            task_id = last_part

            # task/ 바로 다음에 19자리 숫자가 있는지 확인 (규칙 3)
            for i, part in enumerate(parts):
                if part == 'task' and i + 1 < len(parts):
                    next_part = parts[i + 1]
                    if re.match(id_pattern, next_part):
                        # task/<project-id>/<task-id> 형식
                        return next_part, task_id

            # 다른 위치에서 19자리 숫자 찾기
            for i in range(len(parts) - 2, -1, -1):
                if re.match(id_pattern, parts[i]):
                    # 두 개의 19자리 ID가 있는 경우
                    return parts[i], task_id

            # task ID만 있는 경우
            return None, task_id

    # 파싱 실패
    return None


def find_project_by_code(
    client: DoorayClient,
    code: str,
) -> Optional[str]:
    """프로젝트 코드로 프로젝트 ID 찾기.

    Args:
        client: DoorayClient 인스턴스
        code: 프로젝트 코드

    Returns:
        프로젝트 ID 또는 None

    Raises:
        DoorayAPIError: API 오류 발생 시
    """
    # member=me 옵션으로 내가 속한 프로젝트만 조회
    for page in range(20):  # 최대 2000개 프로젝트 검색
        result = client.list_projects(member="me", page=page, size=100)
        projects = result.get('result', [])

        if not projects:
            break

        for proj in projects:
            proj_code = proj.get('code', '')
            proj_id = proj.get('id', '')

            # 정확히 일치
            if proj_code == code:
                return proj_id

            # 부분 일치 (대소문자 무시)
            if code.lower() in proj_code.lower():
                return proj_id

    return None


def get_post_by_number(
    client: DoorayClient,
    project_id: str,
    post_number: int,
) -> Optional[str]:
    """업무 번호로 업무 ID 찾기.

    Args:
        client: DoorayClient 인스턴스
        project_id: 프로젝트 ID
        post_number: 업무 번호

    Returns:
        업무 ID 또는 None

    Raises:
        DoorayAPIError: API 오류 발생 시
    """
    result = client.list_posts(
        project_id=project_id,
        post_number=post_number,
        size=1,
    )
    posts = result.get('result', [])

    if posts:
        return posts[0].get('id')

    return None
