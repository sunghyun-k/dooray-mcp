# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소에서 작업할 때 참고할 가이드라인을 제공합니다.

## 프로젝트 설명

Dooray 업무 관리를 위한 Model Context Protocol (MCP) 서버입니다. Dooray API를 통해 업무(task) 관리, 댓글(comment) 관리 등의 기능을 제공합니다.

### 기술 스택

- **Python 3.10+**: 프로그래밍 언어
- **FastMCP**: MCP 서버 프레임워크
- **uv**: Python 패키지 관리자
- **requests**: HTTP 클라이언트

## 필수 지침

### 언어 지침

- 항상 한국어로 답변한다.

### 코드 스타일

- Python 코드는 가독성을 우선으로 작성
- Type hints 사용 권장
- Docstring은 한국어로 작성

### 작업 완료 후 지침

- 변경된 기능에 대해 README.md 파일을 업데이트한다.

### 참조 자료

- **Dooray API 문서 스킬**: `dooray-doc-navigator` - Dooray API 문서 검색 및 탐색용

### 프로젝트 구조

```
dooray-mcp/
├── src/dooray_mcp/    # 메인 소스 코드
│   ├── server.py      # FastMCP 서버 (도구 정의)
│   ├── client.py      # Dooray API 클라이언트
│   └── utils.py       # URL 파싱 등 유틸리티
├── pyproject.toml     # 프로젝트 설정
├── uv.lock           # 의존성 잠금 파일
└── README.md         # 사용자 문서
```
