from typing import Optional
from models.users import Users
from dao.complaint_dao import ComplaintDAO
from dao.log_dao import LogDAO
from dao.message_dao import MessageDAO
from schemas.complaints import (
    ComplaintCreateRequest, ComplaintResponse, ComplaintListResponse, ComplaintStatsResponse,
)


class ComplaintService:
    """举报业务逻辑"""

    @staticmethod
    async def create(
        user_id: int,
        req: ComplaintCreateRequest,
    ) -> ComplaintResponse:
        obj = await ComplaintDAO.create(
            user_id=user_id,
            complainant_type=req.complainant_type,
            complainant_id=req.complainant_id,
            reason_code=req.reason_code,
            description=req.description,
        )
        return ComplaintResponse(
            id=obj.id,
            user_id=obj.user_id,
            complainant_type=obj.complainant_type,
            complainant_id=obj.complainant_id,
            reason_code=obj.reason_code,
            description=obj.description,
            status=obj.status,
            admin_id=None,
            action=None,
            result_description=None,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    async def list(
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ComplaintListResponse:
        result = await ComplaintDAO.list(
            status=status, user_id=user_id,
            page=page, page_size=page_size,
        )
        return ComplaintListResponse(**result)

    @staticmethod
    async def get_stats() -> ComplaintStatsResponse:
        stats = await ComplaintDAO.get_count_by_status()
        return ComplaintStatsResponse(**stats)

    @staticmethod
    async def approve(
        complaint_id: int,
        admin_id: int,
        action: str,
        result_description: Optional[str] = None,
    ) -> Optional[ComplaintResponse]:
        obj = await ComplaintDAO.approve(
            complaint_id, admin_id, action, result_description,
        )
        if not obj:
            return None

        # 记录管理员操作日志
        admin = await Users.get_or_none(id=admin_id)
        await LogDAO.log(
            action=f"complaint_{action}",
            operator=admin,
            target_type="complaint",
            target_id=complaint_id,
            detail={"result": result_description},
        )

        return ComplaintResponse(
            id=obj.id,
            user_id=obj.user_id,
            complainant_type=obj.complainant_type,
            complainant_id=obj.complainant_id,
            reason_code=obj.reason_code,
            description=obj.description,
            status=obj.status,
            admin_id=obj.admin_id,
            action=obj.action,
            result_description=obj.result_description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    async def reject(
        complaint_id: int,
        admin_id: int,
        result_description: Optional[str] = None,
    ) -> Optional[ComplaintResponse]:
        obj = await ComplaintDAO.reject(complaint_id, admin_id, result_description)
        if not obj:
            return None

        admin = await Users.get_or_none(id=admin_id)
        await LogDAO.log(
            action="complaint_dismiss",
            operator=admin,
            target_type="complaint",
            target_id=complaint_id,
            detail={"reason": result_description},
        )

        return ComplaintResponse(
            id=obj.id,
            user_id=obj.user_id,
            complainant_type=obj.complainant_type,
            complainant_id=obj.complainant_id,
            reason_code=obj.reason_code,
            description=obj.description,
            status=obj.status,
            admin_id=obj.admin_id,
            action=obj.action,
            result_description=obj.result_description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
