## STPE2 과제
1. step2/{name}/djangogirls/blog/api/views.py 에 있는 `retrieve_post_list` 를 작성 하여라

JsonResponse의 결과 값은 아래와 같이 나와야 한다
```json
{
  "posts": [
    {
      "title": "test title",
      "text": "test text",
      "author": 1,
      "created_date": "2021-01-01T00:00:00", # 시간 포맷은 다를 수 있음
      "published_date": "2021-01-01T02:00:00", # 시간 포맷은 다를 수 있음
    },
    {
      "title": "test title2",
      "text": "test text2",
      "author": 1,
      "created_date": "2021-01-02T00:00:00", # 시간 포맷은 다를 수 있음
      "published_date": "2021-01-02T03:00:00", # 시간 포맷은 다를 수 있음
    },
    {...},
    ...
  ]
}
```
4. 1번 완료 이후 예정
5. 2번 완료 이후..
6. 3번 완료 이후...

## 참고
* 테스트 돌리는 법
```shell
> python manage.py test
```

* 정상적으로 돌아갔다면, 아래와 같이 나와됨야 
```shell
(py38) ➜  djangogirls git:(main) ✗ python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
EEE
======================================================================

... 이하 생략
```

