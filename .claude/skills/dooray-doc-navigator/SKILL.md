---
name: dooray-doc-navigator
description: Dooray API 문서 탐색 및 검색을 돕는 스킬. 사용자가 Dooray API 관련 질문을 하거나, 특정 API 엔드포인트를 찾거나, 문서의 특정 섹션을 탐색하려고 할 때 사용한다. 8000줄이 넘는 긴 API 문서를 효율적으로 탐색할 수 있도록 목차 추출, 섹션 검색, API 엔드포인트 검색 기능을 제공한다.
---

# Dooray Doc Navigator

## Overview

Dooray API 문서(`references/dooray-doc.md`)는 8269줄에 달하는 방대한 문서로, 모든 내용을 한 번에 로드하기 어렵다. 이 스킬은 문서를 효율적으로 탐색하고 필요한 정보를 빠르게 찾을 수 있도록 세 가지 핵심 스크립트를 제공한다. 문서는 스킬 내부에 번들되어 있어 외부 의존성 없이 사용할 수 있다.

## When to Use This Skill

다음과 같은 경우에 이 스킬을 사용한다:

1. **사용자가 Dooray API 문서 전체 구조를 파악하고 싶을 때**
   - "Dooray API 문서의 목차를 보여줘"
   - "어떤 API들이 있는지 알려줘"

2. **특정 섹션이나 주제를 찾고 싶을 때**
   - "Members API 문서 찾아줘"
   - "프로젝트 생성하는 부분 어디 있어?"
   - "태그 관련 API 보여줘"

3. **특정 HTTP 엔드포인트를 찾고 싶을 때**
   - "POST /project API 찾아줘"
   - "GET 메서드만 보여줘"
   - "업무(posts) 관련 API 목록 보여줘"

4. **API 통계나 전체 엔드포인트 목록이 필요할 때**
   - "전체 API 수가 몇 개야?"
   - "메서드별로 분류해서 보여줘"

## Core Capabilities

### 1. 목차 추출 (extract_toc.py)

문서의 전체 목차를 계층 구조로 표시한다.

**사용 방법:**

```bash
python3 scripts/extract_toc.py [옵션]
```

**주요 옵션:**

- `--level LEVEL`: 표시할 최대 헤더 레벨 (1-6, 기본값: 3)
- `--file FILE`: 문서 파일 경로 (기본값: references/dooray-doc.md)
- `--no-line-numbers`: 라인 번호를 표시하지 않음

**예시:**

```bash
# 전체 목차 보기 (레벨 3까지)
python3 scripts/extract_toc.py

# 대분류만 보기 (레벨 1-2)
python3 scripts/extract_toc.py --level 2

# 라인 번호 없이 보기
python3 scripts/extract_toc.py --no-line-numbers
```

**출력 형식:**

```
================================================================================
Dooray API 문서 목차
================================================================================

▶ 기본 (Line 3)
  • End Point (Line 5)
  • 인증 (Line 24)
    • 개인 API 인증 토큰 발급 과정 (Line 26)
...
총 342개 항목
================================================================================
```

**언제 사용하는가:**

- 사용자가 문서의 전체 구조를 파악하고 싶을 때
- 어떤 섹션들이 있는지 빠르게 확인하고 싶을 때
- 특정 주제가 문서의 어디쯤 있는지 대략적인 위치를 알고 싶을 때

### 2. 섹션 검색 (search_section.py)

키워드로 섹션을 검색하고 해당 내용을 표시한다.

**사용 방법:**

```bash
python3 scripts/search_section.py "검색어" [옵션]
```

**주요 옵션:**

- `--file FILE`: 문서 파일 경로
- `--case-sensitive`: 대소문자 구분
- `--no-content`: 내용을 표시하지 않고 제목만 표시
- `--max-lines N`: 표시할 최대 내용 라인 수 (기본값: 30)

**예시:**

```bash
# "Members" 포함된 섹션 검색
python3 scripts/search_section.py "Members"

# "프로젝트" 검색 (제목만)
python3 scripts/search_section.py "프로젝트" --no-content

# 정규표현식으로 검색
python3 scripts/search_section.py "GET /project.*posts"

# 많은 내용 보기
python3 scripts/search_section.py "Tags" --max-lines 100
```

**출력 형식:**

```
================================================================================
검색 결과: 2개 섹션 발견
================================================================================

1.   Common > Members
   라인: 122
   레벨: ##

   내용:
   ----------------------------------------------------------------------------
   ### GET /common/v1/members

   - 멤버 목록을 응답
   ...
```

**언제 사용하는가:**

- 특정 주제나 키워드가 포함된 섹션을 찾을 때
- 섹션의 내용을 빠르게 확인하고 싶을 때
- 정규표현식으로 복잡한 패턴 검색이 필요할 때

### 3. API 엔드포인트 검색 (find_api.py)

모든 API 엔드포인트를 추출하고 검색한다.

**사용 방법:**

```bash
python3 scripts/find_api.py [검색어] [옵션]
```

**주요 옵션:**

