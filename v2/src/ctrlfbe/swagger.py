from ctrlfbe.serializers import (
    ImageSerializer,
    ImageUploadRequestBodySerializer,
    IssueApproveRequestBodySerializer,
    IssueApproveResponseSerializer,
    IssueDetailSerializer,
    IssueListQuerySerializer,
    IssueSerializer,
    NoteCreateRequestBodySerializer,
    NoteListQuerySerializer,
    NoteSerializer,
    PageCreateRequestBodySerializer,
    PageListSerializer,
    PageSerializer,
    TopicCreateRequestBodySerializer,
    TopicSerializer,
)

SWAGGER_PAGE_LIST_VIEW = {
    "responses": {200: PageListSerializer(many=True)},
    "operation_summary": "Page List API",
    "operation_description": "topic_id에 해당하는 page들의 list를 리턴해줍니다",
    "tags": ["디테일 화면"],
}

SWAGGER_TOPIC_LIST_VIEW = {
    "responses": {200: TopicSerializer(many=True)},
    "operation_summary": "Topic List API",
    "operation_description": "note_id에 해당하는 topic들의 list를 리턴해줍니다",
    "tags": ["디테일 화면"],
}

SWAGGER_NOTE_DETAIL_VIEW = {
    "responses": {200: NoteSerializer()},
    "operation_summary": "Note Detail API",
    "operation_description": "note_id에 해당하는 Note의 상세 내용을 리턴합니다",
    "tags": ["디테일 화면"],
}

SWAGGER_NOTE_LIST_VIEW = {
    "query_serializer": NoteListQuerySerializer,
    "operation_summary": "Note List API",
    "operation_description": "Cursor based pagination 처리된 Note List를 리턴 합니다",
    "tags": ["메인 화면"],
}

SWAGGER_NOTE_CREATE_VIEW = {
    "operation_summary": "Note Create API",
    "operation_description": "비활성화된 Note와 이슈를 생성 합니다.",
    "request_body": NoteCreateRequestBodySerializer,
    "tags": ["디테일 화면"],
}

SWAGGER_TOPIC_CREATE_VIEW = {
    "operation_summary": "Topic Create API",
    "operation_description": "비활성화된 Topic과 이슈를 생성 합니다.",
    "request_body": TopicCreateRequestBodySerializer,
    "tags": ["디테일 화면"],
}

SWAGGER_PAGE_CREATE_VIEW = {
    "operation_summary": "Page Create API",
    "operation_description": "비활성화된 Page와 이슈를 생성 합니다.",
    "request_body": PageCreateRequestBodySerializer,
    "tags": ["디테일 화면"],
}

SWAGGER_TOPIC_DETAIL_VIEW = {
    "responses": {200: TopicSerializer()},
    "operation_summary": "Topic Detail API",
    "operation_description": "topic_id에 해당하는 Topic의 상세 내용을 리턴합니다",
    "tags": ["디테일 화면"],
}

SWAGGER_PAGE_DETAIL_VIEW = {
    "responses": {200: PageSerializer()},
    "operation_summary": "Page Detail API",
    "operation_description": "page_id에 해당하는 Page의 상세 내용을 리턴합니다",
    "tags": ["디테일 화면"],
}

SWAGGER_ISSUE_LIST_VIEW = {
    "query_serializer": IssueListQuerySerializer,
    "responses": {200: IssueSerializer(many=True)},
    "operation_summary": "Issue List API",
    "operation_description": "Cursor based pagination 처리된 Issue List를 리턴 합니다",
    "tags": ["이슈 화면"],
}

SWAGGER_ISSUE_DETAIL_VIEW = {
    "responses": {200: IssueDetailSerializer()},
    "operation_summary": "Issue Detail API",
    "operation_description": "issue_id에 해당하는 Issue의 상세 내용을 리턴합니다",
    "tags": ["이슈 화면"],
}

SWAGGER_ISSUE_APPROVE_VIEW = {
    "responses": {
        200: IssueApproveResponseSerializer(),
        400: IssueApproveResponseSerializer(),
        401: IssueApproveResponseSerializer(),
    },
    "request_body": IssueApproveRequestBodySerializer(),
    "operation_summary": "Issue Approve API",
    "operation_description": "issue_id에 해당하는 Issue의 content(Note or Topic or Page)를 승인 합니다",
    "tags": ["이슈 화면", "디테일 화면"],
}

SWAGGER_IMAGE_UPLOAD_VIEW = {
    "operation_summary": "Image Upload API",
    "operation_description": "Page content의 이미지를 aws s3에 업로드합니다.",
    "tags": ["디테일 화면"],
    "request_body": ImageUploadRequestBodySerializer(),
    "responses": {200: ImageSerializer()},
}
