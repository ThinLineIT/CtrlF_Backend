from django.db import models
from django.db.models.fields import CharField, DateTimeField, TextField


class Note(models.Model):
    title = CharField(max_length=50)
    create_date = DateTimeField(auto_now_add=True)
    modify_date = DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Topic(models.Model):
    title = CharField(max_length=50)
    note_id = models.ForeignKey("Note", on_delete=models.CASCADE)
    create_date = DateTimeField(auto_now_add=True)
    modify_date = DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Page(models.Model):
    title = CharField(max_length=50)
    note_id = models.ForeignKey("Note", on_delete=models.CASCADE)
    topic_id = models.ForeignKey("Topic", on_delete=models.CASCADE)
    content = TextField()
    create_date = DateTimeField(auto_now_add=True)
    modify_date = DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Issue(models.Model):
    title = CharField(max_length=50)
    note_id = models.ForeignKey("Note", on_delete=models.CASCADE)
    topic_id = models.ForeignKey("Topic", on_delete=models.CASCADE)
    content = TextField()
    registration_date = DateTimeField(auto_now_add=True)
    modify_date = DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
