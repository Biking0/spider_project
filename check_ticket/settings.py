# coding: utf-8
# QQ邮箱成功开启POP3/SMTP服务,在第三方客户端登录时，密码框请输入以下授权码：
# dheyylttgaivdhce
from parse import u2
from parse import fr
from parse import pc
from parse import wn
from parse import a5j
from parse import a6e

# 账号密码配置
MAIL_CONFIG = {
    # '163': ['m18939255180@163.com', 'zzdx63716371', 'pop.163.com', 'plaintext'],
    'qq': ['2793582351@qq.com', 'dheyylttgaivdhce', 'pop.qq.com', 'ssl']
}

# 通过不同的发件人对应不同的解析
PARSE_CARRIER = {
    # 'easyjet': u2,
    # 'wowair': ww,
    'ryanair': fr,
    # 'flypgs': pc,
    # 'cebu': a5j,
    # 'GoIndigo': a6e,
    # 'jetblue': b6,
    # 'eastarjet': ze,
    # 'vueling': vy,
    # 'norwegian': d8,
    # 'pobeda': dp,
    # 'southwest': wn,
    # 'airbusan': bx,
    # 'twayair': tw,
    # 'jejuair': 7c,
    # 'interjet': 4o,
    # 'flybe': be,
    # 'hop': a5,
    # 'eurowings': ex,
    # 'eurowings': ex,
    # 'eurowings': ex,
}

# 因为存在垃圾大邮件的问题，python默认限制了行的大小，在这里增大10倍
MAXLINE = 20480

# 上传测试库的url
PUSH_TEST_URL = 'http://test.jiaoan100.com/br_test/check_ticket'

# 上传正式库的url
PUSH_URL = 'http://task.jiaoan100.com/br/check_ticket'

# 上传的超时时间
PUSH_TIMEOUT = 30

# 日志邮件地址
LOG_ADDR = 'qiaoliang@lamudatech.com'
LOG_PASSWORD = 'Qq7035854'
# TO_ADDR = ['invalidhost@lamudatech.com']
# 测试
TO_ADDR = ['hyn@lamudatech.com']
# TO_ADDR = ['qiaoliang@lamudatech.com']
SMTP_SERVER = ['smtp.exmail.qq.com', 465]
