from django.urls import reverse_lazy


class CrudContextMixin:
    page_title: str = ""
    page_subtitle: str = ""
    list_url_name: str = ""
    create_url_name: str = ""
    update_url_name: str = ""
    delete_url_name: str = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("page_title", self.page_title)
        ctx.setdefault("page_subtitle", self.page_subtitle)
        if self.list_url_name:
            ctx.setdefault("list_url", reverse_lazy(self.list_url_name))
            ctx.setdefault("cancel_url", reverse_lazy(self.list_url_name))
        if self.create_url_name:
            ctx.setdefault("create_url", reverse_lazy(self.create_url_name))
        obj = getattr(self, "object", None)
        if obj and getattr(obj, "pk", None):
            if self.update_url_name:
                ctx.setdefault(
                    "update_url",
                    reverse_lazy(self.update_url_name, kwargs={"pk": obj.pk}),
                )
            if self.delete_url_name:
                ctx.setdefault(
                    "delete_url",
                    reverse_lazy(self.delete_url_name, kwargs={"pk": obj.pk}),
                )
            ctx.setdefault(
                "object_fields",
                [
                    (field.verbose_name, getattr(obj, field.name))
                    for field in obj._meta.fields  # noqa: SLF001
                ],
            )
        return ctx
