# STEP3

* 여태까지 개발한 내용들은 DRF로 개발을 해보자.
    * 조건
        1. APIView를 이용해서 개발을 하자. 이외는 자유롭게 선택해도 됨
        2. STEP3 부터는 pre-commit(black, isort, flake8)과 poetry, github actions이 추가되면서, 코드 작성시 strict 한 것들이 많이 추가 되었음
        3. Rule
            3. branch rule
                * {th|sh|jh|jg}-{issue number}-your-branch-name
                * ex) 내가 작업해야할 Issue가 13번이라면,
                    * `th-13-add-post-list-in-drf`
            4. commit rule
                * {TH|SH|JH|JG}-{issue number} {your commit}
                * ex)
                    1. TH-13 add post list view
                    2. TH-13 refactor post list view
                3. ...
            5. PR title rule(prlint)
                * {TH|SH|JH|JG}-{issue number} {PR title}
                * ex)
                    1. TH-13 add post list in drf
                    2. TH-13 add login api

 * 구현 순서 -> 각 기능 마다 branch를 따로 만들기 바람
    1. post list
    2. post detail
    3. post create
    4. post update
    5. post delete
    6. comment list
    7. comment create
    8. comment update
    9. comment delete

 * 해야할 것 정리
    1. poetry 설치
    3. poetry install --no-root -> poetry로 파이썬 라이브러리 패키지 설치(pip 대체)
    4. 내가 작업할 이슈 생성(ex) post list)
        * github Issue 생성 -> 생성된 이슈번호가 20 일 때,
    5. legacy branch로 checkout
    6. 작업 브랜치 생성 ex) git checkout -b sh-20-add-post-list-api-in-drf
    7. 코드 작업 후 commit + 테스트 코드는 필수
        * 이때, pre-commit이 동작하면서 isort, black, flake8, mypy를 자동으로 검사
        * 위 검사를 모두 통과해서 commit 할 수 있음
    8. commit이 완료되면 push 후 PR 생성
    9. 내 PR에서 github actions가 제대로 돌았는지 확인

 * 주의 사항
    1. 아마도 poetry 설치하고, 패키지 설치하는 것부터 난항이 예상됨 -> 문서 잘 읽어보고 해보도록
    2. 이전에는 자유롭게 commit 했지만, step3 부터는 이것저것 검사를 많이 하게됨 -> 불편하다고 느낄 수 있고, 에러고치는게 짜증날 수 있음(그러나 적응해야함)
    3. commit 뿐 아니라, PR title, branch rule 등 여러가지 제약을 많이 걸어두었으니, 여기에 익숙해 지길 바람
