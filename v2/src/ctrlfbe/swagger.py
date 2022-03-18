from ctrlfbe.serializers import (
    ImageSerializer,
    ImageUploadRequestBodySerializer,
    IssueActionRequestBodySerializer,
    IssueActionResponseSerializer,
    IssueCountSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    IssueUpdateActionRequestBodySerializer,
    IssueUpdatePermissionCheckRequestBodySerializer,
    IssueUpdatePermissionCheckResponseSerializer,
    NoteCreateRequestBodySerializer,
    NoteDeleteRequestBodySerializer,
    NoteDeleteResponseSerializer,
    NoteSerializer,
    NoteUpdateRequestBodySerializer,
    NoteUpdateResponseSerializer,
    PageCreateRequestBodySerializer,
    PageDeleteRequestBodySerializer,
    PageDeleteResponseSerializer,
    PageDetailQuerySerializer,
    PageDetailSerializer,
    PageListSerializer,
    PageUpdateRequestBodySerializer,
    TopicCreateRequestBodySerializer,
    TopicDeleteRequestBodySerializer,
    TopicDeleteResponseSerializer,
    TopicSerializer,
    TopicUpdateRequestBodySerializer,
    TopicUpdateResponseSerializer,
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
    "responses": {200: NoteSerializer(many=True)},
    "operation_summary": "Note List API",
    "operation_description": "Cursor based pagination 처리된 Note List를 리턴 합니다",
    "tags": ["메인 화면"],
}
SWAGGER_ISSUE_COUNT = {
    "responses": {200: IssueCountSerializer()},
    "operation_summary": "Issue Count API",
    "operation_description": "모든 이슈 개수를 리턴합니다.",
    "tags": ["메인 화면"],
}

SWAGGER_NOTE_CREATE_VIEW = {
    "operation_summary": "Note Create API",
    "operation_description": "비활성화된 Note와 이슈를 생성 합니다.",
    "request_body": NoteCreateRequestBodySerializer,
    "tags": ["디테일 화면"],
}

SWAGGER_NOTE_UPDATE_VIEW = {
    "responses": {200: NoteUpdateResponseSerializer()},
    "request_body": NoteUpdateRequestBodySerializer(),
    "operation_summary": "Note Update Request API",
    "operation_description": "Note 업데이트를 위한 Issue를 생성합니다.",
    "tags": ["디테일 화면"],
}

SWAGGER_NOTE_DELETE_VIEW = {
    "responses": {200: NoteDeleteResponseSerializer()},
    "request_body": NoteDeleteRequestBodySerializer(),
    "operation_summary": "Note Delete Request API",
    "operation_description": "Note 삭제를 위한 Issue를 생성합니다.",
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

SWAGGER_TOPIC_UPDATE_VIEW = {
    "responses": {200: TopicUpdateResponseSerializer()},
    "request_body": TopicUpdateRequestBodySerializer(),
    "operation_summary": "Topic Update Request API",
    "operation_description": "Topic 업데이트를 위한 Issue를 생성합니다.",
    "tags": ["디테일 화면"],
}

SWAGGER_TOPIC_DELETE_VIEW = {
    "responses": {200: TopicDeleteResponseSerializer()},
    "request_body": TopicDeleteRequestBodySerializer(),
    "operation_summary": "Topic Delete Request API",
    "operation_description": "Topic 삭제를 위한 Issue를 생성합니다.",
    "tags": ["디테일 화면"],
}

SWAGGER_PAGE_DETAIL_VIEW = {
    "responses": {200: PageDetailSerializer()},
    "operation_summary": "Page Detail API",
    "operation_description": "page_id에 해당하는 Page의 상세 내용을 리턴합니다",
    "query_serializer": PageDetailQuerySerializer,
    "tags": ["디테일 화면"],
}

SWAGGER_PAGE_UPDATE_VIEW = {
    "operation_summary": "Page Update Request API",
    "operation_description": "Page 업데이트를 위한 Issue를 생성합니다.",
    "request_body": PageUpdateRequestBodySerializer,
    "tags": ["디테일 화면"],
}

SWAGGER_PAGE_DELETE_VIEW = {
    "operation_summary": "Page Delete Request API",
    "operation_description": "Page 삭제 위한 Issue를 생성합니다.",
    "responses": {200: PageDeleteResponseSerializer()},
    "request_body": PageDeleteRequestBodySerializer,
    "tags": ["디테일 화면"],
}

SWAGGER_ISSUE_LIST_VIEW = {
    "responses": {200: IssueListSerializer(many=True)},
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
        200: IssueActionResponseSerializer(),
        400: IssueActionResponseSerializer(),
        401: IssueActionResponseSerializer(),
    },
    "request_body": IssueActionRequestBodySerializer(),
    "operation_summary": "Issue Approve API",
    "operation_description": "issue_id에 해당하는 Issue의 content(Note or Topic or Page)를 승인 합니다",
    "tags": ["이슈 화면", "디테일 화면"],
}

