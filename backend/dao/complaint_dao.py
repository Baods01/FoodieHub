from typing import Optional, List

from models.complaints import Complaints, ComplaintHandlers
from models.users import Users


class ComplaintDAO:
    """举报数据访问层"""

    @classmethod
    async def create_complaint(
        cls,
        user_id: int,
        complainant_type: str,  # comment/shop/image
        complainant_id: int,
        reason_code: str,
        description: Optional[str] = None
    ) -> Complaints:
        """创建举报"""
        return await Complaints.create(
            user_id=user_id,
            complainant_type=complainant_type,
            complainant_id=complainant_id,
            reason_code=reason_code,
            description=description
        )

    @classmethod
    async def get_complaint_by_id(cls, complaint_id: int) -> Optional[Complaints]:
        """根据ID获取举报详情"""
        return await Complaints.get_or_none(id=complaint_id, is_active=True).prefetch_related("user")

    @classmethod
    async def get_complaint_with_user(cls, complaint_id: int) -> Optional[Complaints]:
        """获取举报详情（包含举报用户信息）"""
        return await Complaints.get_or_none(id=complaint_id, is_active=True).prefetch_related("user")

    @classmethod
    async def get_complaints_by_status(
        cls,
        status: str = "pending",
        limit: int = 20,
        offset: int = 0
    ) -> List[Complaints]:
        """按状态获取举报列表（管理员用）"""
        return await Complaints.filter(
            status=status,
            is_active=True
        ).order_by("-created_at").limit(limit).offset(offset).prefetch_related("user").all()

    @classmethod
    async def get_complaints_by_user(
        cls,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Complaints]:
        """按用户获取举报列表"""
        query = Complaints.filter(user_id=user_id, is_active=True).order_by("-created_at")
        
        if status:
            query = query.filter(status=status)
        
        return await query.limit(limit).offset(offset).all()

    @classmethod
    async def update_complaint_status(
        cls,
        complaint_id: int,
        status: str
    ) -> Optional[Complaints]:
        """更新举报状态"""
        complaint = await Complaints.get_or_none(id=complaint_id, is_active=True)
        if complaint:
            complaint.status = status
            await complaint.save()
            return complaint
        return None

    @classmethod
    async def create_complaint_handler(
        cls,
        complaint_id: int,
        handler_id: int,
        action: str,
        result_description: Optional[str] = None
    ) -> ComplaintHandlers:
        """创建举报处理记录"""
        return await ComplaintHandlers.create(
            complaint_id=complaint_id,
            handler_id=handler_id,
            action=action,
            result_description=result_description
        )

    @classmethod
    async def get_complaint_handlers(
        cls,
        complaint_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[ComplaintHandlers]:
        """获取举报处理记录列表"""
        return await ComplaintHandlers.filter(
            complaint_id=complaint_id,
            is_active=True
        ).order_by("created_at").limit(limit).offset(offset).prefetch_related("handler", "complaint").all()

    @classmethod
    async def get_complaint_by_complainant(
        cls,
        complainant_type: str,
        complainant_id: int,
        status: Optional[str] = None
    ) -> Optional[Complaints]:
        """根据被举报内容获取举报记录"""
        query = Complaints.filter(
            complainant_type=complainant_type,
            complainant_id=complainant_id,
            is_active=True
        )
        
        if status:
            query = query.filter(status=status)
        
        return await query.first()

    @classmethod
    async def has_pending_complaint(
        cls,
        user_id: int,
        complainant_type: str,
        complainant_id: int
    ) -> bool:
        """检查用户是否对该内容有未处理的举报"""
        return await Complaints.filter(
            user_id=user_id,
            complainant_type=complainant_type,
            complainant_id=complainant_id,
            status="pending",
            is_active=True
        ).exists()

    @classmethod
    async def delete_complaint(cls, complaint_id: int) -> bool:
        """软删除举报"""
        complaint = await Complaints.get_or_none(id=complaint_id, is_active=True)
        if complaint:
            complaint.is_active = False
            await complaint.save()
            return True
        return False

    @classmethod
    async def get_complaint_count_by_status(cls) -> dict:
        """获取各状态的举报数量统计"""
        pending = await Complaints.filter(status="pending", is_active=True).count()
        approved = await Complaints.filter(status="approved", is_active=True).count()
        rejected = await Complaints.filter(status="rejected", is_active=True).count()
        
        return {
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "total": pending + approved + rejected
        }