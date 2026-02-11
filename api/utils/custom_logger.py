"""
统一使用 loguru 日志
- 项目内直接: from utils.logger import logger
- 接管 Python 标准 logging，第三方库的 logging 也会输出到 loguru
"""

import logging
import sys
from pathlib import Path

from loguru import logger

# 项目根目录（api/）
BASE_DIR = Path(__file__).resolve().parent.parent

# 移除 loguru 默认 handler，避免重复输出
logger.remove()

# 控制台输出
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
)

# 文件输出（按日期轮转）
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logger.add(
    LOG_DIR / "api_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天轮转
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
    encoding="utf-8",
)


class InterceptHandler(logging.Handler):
    """将标准 logging 重定向到 loguru"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging_intercept():
    """接管标准 logging，使 Django、DRF 等库的日志也输出到 loguru"""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in logging.root.manager.loggerDict:
        if name != "loguru":
            logging.getLogger(name).handlers = [InterceptHandler()]
            logging.getLogger(name).propagate = False
