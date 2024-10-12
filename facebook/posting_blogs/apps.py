from django.apps import AppConfig


class PostingBlogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posting_blogs'

    def ready(self):
        import posting_blogs.signals

