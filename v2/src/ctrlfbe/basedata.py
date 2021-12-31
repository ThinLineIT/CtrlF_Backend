from rest_framework.request import Request

from .models import CtrlfActionType, CtrlfContentType, CtrlfIssueStatus


class BaseData:
    request: Request

    def __init__(self, request):
        self.request = request

    def build_create_data(self):
        model_data = {
            "title": self.request.data["title"],
        }
        issue_data = {
            "title": self.request.data["title"],
            "reason": self.request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "action": CtrlfActionType.CREATE,
        }
        return model_data, issue_data

    def build_update_data(self):
        issue_data = {
            "title": self.request.data["new_title"],
            "reason": self.request.data["reason"],
            "status": CtrlfIssueStatus.REQUESTED,
            "action": CtrlfActionType.UPDATE,
        }
        return issue_data


class NoteData(BaseData):
    def build_create_data(self):
        note_data, issue_data = super().build_create_data()
        issue_data["related_model_type"] = CtrlfContentType.NOTE

        return {"model_data": note_data, "issue_data": issue_data}

    def build_update_data(self):
        issue_data = super().build_update_data()
        issue_data["related_model_type"] = CtrlfContentType.NOTE
        return issue_data


class TopicData(BaseData):
    def build_create_data(self):
        topic_data, issue_data = super().build_create_data()
        topic_data["note"] = self.request.data["note_id"]
        issue_data["related_model_type"] = CtrlfContentType.TOPIC

        return {"model_data": topic_data, "issue_data": issue_data}


class PageData(BaseData):
    def build_create_data(self):
        page_data, issue_data = super().build_create_data()
        page_data["topic"] = self.request.data["topic_id"]
        page_data["content"] = self.request.data["content"]
        issue_data["related_model_type"] = CtrlfContentType.PAGE

        return {"model_data": page_data, "issue_data": issue_data}
