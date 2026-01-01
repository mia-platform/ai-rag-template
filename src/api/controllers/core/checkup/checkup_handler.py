from fastapi import APIRouter, status

from src.api.schemas.status_ok_schema import StatusOkResponseSchema

router = APIRouter()


@router.get("/-/check-up", response_model=StatusOkResponseSchema, status_code=status.HTTP_200_OK, tags=["RAG-template"])
async def readiness():
    """
    This route can be used as check-up route, to verify if all the
    functionalities of the service are available or not. The purpose of this
    route should be to check the availability of all the dependencies of the
    service and reply with a check-up of the service. By default, the route will
    always response with an OK status and the 200 HTTP code as soon as the
    service is up.
    """

    return {"statusOk": True}
