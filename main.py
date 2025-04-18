from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncio import run_coroutine_threadsafe
# 注册插件


@register(name="ToDoList", description="BotTodoList", version="0.2", author="Shiyuan")
class MyPlugin(BasePlugin):
    scheduler = AsyncIOScheduler()
    scheduler.start()
    # 插件加载时触发

    def __init__(self, host: APIHost):
        self.loop = asyncio.get_event_loop()
        pass

    def parse_time_expression(self, expr):
        # 中文时间名词映射
        now = datetime.now()
        time_mapping = {
            '现在': timedelta(0),
            '今天': timedelta(0),
            '明天': timedelta(days=1),
            '后天': timedelta(days=2),
            '大后天': timedelta(days=3),
            '昨天': timedelta(days=-1),
            '前天': timedelta(days=-2),
            '大前天': timedelta(days=-3),
            '半月后': timedelta(days=15),
            '半年后': relativedelta(months=6),
            '一年后': relativedelta(years=1),
            '一月后': relativedelta(months=1),
            '一周后': timedelta(weeks=1)
        }
        # 处理中文时间名词
        if expr in time_mapping:
            return now + time_mapping[expr]

        # 处理数字+单位格式
        match = re.match(r'(\d+)(?:[  个]?)(小时|分钟|秒|天|周|月|年)([前后]?)', expr)
        if match:
            num = int(match.group(1))     # 数字部分（如"3"）
            unit = match.group(2)    # 单位（如"小时"）
            direction = match.group(3)   # 方向（如"后"）
            delta = None
            if unit == '秒':
                delta = timedelta(seconds=num)
            elif unit == '分钟':
                delta = timedelta(minutes=num)
            elif unit == '小时':
                delta = timedelta(hours=num)
            elif unit == '天':
                delta = timedelta(days=num)
            elif unit == '周':
                delta = timedelta(weeks=num)
            elif unit == '月':
                delta = relativedelta(months=num)
            elif unit == '年':
                delta = relativedelta(years=num)
            else:
                return relativedelta()
            if delta is not None:
                if direction == '前':
                    return now - delta
                else:
                    return now+delta
        time_match = re.match(
            r'^(\d{1,2})(?:点|:)(\d{1,2})(?:分|:)(\d{1,2})秒?$', expr)

        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            second = int(time_match.group(3))
            return datetime(now.year,  now.month,  now.day,  hour, minute, second)

        time_match = re.match(r'^(\d{1,2})(?:点|:)(\d{1,2})(?:分|:)$', expr)

        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            return datetime(now.year,  now.month,  now.day,  hour, minute, 0)

        time_match = re.match(r'^(\d{1,2})(?:点|:)$', expr)

        if time_match:
            hour = int(time_match.group(1))
            return datetime(now.year,  now.month,  now.day,  hour, 0, 0)

        return None

    def extract_reminder(self, input_str):
        """分离时间部分和提醒内容"""
        # 尝试逐步截取最长可解析的时间表达式
        keywords = ['提醒我', '记得', '要']
        for keyword in keywords:
            if keyword in input_str:
                # 分割字符串并取第一个匹配项后的内容
                parts = input_str.split(keyword,  1)
                if len(parts) > 1:
                    title = parts[1].split('|', 1)[0].strip()
                    break
        time = self.parse_time_expression(input_str)
        return (title, time)

    # 异步初始化

    async def initialize(self):
        pass

     # 要放在MyPlugin类里面
    async def send_reminder(self,  ctx, title):
        adapter = self.host.get_platform_adapters()[0]
        id = ctx.event.sender_id
        await ctx.host.send_active_message(
            adapter=adapter,
            target_type="person",
            target_id=id,
            message=platform_message.MessageChain([
                platform_message.Plain(text=title)
            ])
        )
    # 当收到个人消息时触发

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):

        try:
            msg = ctx.event.text_message
            tittle = self.extract_reminder(msg)
            title = tittle[0]
            parsed_time = tittle[1]
            if parsed_time:
                ctx.prevent_default()
                # 调度任务的时候，传入一个普通的同步函数
                self.scheduler.add_job(
                    lambda: run_coroutine_threadsafe(
                        self.send_reminder(ctx, title), self.loop),
                    'date',
                    run_date=parsed_time
                )
        except Exception as e:
            print(f" msg  error: {e  }    ")

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = ctx.event.text_message  # 这里的 event 即为 GroupNormalMessageReceived 的对象
        if msg == "hello":  # 如果消息为hello

            # 输出调试信息
            self.ap.logger.debug("hello, {}".format(ctx.event.sender_id))

            # 回复消息 "hello, everyone!"
            ctx.add_return("reply", ["hello, everyone!"])

            # 阻止该事件默认行为（向接口获取回复）
            ctx.prevent_default()
    # 插件卸载时触发

    def __del__(self):
        pass
