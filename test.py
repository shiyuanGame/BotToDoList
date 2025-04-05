from datetime import datetime, timedelta 
from dateutil.relativedelta  import relativedelta 
import re 

# 当前时间 



def parse_time_expression(expr): 
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
            return relativedelta( )
        if delta is not None: 
            if direction == '前': 
                return now - delta
            else: 
                return now+delta
    time_match = re.match(r'^(\d{1,2})(?:点|:)(\d{1,2})(?:分|:)(\d{1,2})秒?$', expr)
 
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



def extract_reminder(input_str):
    """分离时间部分和提醒内容"""
    # 尝试逐步截取最长可解析的时间表达式 
    keywords = ['提醒我', '记得', '要']
    for keyword in keywords:
            if keyword in input_str:
                # 分割字符串并取第一个匹配项后的内容 
                parts = input_str.split(keyword,  1)
                if len(parts) > 1:
                    title = parts[1].split('|', 1)[0].strip()
                    break; 
 
 

    time =     parse_time_expression(input_str)
    
    # # parse_time_expression(input_str)
 
    return (title , time)
    
 
testname=extract_reminder("3小时后提醒我开飞机")
print(testname[0])
print(testname[1])

# 测试示例 
test_cases = [ 
    '现在', 
    '明天', 
    '后天', 
    '大后天', 
    '昨天', 
    '前天', 
    '大前天', 
    '3小时后', 
    '5分钟前', 
    '2天后', 
    '1周后', 
    '3月后', 
    '2年前', 
    '半年后', 
    '半月后', 
    '10点30分15秒' ,
    '10点0分' ,

]
