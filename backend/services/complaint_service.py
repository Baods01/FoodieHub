from typing import Optional, List
from models.complaints import Complaints, ComplaintHandlers
from models.users import Users
from models.shops import Shops, Comments
from models.images import Images
from dao.complaint_dao import ComplaintDAO
from schemas.complaints import (
    ComplaintCreateRequest, ComplaintResponse,
    ComplaintListResponse, ComplaintHandlerResponse,
    ComplaintStatsResponse, ComplaintHandleRequest
)
from schemas.common import ResponseModel
from fastapi import HTTPException, status


class ComplaintService:
    """举报服务层"""

    @classmethod
    async def create_complaint(
        cls,
        user_id: int,
        request: ComplaintCreateRequest
    ) -> ComplaintResponse:
        """
        创建举报
        :param user_id: 举报发起用户ID
        :param request: 举报请求
        :return: 举报响应
        """
        # 检查是否存在未处理的重复举报
        has_pending = await ComplaintDAO.has_pending_complaint(
            user_id=user_id,
            complainant_type=request.complainant_type,
            complainant_id=request.complainant_id
        )
        
        if has_pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已对此内容发起过举报，请等待管理员处理"
            )
        
        # 验证被举报内容是否存在
        await cls._validate_complainant(request.complainant_type, request.complainant_id)
        
        # 创建举报
        complaint = await ComplaintDAO.create_complaint(
            user_id=user_id,
            complainant_type=request.complainant_type,
            complainant_id=request.complainant_id,
            reason_code=request.reason_code,
            description=request.description
        )
        
        # 获取用户信息
        user = await Users.get_or_none(id=user_id)
        
        return ComplaintResponse(
            id=complaint.id,
            complainant_type=complaint.complainant_type,
            complainant_id=complaint.complainant_id,
            reason_code=complaint.reason_code,
            reason_name=None,  # 可从字典获取名称
            description=complaint.description,
            status=complaint.status,
            user_id=user_id,
            user_nickname=user.nickname if user else None,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at
        )

    @classmethod
    async def _validate_complainant(cls, complainant_type: str, complainant_id: int) -> None:
        """
        验证被举报内容是否存在
        :param complainant_type: 被举报内容类型
        :param complainant_id: 被举报内容ID
        """
        if complainant_type == "comment":
            comment = await Comments.get_or_none(id=complainant_id, is_active=True)
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="举报的评论不存在或已被删除"
                )
        elif complainant_type == "shop":
            shop = await Shops.get_or_none(id=complainant_id, is_active=True)
            if not shop:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="举报的店铺不存在或已被封禁"
                )
        elif complainant_type == "image":
            image = await Images.get_or_none(id=complainant_id, is_active=True)
            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="举报的图片不存在或已被删除"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的举报类型"
            )

    @classmethod
    async def get_complaint_by_id(cls, complaint_id: int) -> ComplaintResponse:
        """
        获取举报详情
        :param complaint_id: 举报ID
        :return: 举报响应
        """
        complaint = await ComplaintDAO.get_complaint_with_user(complaint_id)
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="举报记录不存在"
            )
        
        return ComplaintResponse(
            id=complaint.id,
            complainant_type=complaint.complainant_type,
            complainant_id=complaint.complainant_id,
            reason_code=complaint.reason_code,
            reason_name=None,
            description=complaint.description,
            status=complaint.status,
            user_id=complaint.user.id,
            user_nickname=complaint.user.nickname,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at
        )

    @classmethod
    async def get_pending_complaints(
        cls,
        page: int = 1,
        page_size: int = 20
    ) -> ComplaintListResponse:
        """
        获取待处理举报列表（管理员用）
        :param page: 页码
        :param page_size: 每页数量
        :return: 举报列表响应
        """
        offset = (page - 1) * page_size
        complaints = await ComplaintDAO.get_complaints_by_status(
            status="pending",
            limit=page_size,
            offset=offset
        )
        
        # 获取总数
        stats = await ComplaintDAO.get_complaint_count_by_status()
        
        response_list = []
        for complaint in complaints:
            response_list.append(ComplaintResponse(
                id=complaint.id,
                complainant_type=complaint.complainant_type,
                complainant_id=complaint.complainant_id,
                reason_code=complaint.reason_code,
                reason_name=None,
                description=complaint.description,
                status=complaint.status,
                user_id=complaint.user.id,
                user_nickname=complaint.user.nickname,
                created_at=complaint.created_at,
                updated_at=complaint.updated_at
            ))
        
        return ComplaintListResponse(
            complaints=response_list,
            total=stats["pending"],
            page=page,
            page_size=page_size
        )

    @classmethod
    async def get_user_complaints(
        cls,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> ComplaintListResponse:
        """
        获取用户的举报列表
        :param user_id: 用户ID
        :param status: 状态过滤（可选）
        :param page: 页码
        :param page_size: 每页数量
        :return: 举报列表响应
        """
        offset = (page - 1) * page_size
        complaints = await ComplaintDAO.get_complaints_by_user(
            user_id=user_id,
            status=status,
            limit=page_size,
            offset=offset
        )
        
        # 获取总数
        # 简化处理，直接计数
        query = Complaints.filter(user_id=user_id, is_active=True)
        if status:
            query = query.filter(status=status)
        total = await query.count()
        
        response_list = []
        for complaint in complaints:
            response_list.append(ComplaintResponse(
                id=complaint.id,
                complainant_type=complaint.complainant_type,
                complainant_id=complaint.complainant_id,
                reason_code=complaint.reason_code,
                reason_name=None,
                description=complaint.description,
                status=complaint.status,
                user_id=user_id,
                user_nickname=None,
                created_at=complaint.created_at,
                updated_at=complaint.updated_at
            ))
        
        return ComplaintListResponse(
            complaints=response_list,
            total=total,
            page=page,
            page_size=page_size
        )

    @classmethod
    async def handle_complaint(
        cls,
        complaint_id: int,
        handler_id: int,
        request: ComplaintHandleRequest
    ) -> ComplaintResponse:
        """
        处理举报（管理员用）
        :param complaint_id: 举报ID
        :param handler_id: 处理管理员ID
        :param request: 处理请求
        :return: 更新后的举报响应
        """
        # 获取举报详情
        complaint = await ComplaintDAO.get_complaint_by_id(complaint_id)
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="举报记录不存在"
            )
        
        if complaint.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该举报已被处理"
            )
        
        # 执行处理动作
        await cls._execute_action(
            complainant_type=complaint.complainant_type,
            complainant_id=complaint.complainant_id,
            action=request.action
        )
        
        # 更新举报状态
        new_status = "approved" if request.action != "dismiss" else "rejected"
        await ComplaintDAO.update_complaint_status(complaint_id, new_status)
        
        # 创建处理记录
        await ComplaintDAO.create_complaint_handler(
            complaint_id=complaint_id,
            handler_id=handler_id,
            action=request.action,
            result_description=request.result_description
        )
        
        # 获取更新后的举报信息
        updated_complaint = await ComplaintDAO.get_complaint_with_user(complaint_id)
        
        return ComplaintResponse(
            id=updated_complaint.id,
            complainant_type=updated_complaint.complainant_type,
            complainant_id=updated_complaint.complainant_id,
            reason_code=updated_complaint.reason_code,
            reason_name=None,
            description=updated_complaint.description,
            status=updated_complaint.status,
            user_id=updated_complaint.user.id,
            user_nickname=updated_complaint.user.nickname,
            created_at=updated_complaint.created_at,
            updated_at=updated_complaint.updated_at
        )

    @classmethod
    async def _execute_action(cls, complainant_type: str, complainant_id: int, action: str) -> None:
        """
        执行处理动作
        :param complainant_type: 被举报内容类型
        :param complainant_id: 被举报内容ID
        :param action: 处理动作
        """
        if action == "delete_comment":
            # 删除评论
            comment = await Comments.get_or_none(id=complainant_id)
            if comment:
                comment.is_active = False
                await comment.save()
        
        elif action == "ban_shop":
            # 封禁店铺
            shop = await Shops.get_or_none(id=complainant_id)
            if shop:
                shop.is_active = False
                await shop.save()
        
        elif action == "remove_image":
            # 移除图片
            image = await Images.get_or_none(id=complainant_id)
            if image:
                image.is_active = False
                await image.save()
        
        elif action == "dismiss":
            # 驳回举报，无需执行其他操作
            pass
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的处理动作"
            )

    @classmethod
    async def get_complaint_stats(cls) -> ComplaintStatsResponse:
        """
        获取举报统计信息（管理员用）
        :return: 统计响应
        """
        stats = await ComplaintDAO.get_complaint_count_by_status()
        return ComplaintStatsResponse(**stats)

    @classmethod
    async def get_complaint_handlers(cls, complaint_id: int) -> List[ComplaintHandlerResponse]:
        """
        获取举报处理记录
        :param complaint_id: 举报ID
        :return: 处理记录列表
        """
        handlers = await ComplaintDAO.get_complaint_handlers(complaint_id)
        
        response_list = []
        for handler in handlers:
            handler_user = await Users.get_or_none(id=handler.handler_id) if handler.handler_id else None
            response_list.append(ComplaintHandlerResponse(
                id=handler.id,
                complaint_id=handler.complaint_id,
                handler_id=handler.handler_id,
                handler_nickname=handler_user.nickname if handler_user else None,
                action=handler.action,
                result_description=handler.result_description,
                created_at=handler.created_at
            ))
        
        return response_list
