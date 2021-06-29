# 2021/06/27

### 0. Django 시작
* pyenv를 이용한 python 3.9.5 설치
* Setting.py에서 Server의 설정 저장.
* manage.py 에서 sqlite migration과 Server run.

# 2021/06/28

### 1. Django Model
1. Model 정의 후 `python manange.py makemigrations {App이름}`
2. DB에 Model 추가 `python manage.py migrate {App이름}`
3. admin 계정 추가 후 pythonanywhere에 복제.
4. pythonanywhere의 bash console에서 project git repo를 clone 후 내 branch에서 가져옴.
5. 새 가상환경 설정. WSGI Protocol 설정.
* http://jrhong95.pythonanywhere.com

### 2. Django urls
1. `/admin` url은 `mysite/urls.py`의 `urlpatterns`에 있다.
2. 메인에 blog 글을 보여주기 위해 `""`일 때의 동작을 `blog.urls`로 변경
3. `blog/urls.py`에 `./views.py`의 `post_list`를 연결.
4. 템플릿은 곧 템플릿 파일을 만든다는 것.
    - 정보를 일정한 형태로 표현하기 위한 재사용 가능한 파일
    - MVC 패턴으로 치면 `views.py`는 controller, `template`은 view라고 생각할 수 있음.
        >http://pythonstudy.xyz/python/article/307-Django-템플릿-Template
5. 어우 배고파 http://jrhong95.pythonanywhere.com

# 2021/06/29

### 3. Django templates
1. ORM method
    * `create(속성=내용...)` : 새 내용들을 table로 넣음
    * `all()`: 모든 내용 read
    * `filter(속성__제약조건...)`: 검색
    * `order_by(속성)`: 정렬

2. `views.py`에서 데이터 불러오기
    * vscode에서 오류 출력해서 설정 추가
    ```json
    "python.linting.pylintArgs": [ 
        "--load-plugins=pylint_django", 
        "--disable=django-not-configured"
    ]
    ```
    * 템플릿 안에 있는 값 추가하려면 `{{ posts }}`

3. 장고템플릿 사용법 알아봄.
4. 배포 http://jrhong95.pythonanywhere.com