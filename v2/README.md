# CtrlF Backend API Doc



## Common

```
BASE_URL : "https://..."
```



```python
# 401
{
    "message": "token이 유효하지 않습니다."
}
```



```python
# 500
{
    "message": "서버에러가 발생 하였습니다."
}
```

## User
### 계정
* 회원가입
    * POST 회원가입 submit

      * url

        ```
        POST {BASE_URL}/api/auth/signup
        ```

      * Request

        ```json
        {
            "email": "test1234@testcom",
            "code": "YWJjZGU=",
            "nickname": "my nickname",
            "password": "testpassword%*",
            "password_confirm": "testpassword%*"
        }
        ```

      * Response

        * 2XX

          ```json
          {}
          ```

        * 4XX

          * 400

            ```json
            {
                "message": "전달된 값이 올바르지 않습니다."
            }
            ```

            

            ```json
            {
                "message": "코드가 일치 하지 않습니다."
            }
            ```

    * 중복

      * GET 닉네임 중복 확인

        * url

          ```
          GET {BASE_URL}/api/auth/signup/nickname/duplicate
          ```

        * Request

          ```json
          GET {BASE_URL}/api/auth/signup/nickname/duplicate?data=nick
          ```

        * Response

          * 2XX

            ```json
            {
              "message" : "사용 가능한 닉네임입니다."
            }
            ```

          * 4XX

            ```json
            {
              "message" : "전달된 값이 올바르지 않습니다."
            }
            ```

            ```json
            {
              "message" : "이미 존재하는 닉네임입니다."
            }
            ```

      * GET 이메일 중복 확인

        * url

          ```
          GET {BASE_URL}/api/auth/signup/email/duplicate
          ```

        * Request

          ```
          GET {BASE_URL}/api/auth/signup/email/duplicate?data=test@test.com
          ```

        * Response

          * 2XX
          ```json
          {
            "message": "사용 가능한 이메일 입니다."
          }
          ```
          * 4XX
            1. 이미 존재하는 이메일일 경우
            ```json
            {
              "message": "이미 존재하는 이메일 입니다."
            }
            ```
            2. 이메일 형식이 아닌 경우
            ```json
            {
              "message": "이메일 형식이 유효하지 않습니다."
            }
            ```

          

    * POST 이메일 인증 메일 보내기

      * url

        ```
        POST {BASE_URL}/api/auth/email
        ```

      * Request

        ```json
        {
            "email": "test1234@test.com"
        }
        ```

      * Response

        * 2XX
            * 200
             ```json
             {
                 "message": "인증 메일이 발송되었습니다."
             }
             ``` 
        * 4XX
            * 400 
             ```json
             {
                 "message": "email이 유효하지 않습니다."
             }
             ```
### 인증
1. POST 로그인

   * url

     ```
     POST {BASE_URL}/api/auth/login
     ```

   * Request

     ```json
     {
         "email": "test1234@test.com",
         "password": "testpassword12"
     }
     ```

   * Response

     * 2XX

       * 200

         ```json
         {
             "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
             "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMxMjMiLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE1MTYyMzkwMjJ9.DXi8E6qG8SI4Xzwur1JDsjmVtujkcV3cOF2_LIBjkHI"
         }
         ```

         

     * 4XX

       * 400

         ```json
         {
             "message": "email이 유효하지 않습니다."
         }
         ```

         ```json
         {
             "message": "password가 유효하지 않습니다."
         }
         ```

       * 404

         ```json
         {
             "message": "email이 존재하지 않습니다."
         }
         ```

         

       

2. POST 로그아웃

   * url

     ```python
     POST {BASE_URL}/api/auth/logout
     ```

   * Request

     ```json
     {
         "email": "test1234@test.com"
     }
     ```

   * Response

     * 2XX

       * 204

         ```json
         {
             "message": "로그아웃 되었습니다."
         }
         ```

         

     * 4XX

       * 400

         ```json
         {
             "message": "email이 유효하지 않습니다."
         }
         ```

         ```json
         {
             "message": "password가 유효하지 않습니다."
         }
         ```

       * 404

         ```json
         {
             "message": "email이 존재하지 않습니다."
         }
         ```

       

## Contents
### Note
* GET전체 Note List
  * url

    ```
    GET {BASE_URL}/api/notes
    ```

  * Request

    ```python
    GET {BASE_URL}/api/notes?cursor=30
    ```

  * Response

    * 2XX

      ```json
      {
          "next_cursor": 45,
          "notes": [
              {
                  "title": "컴퓨터 네트워크",
                  "status": "NOT_APPROVED",
              },
              {
                  "title": "자료구조",
                  "status": "NOT_APPROVED",
              },
              {
                  "title": "알고리즘",
                  "status": "APPROVED",
              },
              ...
          ]
      }
      ```

* GET 메인화면 기타 정보

  * url

    ```
    GET {BASE_URL}/api/notes/other-info
    ```

  * Request

  * Response

    * 2XX

      * 200

        ```json
        {
            "not_approved_issues": [
              {
                  "title": "운영체제",
              },
              {
                  "title": "프로세스는 무엇인가?",
              },
              ...
            ],
            "all_issues_count": 30,
            "approved_issues_count": 16,
            "not_approved_issues_count": 14"
        }
        
        ```

* POST Note 추가하기

  * url

    ```
    header: Bearer {JWT_TOKEN}
    POST {BASE_URL}/api/notes
    ```

  * Request

    ```json
    {
        "title": "운영체제",
        "request_contents": "운영체제 노트가 없네요 추가 요청 합니다:)"
    }
    ```

  * Response

    * 2XX

      * 201

        ```json
        {}
        ```

    * 4XX

      * 400

        ```json
        {
            "message": "타이틀과 요청 내용 설명을 채워주세요."
        }
        ```
### Topic
* CRUD
### Page
* CRUD
### Issue
* 