SWAGGER_ISSUE_DELETE_VIEW = {
    "responses": {
        200: IssueActionResponseSerializer(),
        400: IssueActionResponseSerializer(),
        401: IssueActionResponseSerializer(),
    },
    "request_body": IssueActionRequestBodySerializer(),
    "operation_summary": "Issue Delete API",
    "operation_description": "issue_id에 해당하는 Issue를 삭제 합니다.",
    "tags": ["이슈 화면"],
}

SWAGGER_ISSUE_CLOSE_VIEW = {
    "responses": {
        200: IssueActionResponseSerializer(),
        400: IssueActionResponseSerializer(),
        401: IssueActionResponseSerializer(),
    },
    "request_body": IssueActionRequestBodySerializer(),
    "operation_summary": "Issue Close API",
    "operation_description": "issue_id에 해당하는 Issue의 상태를 Closed로 변경합니다",
    "tags": ["이슈 화면"],
}

SWAGGER_ISSUE_REJECT_VIEW = {
    "responses": {
        200: IssueActionResponseSerializer(),
        400: IssueActionResponseSerializer(),
        401: IssueActionResponseSerializer(),
    },
    "request_body": IssueActionRequestBodySerializer(),
    "operation_summary": "Issue Reject API",
    "operation_description": "issue_id에 해당하는 Issue의 상태를 Rejected로 변경합니다",
    "tags": ["이슈 화면"],
}

SWAGGER_ISSUE_UPDATE_VIEW = {
    "responses": {
        200: IssueActionResponseSerializer(),
        400: IssueActionResponseSerializer(),
        401: IssueActionResponseSerializer(),
    },
    "request_body": IssueUpdateActionRequestBodySerializer(),
    "operation_summary": "Issue Update API",
    "operation_description": "issue_id에 해당하는 Issue의 상태를 Updated로 변경합니다",
    "tags": ["이슈 화면"],
}

SWAGGER_ISSUE_UPDATE_PERMISSION_CHECK = {
    "responses": {
        200: IssueUpdatePermissionCheckResponseSerializer(),
        403: IssueActionResponseSerializer(),
        404: IssueActionResponseSerializer(),
    },
    "request_body": IssueUpdatePermissionCheckRequestBodySerializer(),
    "operation_summary": "Issue Update Permission Check API",
    "operation_description": "issue_id에 해당하는 Issue의 수정 권한을 체크 합니다.",
    "tags": ["이슈 화면"],
}

SWAGGER_IMAGE_UPLOAD_VIEW = {
    "operation_summary": "Image Upload API",
    "operation_description": "Page content의 이미지를 aws s3에 업로드합니다.",
    "tags": ["디테일 화면"],
    "request_body": ImageUploadRequestBodySerializer(),
    "responses": {200: ImageSerializer()},
}

SWAGGER_HEALTH_CHECK_VIEW = {
    "operation_summary": "Health Check API",
    "operation_description": "Health Check API",
    "tags": ["Health Check"],
}