- `--method METHOD`: HTTP 메서드 필터 (GET, POST, PUT, DELETE, PATCH)
- `--file FILE`: 문서 파일 경로
- `--no-group`: 섹션별로 그룹화하지 않음
- `--summary`: 통계 정보만 표시

**예시:**

```bash
# 모든 API 목록 보기
python3 scripts/find_api.py

# "projects" 포함된 API만 검색
python3 scripts/find_api.py projects

# GET 메서드만 보기
python3 scripts/find_api.py --method GET

# POST /project 검색
python3 scripts/find_api.py posts --method POST

# API 통계 보기
python3 scripts/find_api.py --summary

# 그룹화 없이 전체 리스트
python3 scripts/find_api.py --no-group
```

**출력 형식 (기본 - 섹션별 그룹화):**

```
================================================================================
Dooray API 엔드포인트 목록 (총 156개)
================================================================================

## Common > Members

  🔵 GET    /common/v1/members                                (Line 125)
  🔵 GET    /common/v1/members/{member-id}                    (Line 184)

## Project > Projects

  🟢 POST   /project/v1/projects                              (Line 444)
  🔵 GET    /project/v1/projects                              (Line 495)
  🔵 GET    /project/v1/projects/{project-id}                 (Line 617)
  ...
```

**출력 형식 (통계):**

```
================================================================================
API 통계
================================================================================

총 API 수: 156

메서드별 분포:
  DELETE:  12 ██████
  GET   :  89 ████████████████████████████████████████████
  PATCH :   3 █
  POST  :  45 ██████████████████████
  PUT   :   7 ███

================================================================================
```

**언제 사용하는가:**

- 특정 API 엔드포인트를 찾을 때
- HTTP 메서드별로 API를 필터링하고 싶을 때
- 전체 API 목록을 섹션별로 정리해서 보고 싶을 때
- API 통계 정보가 필요할 때

## Workflow Examples

### 예시 1: 사용자가 "프로젝트 생성 API 알려줘"라고 요청

1. **API 엔드포인트 검색 실행:**

   ```bash
   python3 scripts/find_api.py projects --method POST
   ```

2. **결과 확인 후 라인 번호로 섹션 검색:**

   ```bash
   python3 scripts/search_section.py "POST /project/v1/projects"
   ```

3. **필요시 Read 도구로 정확한 라인 읽기:**

   ```
   Read references/dooray-doc.md (offset: 444, limit: 50)
   ```

### 예시 2: 사용자가 "태그 관련 API 다 보여줘"라고 요청

1. **키워드로 섹션 검색:**

   ```bash
   python3 scripts/search_section.py "Tags"
   ```

2. **태그 관련 API만 필터링:**

   ```bash
   python3 scripts/find_api.py tags
   ```

### 예시 3: 사용자가 "전체 구조 파악하고 싶어"라고 요청

1. **목차 추출 (대분류):**

   ```bash
   python3 scripts/extract_toc.py --level 2
   ```

2. **API 통계:**

   ```bash
   python3 scripts/find_api.py --summary
   ```

## Best Practices

1. **단계적 접근:**
   - 먼저 `extract_toc.py`로 전체 구조 파악
   - `search_section.py`로 관심 섹션 찾기
   - `find_api.py`로 정확한 엔드포인트 확인
   - 필요시 Read 도구로 세부 내용 읽기

2. **스크립트 실행 전 작업 디렉토리 확인:**
   - 모든 스크립트는 스킬 디렉토리에서 실행
   - 기본 파일 경로는 `references/dooray-doc.md`
   - 문서는 스킬에 번들되어 있어 별도로 준비할 필요 없음

3. **효율적인 검색:**
   - 정규표현식 활용 (예: `"GET /project.*posts"`)
   - 메서드 필터와 키워드 검색 조합
   - `--no-content`로 빠른 스캔 후 상세 검색

4. **결과 해석:**
   - 라인 번호를 활용하여 Read 도구로 정확한 위치 읽기
   - 섹션 그룹화로 관련 API 한 번에 파악
   - 통계 정보로 API 분포 이해

## Resources

### scripts/

이 스킬은 세 가지 핵심 Python 스크립트를 포함한다:

- **extract_toc.py**: 마크다운 헤더를 파싱하여 계층적 목차 생성
- **search_section.py**: 키워드로 섹션 검색 및 내용 추출
- **find_api.py**: API 엔드포인트 추출, 필터링, 통계

모든 스크립트는 독립적으로 실행 가능하며 `--help` 옵션으로 상세 사용법 확인이 가능하다.

### references/

- **dooray-doc.md**: Dooray API 공식 문서 (8269줄). 스킬에 번들되어 있어 외부 의존성이 없다.

## Notes

- Dooray API 문서는 8269줄로 매우 길기 때문에 전체를 한 번에 Read하는 것은 비효율적이다
- 스크립트를 활용하여 필요한 부분만 정확히 찾아 읽는 것이 권장된다
- 정규표현식을 지원하므로 복잡한 패턴 검색도 가능하다
- 모든 스크립트는 UTF-8 인코딩을 사용하며 한글을 완벽히 지원한다
