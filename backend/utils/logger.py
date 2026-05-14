"""日志工具模块 - 用于点赞功能调试"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# 创建日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = LOG_DIR / f"debug_{datetime.now().strftime('%Y%m%d')}.log"


def get_logger(name: str = "debug") -> logging.Logger:
    """获取带文件和控制台输出的日志记录器"""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 清理已存在的处理器
    logger.handlers.clear()
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '[%(asctime)s %(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件输出
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '[%(asctime)s %(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


# 全局日志记录器实例
debug_logger = get_logger("debug")


# 点赞功能专用日志函数
def log_like_action(
    action: str,
    user_id: int = None,
    comment_id: int = None,
    details: dict = None
):
    """
    记录点赞相关操作
    
    Args:
        action: 操作类型，如 'toggle_start', 'toggle_complete', 'error', 'query_software_delete' 等
        user_id: 用户ID
        comment_id: 评论ID
        details: 详细信息字典
    """
    if details is None:
        details = {}
    
    log_message = f"LIKE [{action}] "
    
    if user_id:
        log_message += f"user_id={user_id} "
    if comment_id:
        log_message += f"comment_id={comment_id} "
    
    if details:
        log_message += f"details={details}"
    
    debug_logger.info(log_message)
