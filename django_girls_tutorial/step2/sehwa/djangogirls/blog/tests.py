import json
from http.client import NOT_FOUND, OK

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post, Comment


class TestPostMixin:
    def setUp(self):
        self.author = self._create_author(username="thkwon", password="test_password")

    @staticmethod
    def _create_post(author, title, text):
        return Post.objects.create(author=author, title=title, text=text)

    @staticmethod
    def _create_author(username, password):
        return User.objects.create_superuser(username=username, password=password)

    @staticmethod
    def _create_comment_on_post(post, author, text):
        return Comment.objects.create(post=post, author=author, text=text)


"""띄어쓰기 ㄴㄴ
class TestPostList(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_list_with_count(self):
        for i in range(10):
            post = self._create_post(
                author=self.author, title=f"test title-{i}", text=f"test text-{i}"
            )
            post.publish()
        response = self.client.get(reverse("retrieve_post_list"))
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(len(response_data), 10)

    def test_list_with_published_post(self):
        post = self._create_post(
            author=self.author, title="test title", text="test text"
        )
        post.publish()
        response = self.client.get(reverse("retrieve_post_list"))
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(response_data[0]["title"], "test title")
        self.assertEqual(response_data[0]["text"], "test text")
        self.assertEqual(response_data[0]["author"], self.author.id)

    def test_list_with_no_published_post(self):
        self._create_post(author=self.author, title="test title", text="test text")
        response = self.client.get(reverse("retrieve_post_list"))
        response_data = json.loads(response.content)["posts"]
        self.assertEqual(len(response_data), 0)


class TestPostDetail(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_post_detail(self):
        post = self._create_post(
            author=self.author, title="test title", text="test text"
        )
        post.publish()
        response = self.client.get(reverse("retrieve_post_detail", kwargs={"id": 1}))
        response_data = json.loads(response.content)["post"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["author"], self.author.id)
        self.assertEqual(response_data["title"], "test title")
        self.assertEqual(response_data["text"], "test text")

    def test_post_detail_on_error_with_404_not_found(self):
        response = self.client.get(reverse("retrieve_post_detail", kwargs={"id": 1}))
        response_data = json.loads(response.content)["message"]
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data, "Post를 찾을 수 없습니다")


class TestPostCreate(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_post_create(self):
        # Given: 유효한 request body 값이 주어질 때,
        request_body = {"author": self.author.id, "title": "test title", "text": "test text"}

        # When: post 생성 api를 호출하면,
        response = self.client.post(reverse("create_post"), data=request_body)

        # Then: 상태코드는 201 이고, Post의 개수는 1개이다
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.all().count(), 1)
        # And: 응답 값에서 생성된 post의 title과 text를 리턴한다
        response = json.loads(response.content)["post"]
        self.assertEqual(response["title"], "test title")
        self.assertEqual(response["text"], "test text")

    def test_post_create_with_error_on_404(self):
        # Given: 유효하지 않은 author_id가 주어질 때,
        invalid_author_id = 123123123
        request_body = {"author": invalid_author_id, "title": "test title", "text": "test text"}

        # When: post 생성 api를 호출하면,
        response = self.client.post(reverse("create_post"), data=request_body)

        # Then: 상태코드는 404이고, Post의 개수는 0개이다.
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Post.objects.all().count(), 0)
        # And: 응답 값으로 "author를 찾을 수 없습니다."를 리턴한다
        response = json.loads(response.content)
        self.assertEqual(response["message"], "author를 찾을 수 없습니다.")


class TestPostUpdate(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(author=self.author, title="test title", text="test text")

    def test_post_update_with_put(self):
        # Given: 업데이트 하기 위한 유효한 request body 값이 주어지고,
        request_body_for_put_update = json.dumps({"author": self.author.id, "title": "test test title", "text": "test test text"})

        # When: 1번 post에 대한 업데이트 api를 호출 할 때,
        response = self.client.put(reverse("update_post_with_put", kwargs={"id": self.post.id}), data=request_body_for_put_update)

        # Then: 상태코드는 200이고,
        self.assertEqual(response.status_code, 200)
        # And: 실제 post는 변경되어야 한다
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test test title")
        self.assertEqual(post.text, "test test text")
        # And: 응답 값에서도 변경된 것을 확인할 수 있다
        response = json.loads(response.content)["post"]
        self.assertEqual(response["title"], "test test title")
        self.assertEqual(response["text"], "test test text")


    def test_post_update_with_error_with_author_on_404(self):
        # Given: 업데이트 하기 위한 유효하지 않은 author_id 값이 주어지고,
        invalid_author_id = 123123123
        request_body_for_put_update = json.dumps(
            {"author": invalid_author_id, "title": "test test title", "text": "test test text"})

        # When: 1번 post에 대한 업데이트 api를 호출 할 때,
        response = self.client.put(reverse("update_post_with_put", kwargs={"id": self.post.id}), data=request_body_for_put_update)

        # Then: 상태코드는 404이고,
        self.assertEqual(response.status_code, 404)
        # And: 실제 post는 변경 되지 않아야 한다
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test title")
        self.assertEqual(post.text, "test text")
        # And: 응답 메세지로 author를 찾을 수 없습니다. 를 리턴 해야 한다.
        response = json.loads(response.content)
        self.assertEqual(response["message"], "author를 찾을 수 없습니다.")

    def test_post_update_with_error_with_post_on_404(self):
        # Given: 업데이트 하기 위한 유효하지 않은 post_id 값이 주어지고,
        request_body_for_put_update = json.dumps(
            {"author": self.author.id, "title": "test test title", "text": "test test text"})
        invalid_post_id = 12345

        # When: # When: 유효하지 않은 post에 대한 업데이트 api를 호출 할 때,
        response = self.client.put(reverse("update_post_with_put", kwargs={"id": invalid_post_id}), data=request_body_for_put_update)

        # Then: 상태코드는 404이고,
        self.assertEqual(response.status_code, 404)
        # And: 실제 post는 변경 되지 않아야 한다
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test title")
        self.assertEqual(post.text, "test text")
        response = json.loads(response.content)
        # And: 응답 메세지로 post를 찾을 수 없습니다. 를 리턴 해야 한다.
        self.assertEqual(response["message"], "post를 찾을 수 없습니다.")


class TestPostDelete(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(author=self.author, title="test title", text="test text")

    def test_delete_post(self):
        # Given: 테스트 위한 post id와 author id를 body에 담는다.
        request_body = json.dumps({"author": self.author.id})
        post_id = self.post.id

        # When: delete_post api 실행.
        response = self.client.delete(
            reverse("delete_post", kwargs={"id": post_id}), data=request_body
        )

        # Then: 실행 결과 상태코드 200 return.
        self.assertEqual(response.status_code, 200)

        # And: 기존의 post는 삭제 되어야 한다.
        self.assertQuerysetEqual(Post.objects.all(), [])

    def test_delete_post_with_invalid_post_id(self):
        # Given: 유효하지 않은 post id, 정상적인 author id
        request_body = json.dumps({"author": self.author.id})
        invalid_post_id = 9999999

        # When: delete_post api 실행.
        response = self.client.delete(
            reverse("delete_post", kwargs={"id": invalid_post_id}), data=request_body
        )

        # Then: 실행결과 상태코드 403 여야 한다.
        self.assertEqual(response.status_code, 403)

        # And: post가 삭제되지 않아야 한다.
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test title")
        self.assertEqual(post.text, "test text")

        # And: 응답 메세지가 post를 찾을 수 없습니다. 여야 한다.
        response = json.loads(response.content)
        self.assertEqual(response["message"], "post를 찾을 수 없습니다.")

    def test_delete_post_with_invalid_author_id(self):
        # Given: 정상적인 post id, 유효하지 않은 author id
        invalid_author_id = 99999
        invalid_request_body = json.dumps({"author": invalid_author_id})
        post_id = self.post.id

        # When: delete_post api 실행.
        response = self.client.delete(
            reverse("delete_post", kwargs={"id": post_id}), data=invalid_request_body
        )
        # Then: 실행결과 상태코드 404 여야 한다.
        self.assertEqual(response.status_code, 404)

        # And: post가 삭제되지 않아야 한다.
        post = Post.objects.all()[0]
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.title, "test title")
        self.assertEqual(post.text, "test text")

        # And: 응답 메세지가 유효하지 않은 사용자 id입니다. 여야 한다.
        response = json.loads(response.content)
        self.assertEqual(response["message"], "유효하지 않은 사용자 id입니다.")
"""


class TestCommentList(TestPostMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.post = self._create_post(self.author, "test", "test text")

    def test_comment_list_on_valid_post_with_comment_count_(self):
        # Given: 정상적으로 생성된 comment 10개, 올바른 post id
        post_id = self.post.id
        comment_count = 10
        for i in range(comment_count):
            comment = self._create_comment_on_post(self.post, f"author{i}", f"comment{i}")
            comment.approve()

        # When: retrieve_comment_list api 실행
        response = self.client.get(reverse("retrieve_comment_list", kwargs={"post_id": post_id}))

        # Then: 실행결과 200, 댓글 갯수 10개여야 함.
        response = json.loads(response.content)
        self.assertEqual(comment_count, len(response["data"]))
