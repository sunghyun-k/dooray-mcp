"""Dooray API client."""

import os
from typing import Any, Dict, Optional
import requests


class DoorayAPIError(Exception):
    """Dooray API 오류."""
    pass


class DoorayClient:
    """Dooray API 클라이언트."""

    DEFAULT_BASE_URL = "https://api.dooray.com"

    def __init__(self, api_token: Optional[str] = None, base_url: Optional[str] = None):
        """초기화.

        Args:
            api_token: Dooray API 토큰. None이면 환경 변수에서 가져옴.
            base_url: API base URL. None이면 환경 변수에서 가져옴.

        Raises:
            DoorayAPIError: API 토큰이 없는 경우
        """
        self.api_token = api_token or os.getenv("DOORAY_API_TOKEN")
        if not self.api_token:
            raise DoorayAPIError(
                "Dooray API 토큰이 필요합니다. "
                "DOORAY_API_TOKEN 환경 변수를 설정하세요."
            )

        # 환경 변수 또는 기본값으로 base URL 설정
        self.base_url = base_url or os.getenv("DOORAY_API_BASE_URL", self.DEFAULT_BASE_URL)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """HTTP 요청 실행.

        Args:
            method: HTTP 메서드 (GET, POST, PUT, DELETE)
            endpoint: API 엔드포인트 경로
            params: 쿼리 파라미터
            json: 요청 본문 (JSON)

        Returns:
            응답 JSON

        Raises:
            DoorayAPIError: API 요청 실패 시
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"dooray-api {self.api_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise DoorayAPIError(f"API 요청 실패: {e}")
        except requests.exceptions.RequestException as e:
            raise DoorayAPIError(f"네트워크 오류: {e}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """GET 요청."""
        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST 요청."""
        return self._request("POST", endpoint, json=json)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """PUT 요청."""
        return self._request("PUT", endpoint, json=json)

    def delete(
        self,
        endpoint: str,
    ) -> Dict[str, Any]:
        """DELETE 요청."""
        return self._request("DELETE", endpoint)

    # 프로젝트 API

    def list_projects(
        self,
        member: str = "me",
        page: int = 0,
        size: int = 100,
    ) -> Dict[str, Any]:
        """프로젝트 목록 조회.

        Args:
            member: 'me'로 설정 시 내가 속한 프로젝트만 조회
            page: 페이지 번호 (0부터 시작)
            size: 페이지 크기 (최대 100)

        Returns:
            프로젝트 목록
        """
        params = {
            "member": member,
            "page": page,
            "size": size,
        }
        return self.get("/project/v1/projects", params=params)

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """프로젝트 상세 조회.

        Args:
            project_id: 프로젝트 ID

        Returns:
            프로젝트 상세 정보
        """
        return self.get(f"/project/v1/projects/{project_id}")

    def get_project_members(
        self,
        project_id: str,
        page: int = 0,
        size: int = 100,
        roles: Optional[str] = None,
    ) -> Dict[str, Any]:
        """프로젝트 멤버 목록 조회.

        Args:
            project_id: 프로젝트 ID
            page: 페이지 번호 (0부터 시작)
            size: 페이지 크기 (최대 100)
            roles: 역할 필터 (admin, member, 기본: 모두 조회)

        Returns:
            프로젝트 멤버 목록
        """
        params = {
            "page": page,
            "size": size,
        }
        if roles:
            params["roles"] = roles

        return self.get(f"/project/v1/projects/{project_id}/members", params=params)

    def get_project_member_groups(
        self,
        project_id: str,
        page: int = 0,
        size: int = 100,
    ) -> Dict[str, Any]:
        """프로젝트 멤버 그룹 목록 조회.

        Args:
            project_id: 프로젝트 ID
            page: 페이지 번호 (0부터 시작)
            size: 페이지 크기 (최대 100)

        Returns:
            프로젝트 멤버 그룹 목록
        """
        params = {
            "page": page,
            "size": size,
        }
        return self.get(f"/project/v1/projects/{project_id}/member-groups", params=params)

    def get_project_member_group(
        self,
        project_id: str,
        member_group_id: str,
    ) -> Dict[str, Any]:
        """프로젝트 멤버 그룹 상세 조회 (멤버 목록 포함).

        Args:
            project_id: 프로젝트 ID
            member_group_id: 멤버 그룹 ID

        Returns:
            멤버 그룹 상세 정보 (멤버 목록 포함)
        """
        return self.get(f"/project/v1/projects/{project_id}/member-groups/{member_group_id}")

    # 업무(Post) API

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """업무 조회 (프로젝트 ID 없이).

        Args:
            post_id: 업무 ID

        Returns:
            업무 상세 정보
        """
        return self.get(f"/project/v1/posts/{post_id}")

    def get_post_with_project(
        self,
        project_id: str,
        post_id: str,
    ) -> Dict[str, Any]:
        """업무 조회 (프로젝트 ID 포함).

        Args:
            project_id: 프로젝트 ID
            post_id: 업무 ID

        Returns:
            업무 상세 정보
        """
        return self.get(f"/project/v1/projects/{project_id}/posts/{post_id}")

    def list_posts(
        self,
        project_id: str,
        post_number: Optional[int] = None,
        parent_post_id: Optional[str] = None,
        from_member_ids: Optional[list] = None,
        to_member_ids: Optional[list] = None,
        cc_member_ids: Optional[list] = None,
        workflow_classes: Optional[list] = None,
        subjects: Optional[str] = None,
        created_at: Optional[str] = None,
        order: Optional[str] = None,
        page: int = 0,
        size: int = 20,
    ) -> Dict[str, Any]:
        """업무 목록 조회.

        Args:
            project_id: 프로젝트 ID
            post_number: 특정 업무 번호로 필터링
            parent_post_id: 상위 업무 ID (하위 업무 목록 조회 시)
            from_member_ids: 작성자 ID 목록 (organizationMemberId)
            to_member_ids: 담당자 ID 목록 (organizationMemberId)
            cc_member_ids: 참조자 ID 목록 (organizationMemberId)
            workflow_classes: 상태 클래스 목록 (상태의 대분류)
            subjects: 제목 필터 (부분 일치)
            created_at: 생성일 필터 (today, thisweek, prev-{N}d, next-{N}d, ISO8601 범위)
            order: 정렬 기준 (createdAt, -createdAt, postUpdatedAt, -postUpdatedAt 등)
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            업무 목록
        """
        params: Dict[str, Any] = {
            "page": page,
            "size": size,
        }
        if order is not None:
            params["order"] = order
        if post_number is not None:
            params["postNumber"] = post_number
        if parent_post_id is not None:
            params["parentPostId"] = parent_post_id
        if from_member_ids is not None:
            params["fromMemberIds"] = ",".join(from_member_ids)
        if to_member_ids is not None:
            params["toMemberIds"] = ",".join(to_member_ids)
        if cc_member_ids is not None:
            params["ccMemberIds"] = ",".join(cc_member_ids)
        if workflow_classes is not None:
            params["postWorkflowClasses"] = ",".join(workflow_classes)
        if subjects is not None:
            params["subjects"] = subjects
        if created_at is not None:
            params["createdAt"] = created_at

        return self.get(f"/project/v1/projects/{project_id}/posts", params=params)

    def create_post(
        self,
        project_id: str,
        subject: str,
        body_content: Optional[str] = None,
        body_mime_type: str = "text/x-markdown",
        users_to: Optional[list] = None,
        users_cc: Optional[list] = None,
        parent_post_id: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        due_date_flag: bool = True,
        milestone_id: Optional[str] = None,
        tag_ids: Optional[list] = None,
    ) -> Dict[str, Any]:
        """업무(Post) 생성.

        Args:
            project_id: 프로젝트 ID
            subject: 업무 제목 (필수)
            body_content: 업무 본문 내용
            body_mime_type: 본문 MIME 타입 ('text/x-markdown' 또는 'text/html')
            users_to: 담당자 목록 (예: [{"type": "member", "member": {"organizationMemberId": "1"}}])
            users_cc: 참조자 목록
            parent_post_id: 상위 업무 ID (하위 업무로 만들 경우)
            priority: 우선순위 ('highest', 'high', 'normal', 'low', 'lowest', 'none')
            due_date: 마감일 (ISO 8601 형식, 예: '2025-12-31T23:59:59+09:00')
            due_date_flag: 마감일 플래그 (항상 true 권장)
            milestone_id: 마일스톤 ID
            tag_ids: 태그 ID 목록

        Returns:
            생성된 업무 정보 (ID 포함)
        """
        data: Dict[str, Any] = {
            "subject": subject,
        }

        # 본문
        if body_content is not None:
            data["body"] = {
                "content": body_content,
                "mimeType": body_mime_type,
            }

        # 사용자 (담당자/참조자)
        if users_to is not None or users_cc is not None:
            data["users"] = {}
            if users_to is not None:
                data["users"]["to"] = users_to
            if users_cc is not None:
                data["users"]["cc"] = users_cc

        # 상위 업무 ID
        if parent_post_id is not None:
            data["parentPostId"] = parent_post_id

        # 우선순위
        if priority is not None:
            data["priority"] = priority

        # 마감일
        if due_date is not None:
            data["dueDate"] = due_date
            data["dueDateFlag"] = due_date_flag

        # 마일스톤
        if milestone_id is not None:
            data["milestoneId"] = milestone_id

        # 태그
        if tag_ids is not None:
            data["tagIds"] = tag_ids

        return self.post(
            f"/project/v1/projects/{project_id}/posts",
            json=data,
        )

    def update_post(
        self,
        project_id: str,
        post_id: str,
        subject: Optional[str] = None,
        body_content: Optional[str] = None,
        body_mime_type: str = "text/x-markdown",
        users_to: Optional[list] = None,
        users_cc: Optional[list] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        due_date_flag: bool = True,
        milestone_id: Optional[str] = None,
        tag_ids: Optional[list] = None,
        version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """업무(Post) 수정.

        Args:
            project_id: 프로젝트 ID
            post_id: 업무 ID
            subject: 업무 제목
            body_content: 업무 본문 내용
            body_mime_type: 본문 MIME 타입 ('text/x-markdown' 또는 'text/html')
            users_to: 담당자 목록 (예: [{"type": "member", "member": {"organizationMemberId": "1"}}])
            users_cc: 참조자 목록
            priority: 우선순위 ('highest', 'high', 'normal', 'low', 'lowest', 'none')
            due_date: 마감일 (ISO 8601 형식, 예: '2025-12-31T23:59:59+09:00')
            due_date_flag: 마감일 플래그 (항상 true 권장)
            milestone_id: 마일스톤 ID
            tag_ids: 태그 ID 목록
            version: 버전 번호 (동시 수정 방지용, None이면 최신 버전 사용)

        Returns:
            업데이트 결과
        """
        data: Dict[str, Any] = {}

        # 제목
        if subject is not None:
            data["subject"] = subject

        # 본문
        if body_content is not None:
            data["body"] = {
                "content": body_content,
                "mimeType": body_mime_type,
            }

        # 사용자 (담당자/참조자)
        if users_to is not None or users_cc is not None:
            data["users"] = {}
            if users_to is not None:
                data["users"]["to"] = users_to
            if users_cc is not None:
                data["users"]["cc"] = users_cc

        # 우선순위
        if priority is not None:
            data["priority"] = priority

        # 마감일
        if due_date is not None:
            data["dueDate"] = due_date
            data["dueDateFlag"] = due_date_flag

        # 마일스톤
        if milestone_id is not None:
            data["milestoneId"] = milestone_id

        # 태그
        if tag_ids is not None:
            data["tagIds"] = tag_ids

        # 버전
        if version is not None:
            data["version"] = version

        return self.put(
            f"/project/v1/projects/{project_id}/posts/{post_id}",
            json=data,
        )

    # 댓글(Log) API

    def list_logs(
        self,
        project_id: str,
        post_id: str,
        page: int = 0,
        size: int = 20,
        order: str = "createdAt",
    ) -> Dict[str, Any]:
        """댓글 목록 조회.

        Args:
            project_id: 프로젝트 ID
            post_id: 업무 ID
            page: 페이지 번호 (0부터 시작)
            size: 페이지 크기 (최대 100)
            order: 정렬 순서 ('createdAt': 오래된 순, '-createdAt': 최신 순)

        Returns:
            댓글 목록
        """
        params = {
            "page": page,
            "size": size,
            "order": order,
        }
        return self.get(
            f"/project/v1/projects/{project_id}/posts/{post_id}/logs",
            params=params,
        )

    def create_log(
        self,
        project_id: str,
        post_id: str,
        content: str,
        mime_type: str = "text/x-markdown",
    ) -> Dict[str, Any]:
        """댓글 작성.

        Args:
            project_id: 프로젝트 ID
            post_id: 업무 ID
            content: 댓글 내용
            mime_type: 콘텐츠 타입 ('text/x-markdown' 또는 'text/html')

        Returns:
            생성된 댓글 정보
        """
        data = {
            "body": {
                "content": content,
                "mimeType": mime_type,
            }
        }
        return self.post(
            f"/project/v1/projects/{project_id}/posts/{post_id}/logs",
            json=data,
        )

    def update_log(
        self,
        project_id: str,
        post_id: str,
        log_id: str,
        content: str,
        mime_type: str = "text/x-markdown",
    ) -> Dict[str, Any]:
        """댓글 수정.

        Args:
            project_id: 프로젝트 ID
            post_id: 업무 ID
            log_id: 댓글 ID
            content: 댓글 내용
            mime_type: 콘텐츠 타입 ('text/x-markdown' 또는 'text/html')

        Returns:
            업데이트 결과
        """
        data = {
            "body": {
                "content": content,
                "mimeType": mime_type,
            }
        }
        return self.put(
            f"/project/v1/projects/{project_id}/posts/{post_id}/logs/{log_id}",
            json=data,
        )

    # 상태(Workflow) API

    def get_workflows(self, project_id: str) -> Dict[str, Any]:
        """프로젝트의 워크플로우(상태) 목록 조회.

        Args:
            project_id: 프로젝트 ID

        Returns:
            워크플로우 목록 (ID, 이름, 클래스 등)
        """
        return self.get(f"/project/v1/projects/{project_id}/workflows")

    def set_post_workflow(
        self,
        project_id: str,
        post_id: str,
        workflow_id: str,
    ) -> Dict[str, Any]:
        """업무(Post) 워크플로우(상태) 변경.

        Args:
            project_id: 프로젝트 ID
            post_id: 업무 ID
            workflow_id: 변경할 워크플로우 ID

        Returns:
            업데이트 결과
        """
        data = {
            "workflowId": workflow_id,
        }
        return self.post(
            f"/project/v1/projects/{project_id}/posts/{post_id}/set-workflow",
            json=data,
        )

    # 태그(Tag) API

    def list_tags(
        self,
        project_id: str,
        page: int = 0,
        size: int = 20,
    ) -> Dict[str, Any]:
        """프로젝트의 태그 목록 조회.

        Args:
            project_id: 프로젝트 ID
            page: 페이지 번호 (0부터 시작)
            size: 페이지 크기 (기본: 20, 최대: 100)

        Returns:
            태그 목록 (ID, 이름, 색상, 태그 그룹 정보 등)
        """
        params = {
            "page": page,
            "size": size,
        }
        return self.get(f"/project/v1/projects/{project_id}/tags", params=params)
