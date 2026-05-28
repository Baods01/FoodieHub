from typing import Optional
from models.users import Users
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
        main_shop_id: Optional[int] = None,
    ) -> Optional[EditRequestResponse]:
        obj = await EditRequestDAO.get_by_id(request_id)
        if not obj or obj.status != "pending":
            return None

        proposed = obj.proposed_data or {}

        # 重复店铺反馈：审批时执行合并
        if proposed.get("type") == "merge" and main_shop_id is not None:
            from services.shop_service import ShopService
            candidate_ids = proposed.get("candidate_shop_ids", [])
            all_ids = set(candidate_ids)
            all_ids.add(obj.shop_id)
            all_ids.discard(main_shop_id)
            if all_ids:
                await ShopService.merge_shops(main_shop_id, list(all_ids))

        obj = await EditRequestDAO.approve(request_id, admin_id)
        admin = await Users.get_or_none(id=admin_id)
        await LogDAO.log(
            action="approve_edit_request",
            operator=admin,
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
        admin = await Users.get_or_none(id=admin_id)
        await LogDAO.log(
            action="reject_edit_request",
            operator=admin,
            target_type="shop_edit_request",
            target_id=request_id,
        )
        return EditRequestResponse(
            id=obj.id, shop_id=obj.shop_id, user_id=obj.user_id,
            proposed_data=obj.proposed_data, status=obj.status,
            admin_id=obj.admin_id,
            created_at=obj.created_at, updated_at=obj.updated_at,
        )
