from typing import Optional
from dao.edit_request_dao import EditRequestDAO
from dao.log_dao import LogDAO
from schemas.governance import EditRequestResponse, EditRequestListResponse


class GovernanceService:
    """治理（勘误/重复反馈）业务逻辑"""

    @staticmethod
    async def create_edit_request(
        shop_id: int,
        user_id: int,
        proposed_data: dict,
    ) -> EditRequestResponse:
        obj = await EditRequestDAO.create(shop_id, user_id, proposed_data)
        return EditRequestResponse(
            id=obj.id, shop_id=obj.shop_id, user_id=obj.user_id,
            proposed_data=obj.proposed_data, status=obj.status,
            admin_id=None, created_at=obj.created_at, updated_at=obj.updated_at,
        )

    @staticmethod
    async def list_edit_requests(
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> EditRequestListResponse:
        result = await EditRequestDAO.list(
            status=status, user_id=user_id, shop_id=shop_id,
            page=page, page_size=page_size,
        )
        return EditRequestListResponse(**result)

    @staticmethod
    async def approve_edit_request(
        request_id: int,
        admin_id: int,
    ) -> Optional[EditRequestResponse]:
        obj = await EditRequestDAO.approve(request_id, admin_id)
        if not obj:
            return None
        await LogDAO.log(
            action="approve_edit_request",
            operator_id=admin_id,
            target_type="shop_edit_request",
            target_id=request_id,
        )
        return EditRequestResponse(
            id=obj.id, shop_id=obj.shop_id, user_id=obj.user_id,
            proposed_data=obj.proposed_data, status=obj.status,
            admin_id=obj.admin_id,
            created_at=obj.created_at, updated_at=obj.updated_at,
        )

    @staticmethod
    async def reject_edit_request(
        request_id: int,
        admin_id: int,
    ) -> Optional[EditRequestResponse]:
        obj = await EditRequestDAO.reject(request_id, admin_id)
        if not obj:
            return None
        await LogDAO.log(
            action="reject_edit_request",
            operator_id=admin_id,
            target_type="shop_edit_request",
            target_id=request_id,
        )
        return EditRequestResponse(
            id=obj.id, shop_id=obj.shop_id, user_id=obj.user_id,
            proposed_data=obj.proposed_data, status=obj.status,
            admin_id=obj.admin_id,
            created_at=obj.created_at, updated_at=obj.updated_at,
        )
