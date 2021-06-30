# CTRL-F Back-end Default API Spec

## Format

### 기본 응답 포맷

```json
// SUCCESS
{
    ...
}
    
// FAIL/ERROR
{
    "message": "", // 사용자 노출 에러 메세지,
}
```



### 예시

#### SUCCESS(2XX)

```json
// Single
{
    "id": 1,
    "title": "테스트 타이틀 입니다",
    "contents": "테스트 컨텐츠 입니다."
}

// Multiple
{
    "pagination": {
        "has_next": true,
        "total_count": 1,
        "page": 1,
        "page_size": 200
    },
    "results": [
        {
            "id": 1,
            "title": "테스트 타이틀 입니다.",
            "contents": "테스트 컨텐츠 입니다."
        },
        {...},
        {...},
        {...}
         ...
    ]
}
```



### FAIL(4XX)

```json
// Single
{
    "message": "ID,PW 값이 유효하지 않습니다.
}

// Multiple - 복수의 에러에 대한 정보가 필요할 시에는 수정 필요
{
    "message": "ID,PW 값이 유효하지 않습니다. 
}
```

### Error(5XX)

```json
// Expected - 에러에 대한 상세 정보가 필요할 시에는 수정 필요
{
    "message": "서버 에러가 발생 하였습니다."
}

// UnExpected
```



## Status Code

*   `2XX`
    *   200: 성공
    *   201: 생성 성공
    *   204: 삭제 성공
*   `4XX`
    *   400: 파라미터 오류, 잘못된 요청
    *   401: 인증 실패
    *   403: 권한 없음
    *   404: 리소스를 찾을 수 없음
*   `5XX`
    *   500: 서버 에러

## Methods

`GET` : 조회

`POST` : 생성

`PUT` : 전체 수정

`PATCH` : 부분 수정

`DELETE` : 삭제

## Headers

*   Contenty Type: `application/json`
*   Authorization: `JWT {token}`