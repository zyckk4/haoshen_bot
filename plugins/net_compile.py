# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from mirai import At, GroupMessage
from utils.utils import Listen, send, my_filter

plugin = Listen(
    'net_complie',
    '在线编程,输入"/在线编程帮助"查看帮助'
)


@plugin.group()
async def net_compile(event: GroupMessage):
    kw = ['/R', '/vb', '/ts', '/kt', '/pas', '/lua', '/node.js', '/go', '/swift', '/rs', '/sh',
          '/pl', '/erl', '/scala', '/cs', '/rb', '/cpp', '/c', '/java', '/py3', '/py', '/php']
    if str(event.message_chain) == '/在线编程帮助':
        mesg = '指令为"/cpp 代码内容",、cpp可换成以下编程语言'+','.join(kw)
        await send(event, mesg, True)
        return
    for k in kw:
        if str(event.message_chain) == k:
            await send(event, "请在120s内输入代码")

            def waiter(event2):
                if event.sender.id == event2.sender.id:
                    code = str(event2.message_chain)
                    if code.startswith('输入：'):
                        num = code.find('\n')
                        if num == -1:
                            return code, ''
                        stdin = code[3:num]
                        code = code.replace(code[:num+1], '', 1)
                        return code, stdin
                    return code, ''
            mesg = await my_filter(waiter, "G", 120)
            if mesg is None:
                await send(event, "超时！", True)
                return
            code, stdin = mesg
            result = await netcomp(k.replace('/', '', 1), stdin, code)
            if result == -1:
                await send(event, [At(event.sender.id), "你太长了！"])
            elif result == -2:
                await send(event, [At(event.sender.id), "连接失败！"])
            else:
                # print(result)
                mesg = result['output'] if result["output"] else result["errors"]
                await send(event, mesg)
            return

legal_language = {
    "R": 80,
    "vb": 84,
    "ts": 1001,
    "kt": 19,
    "pas": 18,
    "lua": 17,
    "node.js": 4,
    "go": 6,
    "swift": 16,
    "rs": 9,
    "sh": 11,
    "pl": 14,
    "erl": 12,
    "scala": 5,
    "cs": 10,
    "rb": 1,
    "cpp": 7,
    "c": 7,
    "java": 8,
    "py3": 15,
    "py": 0,
    "php": 3
}


async def netcomp(language: str, stdin: str, code: str):
    if language not in legal_language:
        return -2
    url = "https://tool.runoob.com/compile2.php"
    payload = {
        "code": code,
        "token": "b6365362a90ac2ac7098ba52c13e352b",
        "stdin": stdin,
        "language": legal_language[language],
        "fileext": language
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url=url, data=payload, headers=headers) as resp:
                res = await resp.json()
    except Exception:
        return -2
    if len(res['output']) > 1000000 or len(res['output']) > 1000000:
        return -1
    return res
