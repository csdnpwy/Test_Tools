"""
钉钉群消息发送
"""
from handlers.app_handler import app_request


def dingding(mes_type, mes, isAtAll="false"):
    """
    钉钉群消息发送，默认机器人ATE，默认发送text消息
    :param isAtAll: 是否at所有人
    :param mes: 预发送消息
    :param mes_type: 预发送消息类型 Info、Error
    """
    log_path = "D:\\pwy_log\\Leelen-ATT\\DingDing\\dingding_log.txt"
    # accesstoken = "3d10ad9b7eae68a002fd5271b674f3dae2425944aa5b8d2bd34c7f64b4fa8d43"
    # url = "https://oapi.dingtalk.com/robot/send?access_token=3d10ad9b7eae68a002fd5271b674f3dae2425944aa5b8d2bd34c7f64b4fa8d43"
    accesstoken = "4888bb1dea33f0730598bffe4e76d80070b049925d4c96c8de49b5d8ab0356f9"
    url = "https://oapi.dingtalk.com/robot/send?access_token=4888bb1dea33f0730598bffe4e76d80070b049925d4c96c8de49b5d8ab0356f9"
    data = {
        "at": {
            "isAtAll": f"{isAtAll}",
            "atUserIds": ["user001", "user002"],
            "atMobiles": ["15xxx", "18xxx"]
        },
        # 链接消息
        "link": {
            "messageUrl": "1",
            "picUrl": "1",
            "text": "1",
            "title": "1"
        },
        # markdown消息
        "markdown": {
            "text": "hello this is a test",
            "title": "Attention"
        },
        # feedCard消息
        "feedCard": {
            "links": {
                "picURL": "1",
                "messageURL": "1",
                "title": "1"
            }
        },
        # 文本消息
        "text": {
            "content": f"{mes_type}:{mes}"
        },
        "msgtype": "text",
        # actionCard消息
        "actionCard": {
            "hideAvatar": "1",
            "btnOrientation": "1",
            "singleTitle": "1",
            "btns": [{
                "actionURL": "1",
                "title": "1"
            }],
            "text": "1",
            "singleURL": "1",
            "title": "1"
        }
    }
    app_request(accesstoken, url, data, log_path)
