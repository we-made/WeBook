from typing import Any, Dict
from uuid import uuid4

from django.views import View

UNNAMED_DIALOG_NAME = "Dialog"


class DialogView(View):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.method == "GET":
            if "managerName" in self.request.GET:
                context["managerName"] = self.request.GET.get("managerName")
            else:
                raise Exception("Must specify a managerName")

            if "dialogId" in self.request.GET:
                context["dialogId"] = self.request.GET.get("dialogId")
            else:
                raise Exception("Must specify a dialogId")

            context["title"] = self.request.GET.get(
                "title",
                default=(
                    self.dialog_title
                    if hasattr(self, "dialog_title")
                    else UNNAMED_DIALOG_NAME
                ),
            )

            context["discriminator"] = uuid4()

        return context
