"""Dooray Task Management MCP Server."""

import os
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from .client import DoorayClient, DoorayAPIError
from .utils import (
    parse_dooray_url,
    find_project_by_code,
    get_post_by_number,
)


# FastMCP 서버 초기화
mcp = FastMCP("Dooray Task Management")

# 전역 클라이언트 인스턴스
_client: Optional[DoorayClient] = None


def get_client() -> DoorayClient:
    """DoorayClient 인스턴스 가져오기 (싱글톤)."""
    global _client
    if _client is None:
        _client = DoorayClient()
    return _client


def resolve_task_identifiers(
    task_id: Optional[str] = None,
    project_code: Optional[str] = None,
    task_number: Optional[int] = None,
    url: Optional[str] = None,
) -> tuple[str, str]:
    """업무 식별자를 (project_id, post_id)로 변환.

    Args:
        task_id: 업무 ID
        project_code: 프로젝트 코드
        task_number: 업무 번호
        url: Dooray 웹 URL

    Returns:
        (project_id, post_id) 튜플

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    client = get_client()

    # URL이 제공된 경우
    if url:
        parsed = parse_dooray_url(url)
        if not parsed:
            raise ValueError("유효하지 않은 Dooray URL 형식입니다.")

        first_param, second_param = parsed

        # 업무 ID만 있는 경우
        if not first_param and second_param:
            post_id = second_param
            # 프로젝트 ID를 얻기 위해 업무 조회
            result = client.get_post(post_id)
            project_id = result.get('result', {}).get('project', {}).get('id')
            if not project_id:
                raise ValueError("업무에서 프로젝트 ID를 찾을 수 없습니다.")
            return project_id, post_id

        if not first_param or not second_param:
            raise ValueError("URL에서 프로젝트 정보 또는 업무 정보를 찾을 수 없습니다.")

        # 첫 번째 파라미터가 숫자(ID)인지 문자열(코드)인지 확인
        if first_param.isdigit():
            # ID 형식
            return first_param, second_param
        else:
            # 코드/번호 형식
            project_id = find_project_by_code(client, first_param)
            if not project_id:
                raise ValueError(f"프로젝트를 찾을 수 없습니다: {first_param}")

            post_id = get_post_by_number(client, project_id, int(second_param))
            if not post_id:
                raise ValueError(f"업무를 찾을 수 없습니다: {first_param}/{second_param}")

            return project_id, post_id

    # 프로젝트 코드 + 업무 번호가 제공된 경우
    if project_code and task_number:
        project_id = find_project_by_code(client, project_code)
        if not project_id:
            raise ValueError(f"프로젝트를 찾을 수 없습니다: {project_code}")

        post_id = get_post_by_number(client, project_id, task_number)
        if not post_id:
            raise ValueError(f"업무를 찾을 수 없습니다: {project_code}/{task_number}")

        return project_id, post_id

    # 업무 ID만 제공된 경우
    if task_id:
        # 프로젝트 ID를 얻기 위해 업무 조회
        result = client.get_post(task_id)
        project_id = result.get('result', {}).get('project', {}).get('id')
        if not project_id:
            raise ValueError("업무에서 프로젝트 ID를 찾을 수 없습니다.")
        return project_id, task_id

    raise ValueError(
        "업무를 식별할 수 있는 정보를 제공해야 합니다. "
        "다음 중 하나를 제공하세요: "
        "(1) task_id, (2) project_code + task_number, (3) url"
    )


@mcp.tool()
def list_projects(
    page: int = 0,
    state: Optional[str] = None,
    scope: Optional[str] = None,
) -> Dict[str, Any]:
    """내가 속한 프로젝트 목록 조회.

    Args:
        page: 페이지 번호 (기본: 0)
        state: 프로젝트 상태 필터 ('active', 'archived')
        scope: 프로젝트 접근 범위 필터 ('private', 'public')

    Returns:
        프로젝트 목록 (ID, 코드, 설명, 상태 등)

    Raises:
        DoorayAPIError: API 오류
    """
    try:
        client = get_client()

        # 페이지당 20개 고정
        page_size = 20

        # API 호출
        params = {
            "member": "me",
            "page": page,
            "size": page_size,
        }
        if state:
            params["state"] = state
        if scope:
            params["scope"] = scope

        result = client.get("/project/v1/projects", params=params)

        # 응답에서 프로젝트 목록 추출
        projects = result.get('result', [])
        total_count = result.get('totalCount', 0)

        # 다음 페이지 존재 여부 계산
        fetched_so_far = (page + 1) * page_size
        has_more = total_count > fetched_so_far

        return {
            "totalCount": total_count,
            "page": page,
            "returnedCount": len(projects),
            "hasMore": has_more,
            "projects": projects,
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_task(
    task_id: Optional[str] = None,
    project_code: Optional[str] = None,
    task_number: Optional[int] = None,
    url: Optional[str] = None,
) -> Dict[str, Any]:
    """업무 상세 정보 조회.

    세 가지 방법으로 업무를 조회할 수 있습니다:
    1. 업무 ID만 제공 (task_id)
    2. 프로젝트 코드 + 업무 번호 (project_code, task_number)
    3. Dooray 웹 URL (url)

    Args:
        task_id: 업무 ID (예: '9876543210987654321')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        task_number: 업무 번호 (예: 306)
        url: Dooray 웹 URL (예: 'https://company.dooray.com/task/...')

    Returns:
        업무 상세 정보 (제목, 본문, 담당자, 상태, 생성일 등)

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        project_id, post_id = resolve_task_identifiers(
            task_id=task_id,
            project_code=project_code,
            task_number=task_number,
            url=url,
        )

        client = get_client()
        result = client.get_post_with_project(project_id, post_id)

        # 응답에서 업무 정보 추출
        task_data = result.get('result', {})

        # 하위 업무 목록 조회
        sub_tasks_result = client.list_posts(
            project_id=project_id,
            parent_post_id=post_id,
            page=0,
            size=100,
        )
        sub_tasks = sub_tasks_result.get('result', [])

        # 사용자 친화적인 형식으로 반환
        return {
            "id": task_data.get('id'),
            "subject": task_data.get('subject'),
            "taskNumber": task_data.get('taskNumber'),
            "project": task_data.get('project', {}),
            "body": task_data.get('body', {}),
            "closed": task_data.get('closed'),
            "workflowClass": task_data.get('workflowClass'),
            "workflow": task_data.get('workflow', {}),
            "priority": task_data.get('priority'),
            "users": task_data.get('users', {}),
            "createdAt": task_data.get('createdAt'),
            "updatedAt": task_data.get('updatedAt'),
            "dueDate": task_data.get('dueDate'),
            "milestone": task_data.get('milestone', {}),
            "tags": task_data.get('tags', []),
            "parent": task_data.get('parent', {}),
            "subTasks": sub_tasks,
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_task_comments(
    task_id: Optional[str] = None,
    project_code: Optional[str] = None,
    task_number: Optional[int] = None,
    url: Optional[str] = None,
    page: int = 0,
) -> Dict[str, Any]:
    """업무의 댓글 목록 조회.

    세 가지 방법으로 업무를 지정할 수 있습니다:
    1. 업무 ID만 제공 (task_id)
    2. 프로젝트 코드 + 업무 번호 (project_code, task_number)
    3. Dooray 웹 URL (url)

    Args:
        task_id: 업무 ID (예: '9876543210987654321')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        task_number: 업무 번호 (예: 306)
        url: Dooray 웹 URL (예: 'https://company.dooray.com/task/...')
        page: 페이지 번호 (기본: 0)

    Returns:
        댓글 목록 (작성자, 내용, 작성일시 등)

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        project_id, post_id = resolve_task_identifiers(
            task_id=task_id,
            project_code=project_code,
            task_number=task_number,
            url=url,
        )

        # 페이지당 20개 고정
        page_size = 20

        client = get_client()
        result = client.list_logs(
            project_id=project_id,
            post_id=post_id,
            page=page,
            size=page_size,
            order="createdAt",  # 오래된 순
        )

        # 응답에서 댓글 목록 추출
        logs = result.get('result', [])
        total_count = result.get('totalCount', 0)

        # 다음 페이지 존재 여부 계산
        fetched_so_far = (page + 1) * page_size
        has_more = total_count > fetched_so_far

        # 사용자 친화적인 형식으로 변환
        comments = []
        for log in logs:
            comments.append({
                "id": log.get('id'),
                "type": log.get('type'),
                "subtype": log.get('subtype'),
                "body": log.get('body', {}),
                "creator": log.get('creator', {}),
                "createdAt": log.get('createdAt'),
                "modifiedAt": log.get('modifiedAt'),
            })

        return {
            "totalCount": total_count,
            "page": page,
            "returnedCount": len(comments),
            "hasMore": has_more,
            "comments": comments,
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def create_task_comment(
    content: str,
    task_id: Optional[str] = None,
    project_code: Optional[str] = None,
    task_number: Optional[int] = None,
    url: Optional[str] = None,
    mime_type: str = "text/x-markdown",
) -> Dict[str, Any]:
    """업무에 댓글 작성.

    세 가지 방법으로 업무를 지정할 수 있습니다:
    1. 업무 ID만 제공 (task_id)
    2. 프로젝트 코드 + 업무 번호 (project_code, task_number)
    3. Dooray 웹 URL (url)

    Args:
        content: 댓글 내용 (필수)
        task_id: 업무 ID (예: '9876543210987654321')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        task_number: 업무 번호 (예: 306)
        url: Dooray 웹 URL (예: 'https://company.dooray.com/task/...')
        mime_type: 콘텐츠 타입 (기본: 'text/x-markdown', 또는 'text/html')

    Returns:
        생성된 댓글 정보 (댓글 ID 등)

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        project_id, post_id = resolve_task_identifiers(
            task_id=task_id,
            project_code=project_code,
            task_number=task_number,
            url=url,
        )

        client = get_client()
        result = client.create_log(
            project_id=project_id,
            post_id=post_id,
            content=content,
            mime_type=mime_type,
        )

        # 응답에서 생성된 댓글 ID 추출
        comment_id = result.get('result', {}).get('id')

        return {
            "success": True,
            "commentId": comment_id,
            "message": "댓글이 성공적으로 작성되었습니다.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def update_task_comment(
    comment_id: str,
    content: str,
    task_id: Optional[str] = None,
    project_code: Optional[str] = None,
    task_number: Optional[int] = None,
    url: Optional[str] = None,
    mime_type: str = "text/x-markdown",
) -> Dict[str, Any]:
    """업무 댓글 수정.

    세 가지 방법으로 업무를 지정할 수 있습니다:
    1. 업무 ID만 제공 (task_id)
    2. 프로젝트 코드 + 업무 번호 (project_code, task_number)
    3. Dooray 웹 URL (url)

    Args:
        comment_id: 댓글 ID (필수, list_task_comments로 조회 가능)
        content: 수정할 댓글 내용 (필수)
        task_id: 업무 ID (예: '9876543210987654321')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        task_number: 업무 번호 (예: 306)
        url: Dooray 웹 URL (예: 'https://company.dooray.com/task/...')
        mime_type: 콘텐츠 타입 (기본: 'text/x-markdown', 또는 'text/html')

    Returns:
        수정 결과

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        project_id, post_id = resolve_task_identifiers(
            task_id=task_id,
            project_code=project_code,
            task_number=task_number,
            url=url,
        )

        client = get_client()
        result = client.update_log(
            project_id=project_id,
            post_id=post_id,
            log_id=comment_id,
            content=content,
            mime_type=mime_type,
        )

        # 성공 여부 확인
        is_successful = result.get('header', {}).get('isSuccessful', False)

        if is_successful:
            return {
                "success": True,
                "message": "댓글이 성공적으로 수정되었습니다.",
            }
        else:
            error_message = result.get('header', {}).get('resultMessage', '알 수 없는 오류')
            return {
                "success": False,
                "error": error_message,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def create_task(
    project_id: Optional[str] = None,
    project_code: Optional[str] = None,
    subject: str = "",
    body_content: Optional[str] = None,
    body_mime_type: str = "text/x-markdown",
    users_to: Optional[list] = None,
    users_cc: Optional[list] = None,
    parent_post_id: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    milestone_id: Optional[str] = None,
    tag_ids: Optional[list] = None,
) -> Dict[str, Any]:
    """업무(Task) 생성.

    프로젝트 ID 또는 프로젝트 코드로 프로젝트를 지정할 수 있습니다.

    Args:
        project_id: 프로젝트 ID (예: '1234567890123456789')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        subject: 업무 제목 (필수)
        body_content: 업무 본문 내용
        body_mime_type: 본문 MIME 타입 ('text/x-markdown' 또는 'text/html')
        users_to: 담당자 목록 (예: [{"type": "member", "member": {"organizationMemberId": "123"}}])
        users_cc: 참조자 목록
        parent_post_id: 상위 업무 ID (하위 업무로 만들 경우)
        priority: 우선순위 ('highest', 'high', 'normal', 'low', 'lowest', 'none')
        due_date: 마감일 (ISO 8601 형식, 예: '2025-12-31T23:59:59+09:00')
        milestone_id: 마일스톤 ID
        tag_ids: 태그 ID 목록 (예: ["tag1", "tag2"])

    Returns:
        생성된 업무 정보 (업무 ID 포함)

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        # 제목 확인
        if not subject:
            raise ValueError("업무 제목(subject)은 필수입니다.")

        client = get_client()

        # 프로젝트 ID 결정
        if project_code:
            resolved_project_id = find_project_by_code(client, project_code)
            if not resolved_project_id:
                raise ValueError(f"프로젝트를 찾을 수 없습니다: {project_code}")
        elif project_id:
            resolved_project_id = project_id
        else:
            raise ValueError("project_id 또는 project_code 중 하나를 제공해야 합니다.")

        # 업무 생성
        result = client.create_post(
            project_id=resolved_project_id,
            subject=subject,
            body_content=body_content,
            body_mime_type=body_mime_type,
            users_to=users_to,
            users_cc=users_cc,
            parent_post_id=parent_post_id,
            priority=priority,
            due_date=due_date,
            milestone_id=milestone_id,
            tag_ids=tag_ids,
        )

        # 성공 여부 확인
        is_successful = result.get('header', {}).get('isSuccessful', False)

        if is_successful:
            task_id = result.get('result', {}).get('id')
            return {
                "success": True,
                "taskId": task_id,
                "message": "업무가 성공적으로 생성되었습니다.",
            }
        else:
            error_message = result.get('header', {}).get('resultMessage', '알 수 없는 오류')
            return {
                "success": False,
                "error": error_message,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def update_task(
    task_id: Optional[str] = None,
    project_code: Optional[str] = None,
    task_number: Optional[int] = None,
    url: Optional[str] = None,
    subject: Optional[str] = None,
    body_content: Optional[str] = None,
    body_mime_type: str = "text/x-markdown",
    users_to: Optional[list] = None,
    users_cc: Optional[list] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    milestone_id: Optional[str] = None,
    tag_ids: Optional[list] = None,
    version: Optional[int] = None,
) -> Dict[str, Any]:
    """업무 정보 수정.

    세 가지 방법으로 업무를 지정할 수 있습니다:
    1. 업무 ID만 제공 (task_id)
    2. 프로젝트 코드 + 업무 번호 (project_code, task_number)
    3. Dooray 웹 URL (url)

    수정하고 싶은 필드만 제공하면 됩니다 (부분 업데이트 지원).

    Args:
        task_id: 업무 ID (예: '9876543210987654321')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        task_number: 업무 번호 (예: 306)
        url: Dooray 웹 URL (예: 'https://company.dooray.com/task/...')
        subject: 업무 제목
        body_content: 업무 본문 내용
        body_mime_type: 본문 MIME 타입 ('text/x-markdown' 또는 'text/html')
        users_to: 담당자 목록 (예: [{"type": "member", "member": {"organizationMemberId": "123"}}])
        users_cc: 참조자 목록
        priority: 우선순위 ('highest', 'high', 'normal', 'low', 'lowest', 'none')
        due_date: 마감일 (ISO 8601 형식, 예: '2025-12-31T23:59:59+09:00')
        milestone_id: 마일스톤 ID
        tag_ids: 태그 ID 목록 (예: ["tag1", "tag2"])
        version: 버전 번호 (동시 수정 방지용, None이면 최신 버전 사용)

    Returns:
        업데이트 결과

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        project_id, post_id = resolve_task_identifiers(
            task_id=task_id,
            project_code=project_code,
            task_number=task_number,
            url=url,
        )

        client = get_client()
        result = client.update_post(
            project_id=project_id,
            post_id=post_id,
            subject=subject,
            body_content=body_content,
            body_mime_type=body_mime_type,
            users_to=users_to,
            users_cc=users_cc,
            priority=priority,
            due_date=due_date,
            milestone_id=milestone_id,
            tag_ids=tag_ids,
            version=version,
        )

        # 성공 여부 확인
        is_successful = result.get('header', {}).get('isSuccessful', False)

        if is_successful:
            return {
                "success": True,
                "message": "업무가 성공적으로 수정되었습니다.",
            }
        else:
            error_message = result.get('header', {}).get('resultMessage', '알 수 없는 오류')
            return {
                "success": False,
                "error": error_message,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def get_project_members(
    project_id: Optional[str] = None,
    project_code: Optional[str] = None,
) -> Dict[str, Any]:
    """프로젝트의 멤버 및 멤버 그룹 조회.

    프로젝트 ID 또는 프로젝트 코드로 프로젝트를 지정할 수 있습니다.
    멤버 목록과 멤버 그룹 목록(각 그룹의 멤버 포함)을 모두 반환합니다.

    Args:
        project_id: 프로젝트 ID (예: '1234567890123456789')
        project_code: 프로젝트 코드 (예: '개발팀-업무')

    Returns:
        프로젝트 멤버 및 멤버 그룹 정보

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        client = get_client()

        # 프로젝트 ID 결정
        if project_code:
            resolved_project_id = find_project_by_code(client, project_code)
            if not resolved_project_id:
                raise ValueError(f"프로젝트를 찾을 수 없습니다: {project_code}")
        elif project_id:
            resolved_project_id = project_id
        else:
            raise ValueError("project_id 또는 project_code 중 하나를 제공해야 합니다.")

        # 멤버 목록 조회
        members_result = client.get_project_members(
            project_id=resolved_project_id,
            page=0,
            size=100,
        )
        members = members_result.get('result', [])
        total_members = members_result.get('totalCount', 0)

        # 멤버 그룹 목록 조회
        groups_result = client.get_project_member_groups(
            project_id=resolved_project_id,
            page=0,
            size=100,
        )
        # API 응답이 이중 배열 형태 [[...]]로 오므로 첫 번째 요소 추출
        member_groups_raw = groups_result.get('result', [[]])
        member_groups = member_groups_raw[0] if member_groups_raw else []

        # 각 그룹의 상세 정보(멤버 포함) 조회
        detailed_groups = []
        for group in member_groups:
            group_id = group.get('id')
            if group_id:
                try:
                    group_detail = client.get_project_member_group(
                        project_id=resolved_project_id,
                        member_group_id=group_id,
                    )
                    detailed_groups.append(group_detail.get('result', {}))
                except Exception:
                    # 그룹 상세 조회 실패 시 기본 정보만 포함
                    detailed_groups.append(group)

        return {
            "projectId": resolved_project_id,
            "members": {
                "totalCount": total_members,
                "list": members,
            },
            "memberGroups": {
                "totalCount": len(detailed_groups),
                "list": detailed_groups,
            },
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_available_workflows(
    project_id: Optional[str] = None,
    project_code: Optional[str] = None,
) -> Dict[str, Any]:
    """프로젝트의 사용 가능한 상태 목록 조회.

    프로젝트 ID 또는 프로젝트 코드로 프로젝트를 지정할 수 있습니다.
    프로젝트에서 사용 가능한 모든 상태를 반환합니다.

    Args:
        project_id: 프로젝트 ID (예: '1234567890123456789')
        project_code: 프로젝트 코드 (예: '개발팀-업무')

    Returns:
        상태 목록 (ID, 이름, 클래스 등)

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        client = get_client()

        # 프로젝트 ID 결정
        if project_code:
            resolved_project_id = find_project_by_code(client, project_code)
            if not resolved_project_id:
                raise ValueError(f"프로젝트를 찾을 수 없습니다: {project_code}")
        elif project_id:
            resolved_project_id = project_id
        else:
            raise ValueError("project_id 또는 project_code 중 하나를 제공해야 합니다.")

        # 워크플로우(상태) 목록 조회
        result = client.get_workflows(project_id=resolved_project_id)

        # 응답에서 워크플로우 목록 추출
        workflows = result.get('result', [])
        total_count = result.get('totalCount', len(workflows))

        return {
            "projectId": resolved_project_id,
            "totalCount": total_count,
            "workflows": workflows,
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_project_tasks(
    project_id: Optional[str] = None,
    project_code: Optional[str] = None,
    from_member_ids: Optional[list] = None,
    to_member_ids: Optional[list] = None,
    cc_member_ids: Optional[list] = None,
    workflow_classes: Optional[list] = None,
    subject: Optional[str] = None,
    created_at: str = "prev-30d",
    page: int = 0,
) -> Dict[str, Any]:
    """프로젝트의 업무 목록 조회.

    프로젝트 ID 또는 프로젝트 코드로 프로젝트를 지정할 수 있습니다.

    Args:
        project_id: 프로젝트 ID (예: '1234567890123456789')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        from_member_ids: 작성자 ID 목록 (organizationMemberId)
        to_member_ids: 담당자 ID 목록 (organizationMemberId)
        cc_member_ids: 참조자 ID 목록 (organizationMemberId)
        workflow_classes: 상태 클래스 목록 (상태의 대분류, get_available_workflows로 조회 가능)
        subject: 제목 필터 (부분 일치)
        created_at: 생성일 필터 (기본: 'prev-30d'). today, thisweek, prev-{N}d, next-{N}d, ISO8601 범위 지원
        page: 페이지 번호 (기본: 0)

    Returns:
        업무 목록 (ID, 제목, 상태, 담당자 등)

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        client = get_client()

        # 프로젝트 ID 결정
        if project_code:
            resolved_project_id = find_project_by_code(client, project_code)
            if not resolved_project_id:
                raise ValueError(f"프로젝트를 찾을 수 없습니다: {project_code}")
        elif project_id:
            resolved_project_id = project_id
        else:
            raise ValueError("project_id 또는 project_code 중 하나를 제공해야 합니다.")

        # 페이지당 20개 고정
        page_size = 20

        # 업무 목록 조회 (최신순 정렬)
        result = client.list_posts(
            project_id=resolved_project_id,
            from_member_ids=from_member_ids,
            to_member_ids=to_member_ids,
            cc_member_ids=cc_member_ids,
            workflow_classes=workflow_classes,
            subjects=subject,
            created_at=created_at,
            order="-createdAt",
            page=page,
            size=page_size,
        )

        # 응답에서 업무 목록 추출
        tasks = result.get('result', [])
        total_count = result.get('totalCount', 0)

        # 다음 페이지 존재 여부 계산
        fetched_so_far = (page + 1) * page_size
        has_more = total_count > fetched_so_far

        return {
            "projectId": resolved_project_id,
            "totalCount": total_count,
            "page": page,
            "returnedCount": len(tasks),
            "hasMore": has_more,
            "tasks": tasks,
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def set_task_workflow(
    workflow_id: str,
    task_id: Optional[str] = None,
    project_code: Optional[str] = None,
    task_number: Optional[int] = None,
    url: Optional[str] = None,
) -> Dict[str, Any]:
    """업무 상태 변경.

    세 가지 방법으로 업무를 지정할 수 있습니다:
    1. 업무 ID만 제공 (task_id)
    2. 프로젝트 코드 + 업무 번호 (project_code, task_number)
    3. Dooray 웹 URL (url)

    Args:
        workflow_id: 변경할 워크플로우 ID (필수)
        task_id: 업무 ID (예: '9876543210987654321')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        task_number: 업무 번호 (예: 306)
        url: Dooray 웹 URL (예: 'https://company.dooray.com/task/...')

    Returns:
        업데이트 결과

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        project_id, post_id = resolve_task_identifiers(
            task_id=task_id,
            project_code=project_code,
            task_number=task_number,
            url=url,
        )

        client = get_client()
        result = client.set_post_workflow(
            project_id=project_id,
            post_id=post_id,
            workflow_id=workflow_id,
        )

        # 성공 여부 확인
        is_successful = result.get('header', {}).get('isSuccessful', False)

        if is_successful:
            return {
                "success": True,
                "message": "업무 상태가 성공적으로 변경되었습니다.",
            }
        else:
            error_message = result.get('header', {}).get('resultMessage', '알 수 없는 오류')
            return {
                "success": False,
                "error": error_message,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@mcp.tool()
def list_project_tags(
    project_id: Optional[str] = None,
    project_code: Optional[str] = None,
    page: int = 0,
) -> Dict[str, Any]:
    """프로젝트의 태그 목록 조회.

    프로젝트 ID 또는 프로젝트 코드로 프로젝트를 지정할 수 있습니다.
    프로젝트에서 사용 가능한 모든 태그를 반환합니다.

    Args:
        project_id: 프로젝트 ID (예: '1234567890123456789')
        project_code: 프로젝트 코드 (예: '개발팀-업무')
        page: 페이지 번호 (기본: 0)

    Returns:
        태그 목록 (ID, 이름, 색상, 태그 그룹 정보 등)

    Raises:
        ValueError: 잘못된 입력
        DoorayAPIError: API 오류
    """
    try:
        client = get_client()

        # 프로젝트 ID 결정
        if project_code:
            resolved_project_id = find_project_by_code(client, project_code)
            if not resolved_project_id:
                raise ValueError(f"프로젝트를 찾을 수 없습니다: {project_code}")
        elif project_id:
            resolved_project_id = project_id
        else:
            raise ValueError("project_id 또는 project_code 중 하나를 제공해야 합니다.")

        # 페이지당 20개 고정
        page_size = 20

        # 태그 목록 조회
        result = client.list_tags(
            project_id=resolved_project_id,
            page=page,
            size=page_size,
        )

        # 응답에서 태그 목록 추출
        tags = result.get('result', [])
        total_count = result.get('totalCount', 0)

        # 다음 페이지 존재 여부 계산
        fetched_so_far = (page + 1) * page_size
        has_more = total_count > fetched_so_far

        return {
            "projectId": resolved_project_id,
            "totalCount": total_count,
            "page": page,
            "returnedCount": len(tags),
            "hasMore": has_more,
            "tags": tags,
        }

    except Exception as e:
        return {"error": str(e)}


def main():
    """MCP 서버 진입점."""
    mcp.run()
