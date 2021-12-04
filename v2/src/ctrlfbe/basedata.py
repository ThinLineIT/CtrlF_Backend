from .models import CtrlfActionType, CtrlfContentType, CtrlfIssueStatus


class BaseData:
    def __init__(self):
        pass

    def build_data(self, request, ctrlf_user):
        model_data = {
            "title": request.data["title"],
            "owners": [ctrlf_user.id],
        }
        issue_data = {
            "owner": ctrlf_user.id,
            "title": request.data["title"],
            "reason": request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "action": CtrlfActionType.CREATE,
        }
        return model_data, issue_data


class NoteData(BaseData):
    def __init__(self):
        super().__init__()

    def build_data(self, request, ctrlf_user):
        note_data, issue_data = super(NoteData, self).build_data(request, ctrlf_user)
        issue_data["related_model_type"] = CtrlfContentType.NOTE

        return note_data, issue_data


class TopicData(BaseData):
    def __init__(self):
        super().__init__()

    def build_data(self, request, ctrlf_user):
        topic_data, issue_data = super(TopicData, self).build_data(request, ctrlf_user)
        topic_data["note"] = request.data["note_id"]
        issue_data["related_model_type"] = CtrlfContentType.TOPIC

        return topic_data, issue_data


class PageData(BaseData):
    def __init__(self):
        super().__init__()

    def build_data(self, request, ctrlf_user):
        page_data, issue_data = super(PageData, self).build_data(request, ctrlf_user)
        page_data["topic"] = request.data["topic_id"]
        page_data["content"] = request.data["content"]
        issue_data["related_model_type"] = CtrlfContentType.PAGE
        return page_data, issue_data
