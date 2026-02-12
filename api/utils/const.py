# 全局常量与业务配置（与 Django/插件无关的可变配置放这里）

# 默认密码（新建用户、重置密码时使用）
DEFAULT_PASSWORD = "123456"

# ---------- 登录失败锁定 ----------
# 统计失败次数的时间窗口（秒），在此时间内达到最大次数则触发惩罚
LOGIN_FAILURE_WINDOW_SECONDS = 120  # 2 分钟
# 时间窗口内允许的最大失败次数
LOGIN_MAX_FAILURES = 5
# 惩罚方式：'cooldown' = 仅冷却时间内禁止登录，到期可再试；'disable' = 禁用账户，需联系管理员恢复
LOGIN_PUNISHMENT_TYPE = "cooldown"  # 可选: "cooldown" | "disable"
# 惩罚时长（秒），仅对 cooldown 有效；disable 模式下账户需管理员在用户管理中恢复
LOGIN_LOCKOUT_SECONDS = 600  # 10 分钟
