from ctrlfbe.serializers import NoteSerializer, PageSerializer, TopicSerializer

SWAGGER_PAGE_LIST_VIEW = {
    "responses": {200: PageSerializer(many=True)},
    "operation_summary": "Page List API",
    "operation_description": "topic_id에 해당하는 page들의 list를 리턴해줍니다",
}

SWAGGER_TOPIC_LIST_VIEW = {
    "responses": {200: TopicSerializer(many=True)},
    "operation_summary": "Topic List API",
    "operation_description": "note_id에 해당하는 topic들의 list를 리턴해줍니다",
}

SWAGGER_NOTE_DETAIL_VIEW = {
    "responses": {200: NoteSerializer()},
    "operation_summary": "Note Detail API",
    "operation_description": "note_id에 해당하는 Note의 상세 내용을 리턴합니다",
}
