# Django girls tutorial 을 완성 해보자

> 1. https://tutorial.djangogirls.org/ko/ -> 기본
> 2. https://tutorial-extensions.djangogirls.org/ko -> 심화

## 목적
* Django를 한번도 다루어본적이 없는 사람을 위한 워밍업 차원에서 진행

## TODO

### STEP 1
* django girls tutorial 완성 -> django template 이용
* 결과물 -> pythonanywhere에 배포된 url

### STEP 2
* django girls tutorial을 SPA 형태로 변경 -> JSON 통신하는 REST API 형태로 변경
* django template 구현 부분을 jquery를 이용해서 변경

### STEP 3
* STEP2에 완성된 부분을 DRF(django rest framework)를 이용해서 변경

## 제약 조건
1. python version -> 3.9
2. django version -> 3 버젼 이상
3. STEP1 까지는 main branch에 자유롭게 commit 가능(but, 가능하다면 feature branch를 나눠서 작업하도록)
4. STEP2 부터는 아래 제약이 추가된다.
    * poetry를 통한 패키지 관리
    * branch 룰 추가(추후 공지)
    * pre-commit 추가 - commit 할 때마다 아래 라이브러리 검사가 자동실행 됨
        * black
        * isort
        * mypy
    * 테스트 코드가 없으면 코드리뷰 통과할 수 없
    * github actions(CI) 추가
        * 작성한 모든 테스트 코드가 통과 해야 함
    * PR을 통한 merge 만 가능 with Code Review 통과해야 함
    

## 참고
* 기획서 분석 및 API에 대한 기본적인 요청/응답 정의가 끝나기 전까지는 django girls tutorial을 통해 각 개인이 django와 python에 익숙해지길 기대함
* 위 과정은 약 3주, 길면 4주 정도로 보고 있고 이 과정 없이 바로 프로젝트를 하는 것은 계란으로 바위치기라고 생각하여 추가함
* 위 과정 중에 STEP1은 가볍게 완성해보는 것을 목표로 하나 STEP2 부터는 빡세게 제약 조건들이 추가 됨. 제약 중에서 신경써야할 부분은 테스트 코드와, branch룰, 코드리뷰 이고, 나머지는 멘토가
 알아서 구축해 놓을 예정
* 잘 모르겠는 것은 언제든지 질문 가능(But, 최소한 공식문서와 Stackoverflow를 꼭 찾아보았으면 좋겠고, 질문의 대한 답변은 아마도 공식문서, Stackoverflow 링크로 제공될 것임 - 
왠만하면 거기에 다있어서..)
* 질문은 github issue에 정리해서 올려주고, slack에서 멘토를 반드시 멘션 해주길 - 안해주면 질문했는지 안했는지를 모름..
* 코드리뷰는 나만 하는게 아니고 전체가 다 할 예정이고, 누구든 질문과 의견을 낼 수 있음 처음에 적응이 안되겠지만 이걸하는 중에 적응 될 것으로 기대함
