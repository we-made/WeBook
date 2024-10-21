from typing import List, Optional, Type
import django
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Router, File
from ninja.files import UploadedFile
from webook.api.schemas.base_schema import BaseSchema
from webook.api.schemas.operation_result_schema import (
    OperationResultSchema,
    OperationResultStatus,
    OperationType,
)
from webook.arrangement.api.mixin_routers.base_mixin_router import BaseMixinRouter
from webook.arrangement.api.routers.person_router import PersonGetSchema
from webook.arrangement.models import BaseFileRelAbstractModel, Person
from ninja.errors import HttpError


class FileSchema(BaseSchema):
    # associated_with: str
    id: Optional[int]
    filename: str
    uploader: PersonGetSchema
    url: str


class UploadFileSchema(BaseSchema):
    files: list


class UploadFileResponseSchema(BaseSchema):
    files: list


class FileMixinRouter(BaseMixinRouter):
    file_model: Type[BaseFileRelAbstractModel] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self.model, "files"):
            raise HttpError(status_code=500, message="Model does not have files")

        self.add_api_operation(
            path="/files/upload",
            methods=["POST"],
            view_func=self.FileFunctionality.get_upload_func(router_instance=self),
            response=List[OperationResultSchema[FileSchema]],
            operation_id="upload_file_to_" + self.model_name_singular.lower(),
            summary="Upload a file",
            description=f"Upload a file to the {self.model_name_singular.lower()} entity",
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

        self.add_api_operation(
            path="/files/delete",
            methods=["DELETE"],
            view_func=self.FileFunctionality.get_delete_func(router_instance=self),
            operation_id="delete_file_from_" + self.model_name_singular.lower(),
            summary="Delete a file from the " + self.model_name_singular.lower(),
            description=f"Delete a file from the {self.model_name_singular.lower()} entity",
            response=OperationResultSchema[FileSchema],
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

        self.add_api_operation(
            path="/files/list",
            methods=["GET"],
            view_func=self.FileFunctionality.get_list_func(router_instance=self),
            operation_id="list_files_of_" + self.model_name_singular.lower(),
            summary="List files",
            description=f"List all files associated with the {self.model_name_singular.lower()} entity",
            response=List[FileSchema],
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

        self.add_api_operation(
            path="/files/download",
            methods=["GET"],
            view_func=self.FileFunctionality.get_download_func(router_instance=self),
            operation_id="download_file_from_" + self.model_name_singular.lower(),
            summary="Download a file",
            description=f"Download a file from the {self.model_name_singular.lower()} entity",
            response=None,
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

    class FileFunctionality:
        """Functionality for the FileMixinRouter."""

        def _convert_base_entity_to_file_schema(
            file_instance: BaseFileRelAbstractModel,
        ):
            return FileSchema(
                id=file_instance.id,
                # associated_with=file_instance.associated_w,
                filename=file_instance.file.name,
                uploader=file_instance.uploader,
                url=file_instance.file.url,
            )

        def get_upload_func(router_instance: "FileMixinRouter"):
            def upload_func(
                request, parent_id: int, files: List[UploadedFile] = None
            ) -> List[OperationResultSchema[FileSchema]]:
                parent_instance: Type[django.db.models.Model] = (
                    router_instance._get_base_entity_or_404(parent_id)
                )
                uploading_person: Person = router_instance._get_user_person(request)

                uploaded_files = []
                for file in files:
                    file_instance = router_instance.file_model(
                        file=file,
                        uploader=uploading_person,
                        associated_with=parent_instance,
                    )
                    file_instance.save()
                    uploaded_files.append(file_instance)

                return [
                    OperationResultSchema[FileSchema](
                        operation=OperationType.CREATE,
                        status=OperationResultStatus.SUCCESS,
                        message="File uploaded successfully",
                        data=FileMixinRouter.FileFunctionality._convert_base_entity_to_file_schema(
                            file_instance
                        ),
                    )
                    for file_instance in uploaded_files
                ]

            upload_func.__name__ = "upload_file"
            upload_func.__annotations__ = {
                "parent_id": int,
                "files": List[UploadedFile],
                "response": List[OperationResultSchema[FileSchema]],
            }

            upload_func.__doc__ = (
                "Upload a file to " + router_instance.model_name_singular.lower()
            )

            return upload_func

        def get_delete_func(router_instance: "FileMixinRouter"):
            def delete_func(
                request, parent_id: int, file_id: int
            ) -> OperationResultSchema[FileSchema]:
                parent_instance: Type[django.db.models.Model] = (
                    router_instance._get_base_entity_or_404(parent_id)
                )
                file_instance: Type[BaseFileRelAbstractModel] = get_object_or_404(
                    parent_instance.files, id=file_id
                )

                if file_instance is None:
                    raise Http404("File does not exist")

                file_instance.delete()

                return OperationResultSchema[FileSchema](
                    operation=OperationType.DELETE,
                    status=OperationResultStatus.SUCCESS,
                    message="File deleted successfully",
                    data=FileMixinRouter.FileFunctionality._convert_base_entity_to_file_schema(
                        file_instance
                    ),
                )

            delete_func.__name__ = "delete_file"
            delete_func.__annotations__ = {
                "parent_id": int,
                "file_id": int,
                "response": OperationResultSchema[FileSchema],
            }

            delete_func.__doc__ = (
                "Delete a file from " + router_instance.model_name_singular.lower()
            )

            return delete_func

        def get_list_func(router_instance: "FileMixinRouter"):
            def list_func(request, parent_id: int) -> List[FileSchema]:
                parent_instance: Type[django.db.models.Model] = (
                    router_instance._get_base_entity_or_404(parent_id)
                )

                return [
                    FileMixinRouter.FileFunctionality._convert_base_entity_to_file_schema(
                        file_instance
                    )
                    for file_instance in parent_instance.files.all()
                ]

            list_func.__name__ = "list_files"
            list_func.__annotations__ = {
                "parent_id": int,
                "response": List[FileSchema],
            }

            list_func.__doc__ = (
                "List all files associated with "
                + router_instance.model_name_singular.lower()
            )

            return list_func

        def get_download_func(router_instance: "FileMixinRouter"):
            def download_func(
                request, parent_id: int, file_id: int
            ) -> List[FileSchema]:
                parent_instance: Type[django.db.models.Model] = (
                    router_instance._get_base_entity_or_404(parent_id)
                )

                file_instance: Type[BaseFileRelAbstractModel] = get_object_or_404(
                    parent_instance.files, id=file_id
                )

                if file_instance is None:
                    raise Http404("File does not exist")

                with open(file_instance.file.path, "rb") as f:
                    response = HttpResponse(
                        f.read(), content_type="application/octet-stream"
                    )
                    response["Content-Disposition"] = (
                        f"attachment; filename={file_instance.file.name}"
                    )
                    return response

            download_func.__name__ = "download_file"
            download_func.__annotations__ = {
                "parent_id": int,
                "file_id": int,
                "response": HttpResponse,
            }

            download_func.__doc__ = (
                "Download a file from " + router_instance.model_name_singular.lower()
            )

            return download_func
