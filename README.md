# Dooray MCP

Dooray 업무 관리를 위한 Model Context Protocol (MCP) 서버입니다.

이 MCP 서버는 업무 생성/조회/수정/목록, 댓글 관리, 프로젝트 멤버/상태/태그 조회 등 총 10가지 도구를 제공합니다.

## 필수 요구사항

이 프로젝트는 [uv](https://github.com/astral-sh/uv)를 사용하여 Python 의존성을 관리합니다. uv는 빠르고 안정적인 Python 패키지 관리자입니다.

### uv 설치

macOS에서 Homebrew를 사용하여 설치:

```bash
brew install uv
```

다른 운영체제의 설치 방법은 [uv 공식 문서](https://github.com/astral-sh/uv)를 참조하세요.

## 설치

### 1단계: API 토큰 발급

개인설정 > API > 개인 인증 토큰 메뉴에서 토큰을 생성합니다.

- 토큰은 발급받은 계정과 동일한 권한을 갖습니다
- API로 작업한 내용은 해당 사용자가 로그인하여 Dooray를 직접 사용하는 것과 차이가 없습니다

### 2단계: 환경 변수 설정

토큰을 설정하는 방법은 두 가지가 있습니다:

#### 방법 A: 전역 설정 (추천)

모든 프로젝트에서 사용할 수 있도록 사용자 홈 디렉토리에 설정:

```jsonc
// ~/.claude/settings.json
{
  "env": {
    "DOORAY_API_TOKEN": "your-api-token-here",
    "DOORAY_API_BASE_URL": "https://api.dooray.com" // 선택사항 (기본값: https://api.dooray.com)
  }
}
```

#### 방법 B: 프로젝트별 설정

특정 프로젝트에서만 사용하도록 프로젝트 디렉토리에 설정:

```jsonc
// <프로젝트 디렉토리>/.claude/settings.local.json
{
  "env": {
    "DOORAY_API_TOKEN": "your-api-token-here",
    "DOORAY_API_BASE_URL": "https://api.dooray.com" // 선택사항 (기본값: https://api.dooray.com)
  }
}
```

#### 지원하는 API 서버

`DOORAY_API_BASE_URL` 환경 변수를 통해 다양한 Dooray 환경을 지원합니다:

- **민간 클라우드** (기본값): `https://api.dooray.com`
- **공공 클라우드**: `https://api.gov-dooray.com`
- **공공 업무망 클라우드**: `https://api.gov-dooray.co.kr`
- **금융 클라우드**: `https://api.dooray.co.kr`

### 3단계: Claude Code에 MCP 서버 설치

Claude Code에서 다음 명령을 실행하여 Dooray MCP 서버를 설치합니다:

```bash
claude mcp add dooray -- uvx --from git+https://github.com/sunghyun-k/dooray-mcp dooray-mcp
```

## 기능

이 MCP 서버는 다음 10가지 도구를 제공합니다:

### 1. `create_task` - 업무 생성

새로운 업무를 생성합니다.

**필수 파라미터:**

- `subject`: 업무 제목

**지원하는 입력 방식:**

- 프로젝트 ID: `project_id="1234567890123456789"`
- 프로젝트 코드: `project_code="개발팀-업무"`

**추가 파라미터 (모두 선택사항):**

- `body_content`: 업무 본문 내용
- `body_mime_type`: 본문 MIME 타입 (기본: `text/x-markdown`, 또는 `text/html`)
- `users_to`: 담당자 목록 (예: `[{"type": "member", "member": {"organizationMemberId": "123"}}]`)
- `users_cc`: 참조자 목록
- `parent_post_id`: 상위 업무 ID (하위 업무로 만들 경우)
- `priority`: 우선순위 (`highest`, `high`, `normal`, `low`, `lowest`, `none`)
- `due_date`: 마감일 (ISO 8601 형식, 예: `2025-12-31T23:59:59+09:00`)
- `milestone_id`: 마일스톤 ID
- `tag_ids`: 태그 ID 목록 (예: `["tag1", "tag2"]`)

**반환 정보:**

- 성공 여부
- 생성된 업무 ID
- 메시지

**사용 예시:**

```python
# 기본 업무 생성
create_task(
    project_code="개발팀-업무",
    subject="새로운 기능 구현"
)

# 상세 정보가 포함된 업무 생성
create_task(
    project_code="개발팀-업무",
    subject="버그 수정 필요",
    body_content="로그인 버튼이 작동하지 않는 문제",
    priority="high",
    due_date="2025-11-30T23:59:59+09:00",
    users_to=[{"type": "member", "member": {"organizationMemberId": "123"}}]
)
```

### 2. `get_task` - 업무 조회

업무의 상세 정보를 조회합니다.

**지원하는 입력 방식:**

- 업무 ID만 제공: `task_id="9876543210987654321"`
- 프로젝트 코드 + 업무 번호: `project_code="개발팀-업무"`, `task_number=123`
- Dooray 웹 URL: `url="https://company.dooray.com/task/..."`

**반환 정보:**

- 업무 제목, 본문, 상태
- 담당자, 생성자 정보
- 생성일, 수정일, 만기일
- 워크플로, 마일스톤, 태그
- 상위 업무 정보
- 하위 업무 목록 (최대 100개)

### 3. `list_task_comments` - 댓글 조회

업무의 댓글 목록을 조회합니다.

**지원하는 입력 방식:**

- 업무 ID만 제공: `task_id="9876543210987654321"`
- 프로젝트 코드 + 업무 번호: `project_code="개발팀-업무"`, `task_number=123`
- Dooray 웹 URL: `url="https://company.dooray.com/task/..."`

**추가 파라미터:**

- `page`: 페이지 번호 (기본: 0)
- `size`: 페이지 크기 (기본: 20, 최대: 100)

**반환 정보:**

- 댓글 ID, 타입
- 작성자 정보
- 댓글 내용 (본문, MIME 타입)
- 작성일시, 수정일시
- 총 댓글 수

### 4. `create_task_comment` - 댓글 작성

업무에 새로운 댓글을 작성합니다.

**필수 파라미터:**

- `content`: 댓글 내용

**지원하는 입력 방식:**

- 업무 ID만 제공: `task_id="9876543210987654321"`
- 프로젝트 코드 + 업무 번호: `project_code="개발팀-업무"`, `task_number=123`
- Dooray 웹 URL: `url="https://company.dooray.com/task/..."`

**추가 파라미터:**

- `mime_type`: 콘텐츠 타입 (기본: `text/x-markdown`, 또는 `text/html`)

**반환 정보:**

- 성공 여부
- 생성된 댓글 ID

### 5. `update_task` - 업무 수정

업무의 정보를 수정합니다. 수정하고 싶은 필드만 제공하면 됩니다 (부분 업데이트 지원).

**지원하는 입력 방식:**

- 업무 ID만 제공: `task_id="9876543210987654321"`
- 프로젝트 코드 + 업무 번호: `project_code="개발팀-업무"`, `task_number=123`
- Dooray 웹 URL: `url="https://company.dooray.com/task/..."`

**수정 가능한 파라미터 (모두 선택사항):**

- `subject`: 업무 제목
- `body_content`: 업무 본문 내용
- `body_mime_type`: 본문 MIME 타입 (기본: `text/x-markdown`, 또는 `text/html`)
- `users_to`: 담당자 목록 (예: `[{"type": "member", "member": {"organizationMemberId": "123"}}]`)
- `users_cc`: 참조자 목록
- `priority`: 우선순위 (`highest`, `high`, `normal`, `low`, `lowest`, `none`)
- `due_date`: 마감일 (ISO 8601 형식, 예: `2025-12-31T23:59:59+09:00`)
- `milestone_id`: 마일스톤 ID
- `tag_ids`: 태그 ID 목록 (예: `["tag1", "tag2"]`)
- `version`: 버전 번호 (동시 수정 방지용, None이면 최신 버전 사용)

**반환 정보:**

- 성공 여부
- 오류 메시지 (실패 시)

### 6. `get_project_members` - 프로젝트 멤버 및 그룹 조회

프로젝트의 멤버와 멤버 그룹을 모두 조회합니다. 각 멤버 그룹에는 소속된 멤버 목록도 포함됩니다.

**지원하는 입력 방식:**

- 프로젝트 ID: `project_id="4062369282783966548"`
- 프로젝트 코드: `project_code="개발팀-업무"`

**반환 정보:**

- **멤버 목록**:
  - Organization Member ID
  - 프로젝트 내 역할 (admin/member)
- **멤버 그룹 목록**:
  - 그룹 ID
  - 그룹 코드
  - 그룹에 속한 멤버 목록 (ID, 이름)

**사용 예시:**

담당자를 지정할 때 필요한 ID를 찾을 수 있습니다:

- 개인 담당자: `{"type": "member", "member": {"organizationMemberId": "123"}}`
- 그룹 담당자: `{"type": "group", "group": {"projectMemberGroupId": "456"}}`

### 7. `get_available_workflows` - 프로젝트 상태 목록 조회

프로젝트에서 사용 가능한 모든 상태를 조회합니다.

**지원하는 입력 방식:**

- 프로젝트 ID: `project_id="4062369282783966548"`
- 프로젝트 코드: `project_code="개발팀-업무"`

**반환 정보:**

- 상태 ID (workflow_id로 업무 상태 변경 시 사용)
- 상태 이름 (여러 언어 지원)
- 상태 클래스 (backlog, registered, working, closed)
- 정렬 순서

**상태 클래스:**

- `backlog`: 대기
- `registered`: 등록 (할 일)
- `working`: 진행 중
- `closed`: 완료

### 8. `list_project_tasks` - 프로젝트 업무 목록 조회

프로젝트의 업무 목록을 조회합니다.

**지원하는 입력 방식:**

- 프로젝트 ID: `project_id="4062369282783966548"`
- 프로젝트 코드: `project_code="개발팀-업무"`

**필터 파라미터 (모두 선택사항):**

- `from_member_ids`: 작성자 ID 목록 (organizationMemberId)
- `to_member_ids`: 담당자 ID 목록 (organizationMemberId)
- `cc_member_ids`: 참조자 ID 목록 (organizationMemberId)
- `workflow_classes`: 상태 클래스 목록 (상태의 대분류, `get_available_workflows`로 조회 가능)
- `subject`: 제목 필터 (부분 일치)
- `size`: 조회할 업무 수 (기본: 100, 최대: 100)

**반환 정보:**

- 프로젝트 ID
- 총 업무 수 (totalCount)
- 반환된 업무 수 (returnedCount)
- 추가 업무 존재 여부 (hasMore)
- 업무 목록 (ID, 제목, 상태, 담당자 등)

**사용 예시:**

```python
# 프로젝트의 모든 업무 조회
list_project_tasks(project_code="개발팀-업무")

# 특정 상태 클래스의 업무만 조회 (클래스는 get_available_workflows로 확인)
list_project_tasks(
    project_code="개발팀-업무",
    workflow_classes=["working"]
)

# 특정 담당자의 업무 조회
list_project_tasks(
    project_code="개발팀-업무",
    to_member_ids=["1234567890"]
)
```

### 9. `set_task_workflow` - 업무 상태 변경

업무의 상태를 변경합니다.

**필수 파라미터:**

- `workflow_id`: 변경할 상태 ID (get_available_workflows로 조회 가능)

**지원하는 입력 방식:**

- 업무 ID만 제공: `task_id="9876543210987654321"`
- 프로젝트 코드 + 업무 번호: `project_code="개발팀-업무"`, `task_number=123`
- Dooray 웹 URL: `url="https://company.dooray.com/task/..."`

**반환 정보:**

- 성공 여부
- 오류 메시지 (실패 시)

**사용 예시:**

1. 먼저 프로젝트의 사용 가능한 상태 목록 조회:

   ```python
   statuses = get_available_workflows(project_code="개발팀-업무")
   # 결과에서 원하는 상태의 ID 확인
   ```

2. 해당 상태 ID로 업무 상태 변경:

   ```python
   set_task_workflow(
       workflow_id="3629707640373969653",
       project_code="개발팀-업무",
       task_number=123
   )
   ```

### 10. `list_project_tags` - 프로젝트 태그 목록 조회

프로젝트에서 사용 가능한 모든 태그를 조회합니다.

**지원하는 입력 방식:**

- 프로젝트 ID: `project_id="4062369282783966548"`
- 프로젝트 코드: `project_code="개발팀-업무"`

**추가 파라미터:**

- `page`: 페이지 번호 (기본: 0)
- `size`: 페이지 크기 (기본: 20, 최대: 100)

**반환 정보:**

- 태그 ID (tag_ids로 업무 생성/수정 시 사용)
- 태그 이름
- 태그 색상
- 태그 그룹 정보 (ID, 이름, mandatory, selectOne)
- 총 태그 수

**태그 그룹 속성:**

- `mandatory`: true인 경우 업무 등록 시 해당 그룹에서 하나 이상의 태그 할당 필요
- `selectOne`: true인 경우 해당 그룹에서 하나의 태그만 선택 가능, false인 경우 여러 개 선택 가능

**사용 예시:**

1. 프로젝트의 태그 목록 조회:

   ```python
   tags = list_project_tags(project_code="개발팀-업무")
   # 결과에서 원하는 태그의 ID 확인
   ```

2. 조회한 태그 ID로 업무 생성 시 태그 지정:

   ```python
   create_task(
       project_code="개발팀-업무",
       subject="새로운 기능",
       tag_ids=["4062401244884975089", "4062400865106463592"]
   )
   ```

## 라이선스

MIT License
