"""
Example program to demonstrate Gooey's presentation of subparsers
"""

from datetime import datetime

from gooey import Gooey, GooeyParser

from commons.variables import *
from handlers.check_for_update import check_for_update, profile_check_for_update, driver_check_for_update, \
    config_check_for_update, audio_check_for_update, profile_rf7_check_for_update
from handlers.configReader import ConfigReader
from tools.conf_builder import conf_builder
from tools.data_pressure import data_pressure
from tools.direct_con_dev import direct_con_dev
from tools.excel_tool import excel_tool
from tools.gw_bind_unbind_pressure import gw_bind_unbind_pressure
from tools.gw_simulator import gw_simulator
from tools.link_duration import link_duration
from tools.property_builder import property_builder
from tools.regular_filter import regular_filter
from tools.scene_builder_tool import scene_builder_tool
from tools.t2_colorTemperaTure import t2_colorTemperaTure
from tools.t2_led import t2_led
from tools.web_ota_tool import web_ota_tool
from tools.web_reboot_tool import web_reboot_tool

running = True


@Gooey(encoding='utf-8', program_name="Test-Tools", language='chinese', default_size=(750, 700),
       header_show_title=False,
       menu=[{'name': '文件', 'items': [item_script_link, item_env, item_vdev, item_sys, item_data_pressure_test_template,
                                      item_subDev_info_template]},
             {'name': '工具', 'items': [item_rttys, item_json]},
             {'name': '帮助', 'items': [item_about, item_guide_web, item_guide]}])
def main():
    input_info = os.path.join(project_root, "input_info.ini")
    config_manager = ConfigReader(input_info)

    settings_msg = f'版本：{version}\n执行日志：D:\pwy_log\Leelen-ATT'
    parser = GooeyParser(description=settings_msg)
    subs = parser.add_subparsers(help='tools', dest='tools')

    home_page = subs.add_parser('******Welcome*******')
    env = home_page.add_argument_group('欢迎使用Test-Tools', gooey_options={'columns': 1})
    env.add_argument(' ', help='', type=str, widget='Textarea', gooey_options={'height': 330},
                     default=welcome_mes)

    readme_parser = subs.add_parser('******家居助手*******')
    env = readme_parser.add_argument_group('Readme', gooey_options={'columns': 1})
    default_txt = readme_test
    env.add_argument(' ', help='', type=str, widget='Textarea', gooey_options={'height': 600},
                     default=f"{default_txt}")

    time_parser = subs.add_parser('真实设备链路监控')
    env = time_parser.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    scenes = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=scenes,
                     default=config_manager.get_value('真实设备链路监控', '测试环境', fallback='iotpre'))
    envs = ["单控", "群组", "联动场景", "定时场景", "手动场景", "小立管家唤醒"]
    env.add_argument('场景', type=str, widget='Dropdown', choices=envs,
                     default=config_manager.get_value('真实设备链路监控', '场景', fallback='单控'))
    env.add_argument('联动条件did', type=str, widget='TextField', default='none', help='仅联动场景填写，其他场景默认即可')
    env.add_argument('最大控制数量', type=str, widget='TextField', default='All',
                     help='All：网关下挂所有逻辑设备\n100：100个逻辑设备（自定义）\ndid：具体设备did\n注：小立管家唤醒场景仅支持All')
    app = time_parser.add_argument_group('测试APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('真实设备链路监控', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('真实设备链路监控', '密码', fallback='test'))
    gateway = time_parser.add_argument_group('测试网关信息', gooey_options={'columns': 2})
    gateway.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('真实设备链路监控', 'Did'))
    other = time_parser.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('测试间隔时长', type=float, widget='TextField',
                       default=config_manager.get_value('真实设备链路监控', '测试间隔时长', fallback='30'), help='每轮测试超时时长')
    other.add_argument('测试轮询次数', type=int, widget='TextField',
                       default=config_manager.get_value('真实设备链路监控', '测试轮询次数', fallback='100'))

    time_parser = subs.add_parser('虚拟设备链路监控')
    env = time_parser.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    scenes = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=scenes,
                     default=config_manager.get_value('虚拟设备链路监控', '测试环境', fallback='iotpre'))
    vDevs = ["虚拟设备1（204|208|209）", "虚拟设备2（206|207|213）",
             "虚拟设备3（210|211|212）", "虚拟设备4（214|215|217）",
             "虚拟设备5（216|218|219）"]
    env.add_argument('虚拟设备', type=str, widget='Dropdown', choices=vDevs,
                     default=config_manager.get_value('虚拟设备链路监控', '虚拟设备'))
    env.add_argument('APP用户名', type=str, widget='TextField',
                     default=config_manager.get_value('虚拟设备链路监控', 'APP用户名', fallback='15606075512'))
    env.add_argument('APP密码', type=str, widget='TextField',
                     default=config_manager.get_value('虚拟设备链路监控', 'APP密码', fallback='test'))
    other = time_parser.add_argument_group('测试关键信息', gooey_options={'columns': 3})
    scenes = ["联动场景", "定时场景", "手动场景", "群组"]
    other.add_argument('测试场景', type=str, widget='Dropdown', choices=scenes,
                       default=config_manager.get_value('虚拟设备链路监控', '测试场景', fallback='联动场景'))
    other.add_argument('测试间隔时长', type=float, widget='TextField',
                       default=config_manager.get_value('虚拟设备链路监控', '测试间隔时长', fallback='30'), help='每轮测试超时时长')
    other.add_argument('测试轮询次数', type=int, widget='TextField',
                       default=config_manager.get_value('虚拟设备链路监控', '测试轮询次数', fallback='100'))
    linkage = time_parser.add_argument_group('联动场景', gooey_options={'columns': 3})
    conditions = ["人体存在传感器", "温湿度传感器", "嵌入式红外幕帘传感器"]
    linkage.add_argument('条件执行设备', type=str, widget='Dropdown', choices=conditions,
                         default=config_manager.get_value('虚拟设备链路监控', '条件执行设备', fallback='人体存在传感器'))
    num = [1, 2]
    linkage.add_argument('条件设备个数', type=int, widget='Dropdown', choices=num,
                         default=config_manager.get_value('虚拟设备链路监控', '条件设备个数', fallback=1))
    linkage.add_argument('条件设备所在网关', type=str, widget='TextField',
                         default=config_manager.get_value('虚拟设备链路监控', '条件设备所在网关', fallback=''))
    actions = ["T2筒射灯", "所有下挂设备"]
    linkage.add_argument('动作执行设备', type=str, widget='Dropdown', choices=actions,
                         default=config_manager.get_value('虚拟设备链路监控', '动作执行设备', fallback='T2筒射灯'))
    action = ["开关", "手动配置"]
    linkage.add_argument('执行动作', type=str, widget='Dropdown', choices=action,
                         default=config_manager.get_value('虚拟设备链路监控', '执行动作', fallback="开关"))
    linkage.add_argument('动作设备所在网关', type=str, widget='TextField',
                         default=config_manager.get_value('虚拟设备链路监控', '动作设备所在网关', fallback=''))

    colorTemperaTure_parser = subs.add_parser('T2筒射灯色温压测', help='T2筒射灯色温压测')
    env = colorTemperaTure_parser.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    scenes = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=scenes,
                     default=config_manager.get_value('T2筒射灯色温压测', '测试环境', fallback='iotpre'))
    env.add_argument('测试模型', type=str, widget='TextField',
                     default=config_manager.get_value('T2筒射灯色温压测', '测试模型', fallback='HAZB-AD-R82-001'))
    app = colorTemperaTure_parser.add_argument_group('测试APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('T2筒射灯色温压测', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('T2筒射灯色温压测', '密码', fallback='test'))
    gateway = colorTemperaTure_parser.add_argument_group('测试网关信息', gooey_options={'columns': 2})
    gateway.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('T2筒射灯色温压测', 'Did'))
    other = colorTemperaTure_parser.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('测试轮询次数', type=int, widget='TextField',
                       default=config_manager.get_value('T2筒射灯色温压测', '测试轮询次数', fallback='50'))

    gw_bind_unbind = subs.add_parser('解绑绑定压测', help='解绑绑定压测')
    env = gw_bind_unbind.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    scenes = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=scenes,
                     default=config_manager.get_value('解绑绑定压测', '测试环境', fallback='iotpre'))
    app = gw_bind_unbind.add_argument_group('测试APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('解绑绑定压测', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('解绑绑定压测', '密码', fallback='test'))
    gateway = gw_bind_unbind.add_argument_group('测试设备信息', gooey_options={'columns': 2})
    devices = ["网关", "wifi灯带"]
    gateway.add_argument('设备类型', type=str, widget='Dropdown', choices=devices,
                         default=config_manager.get_value('解绑绑定压测', '设备类型', fallback='网关'))
    gateway.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('解绑绑定压测', 'Did'))
    gateway.add_argument('SN', type=str, widget='TextField', help='网关填写默认值None',
                         default=config_manager.get_value('解绑绑定压测', 'SN', fallback='None'))
    wifi = gw_bind_unbind.add_argument_group('WiFi信息', gooey_options={'columns': 2})
    wifi.add_argument('wifi名称', type=str, widget='TextField', default=config_manager.get_value('解绑绑定压测', 'wifi名称'))
    wifi.add_argument('wifi密码', type=str, widget='TextField', default=config_manager.get_value('解绑绑定压测', 'wifi密码'))
    other = gw_bind_unbind.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('测试间隔时长', type=int, widget='TextField',
                       default=config_manager.get_value('解绑绑定压测', '测试间隔时长', fallback='1'))
    other.add_argument('测试轮询次数', type=int, widget='TextField',
                       default=config_manager.get_value('解绑绑定压测', '测试轮询次数', fallback='1'))

    scene_builder = subs.add_parser('场景生成器')
    env = scene_builder.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    scenes = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=scenes,
                     default=config_manager.get_value('场景生成器', '测试环境', fallback='iotpre'))
    envs = ["群组", "手动场景", "定时执行", "联动执行"]
    env.add_argument('预生成场景', type=str, widget='Dropdown', choices=envs,
                     default=config_manager.get_value('场景生成器', '预生成场景', fallback='群组'))
    app = scene_builder.add_argument_group('测试APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('场景生成器', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('场景生成器', '密码', fallback='test'))
    gateway = scene_builder.add_argument_group('测试网关信息', gooey_options={'columns': 2})
    gateway.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('场景生成器', 'Did'))
    other = scene_builder.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('生成间隔时长', type=float, widget='TextField',
                       default=config_manager.get_value('场景生成器', '生成间隔时长', fallback='3'), help='创建下一个场景间隔时长')
    other.add_argument('生成总数', type=int, widget='TextField',
                       default=config_manager.get_value('场景生成器', '生成总数', fallback='100'), help='注：为0时则删除所有场景')

    gateway_simulator = subs.add_parser('从网关模拟器')
    env = gateway_simulator.add_argument_group('预注册环境信息', gooey_options={'columns': 2})
    envs = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=envs,
                     default=config_manager.get_value('从网关模拟器', '测试环境', fallback='iotpre'))
    app = gateway_simulator.add_argument_group('预绑定APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('从网关模拟器', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('从网关模拟器', '密码', fallback='test'))
    app.add_argument('住家名称', type=str, widget='TextField',
                     default=config_manager.get_value('从网关模拟器', '住家名称', fallback='我的家'))
    app.add_argument('房间', type=str, widget='TextField',
                     default=config_manager.get_value('从网关模拟器', '房间', fallback='客厅'))
    app.add_argument('主网关Did', type=str, widget='TextField',
                     default=config_manager.get_value('从网关模拟器', '主网关Did'))
    app.add_argument('主网关IP', type=str, widget='TextField',
                     default=config_manager.get_value('从网关模拟器', '主网关IP'))
    gw = gateway_simulator.add_argument_group('预注册网关信息', gooey_options={'columns': 1})
    # gw_type = ['主网关', '备网关', '从网关', '盲网关']
    # gw.add_argument('网关类型', type=str, widget='Dropdown', choices=gw_type,
    #                 default=config_manager.get_value('从网关模拟器', '网关类型', fallback='从网关'))
    gw.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('从网关模拟器', 'Did'))
    soft_model = ["Zigbee无线网关3.0:HAZB-CE-R15-112:371"]
    gw.add_argument('产品_软件模型_profileId', type=str, widget='Dropdown', choices=soft_model,
                    default=config_manager.get_value('从网关模拟器', '产品_软件模型_profileId'))
    subDev = gateway_simulator.add_argument_group('预绑定子设备信息', gooey_options={'columns': 1})
    subDev.add_argument('Path', type=str, widget='FileChooser', help='子设备信息模板获取：文件-虚拟子设备信息模板下载',
                        default=config_manager.get_value('从网关模拟器', 'Path'))
    other = gateway_simulator.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('间隔时长', type=float, widget='TextField', help='模拟设备发起局域网信息请求间隔时长（S）',
                       default=config_manager.get_value('从网关模拟器', '间隔时长', fallback='10'))
    other.add_argument('测试次数', type=int, widget='TextField', help='所有子设备发送一轮信息请求为1次',
                       default=config_manager.get_value('从网关模拟器', '测试次数', fallback='100'))

    readme_parser = subs.add_parser('****海外门禁助手****')
    env = readme_parser.add_argument_group('Readme', gooey_options={'columns': 1})
    default_txt = readme_access_ctl
    env.add_argument(' ', help='', type=str, widget='Textarea', gooey_options={'height': 600},
                     default=f"{default_txt}")

    web_ota = subs.add_parser('web-OTA中断电压测')
    env = web_ota.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    env.add_argument('PDU_IP', type=str, widget='TextField',
                     default=config_manager.get_value('web-OTA中断电压测', 'PDU_IP', fallback='192.168.1.250'))
    lock = [1, 2, 3, 4]
    env.add_argument('PDU插座号', type=int, widget='Dropdown', choices=lock,
                     default=config_manager.get_value('web-OTA中断电压测', 'PDU插座号', fallback=1))
    env.add_argument('主机IP', type=str, widget='TextField',
                     default=config_manager.get_value('web-OTA中断电压测', '主机IP', fallback='192.168.1.100'))
    package = web_ota.add_argument_group("升级信息", gooey_options={'columns': 1})
    package.add_argument('升级包路径', type=str, widget='FileChooser',
                         default=config_manager.get_value('web-OTA中断电压测', '升级包路径'))
    package.add_argument('软件版本', type=str, widget='TextField', default=config_manager.get_value('web-OTA中断电压测', '软件版本'))
    other = web_ota.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('下电区间', type=str, widget='TextField', help='点击升级后在此区间轮询下电\n注：0-0为不做下电操作',
                       default=config_manager.get_value('web-OTA中断电压测', '下电区间', fallback='2-5'))
    other.add_argument('间隔时长', type=int, widget='TextField', help='上电后到操作登录的间隔时长（S）',
                       default=config_manager.get_value('web-OTA中断电压测', '间隔时长', fallback='60'))
    other.add_argument('压测次数', type=int, widget='TextField', help='下电-上电为一轮询',
                       default=config_manager.get_value('web-OTA中断电压测', '压测次数', fallback='100'))

    web_reboot = subs.add_parser('web-reboot')
    env = web_reboot.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    env.add_argument('主机IP', type=str, widget='TextField',
                     default=config_manager.get_value('web-reboot', '主机IP', fallback='192.168.1.100'))
    other = web_reboot.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('间隔时长', type=int, widget='TextField', help='主机软重启后ping通到操作登录的间隔时长（S）',
                       default=config_manager.get_value('web-reboot', '间隔时长', fallback='20'))
    other.add_argument('压测次数', type=int, widget='TextField',
                       default=config_manager.get_value('web-reboot', '压测次数', fallback='100'))

    readme_parser = subs.add_parser('******开发助手*******')
    env = readme_parser.add_argument_group('Readme', gooey_options={'columns': 1})
    default_txt = readme_develop
    env.add_argument(' ', help='', type=str, widget='Textarea', gooey_options={'height': 600},
                     default=f"{default_txt}")

    cf_parser = subs.add_parser('配置生成器')
    env = cf_parser.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    envs = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=envs,
                     default=config_manager.get_value('配置生成器', '测试环境', fallback='iotpre'))
    framework = ["RF2.8", "RF7.0"]
    env.add_argument('测试框架', type=str, widget='Dropdown', choices=framework,
                     default=config_manager.get_value('配置生成器', '测试框架', fallback='RF7.0'))
    app = cf_parser.add_argument_group('测试APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('配置生成器', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('配置生成器', '密码', fallback='test'))
    gateway = cf_parser.add_argument_group('测试网关信息', gooey_options={'columns': 2})
    gateway.add_argument('Did', type=str, widget='TextField', help='注：若tp_bus虚拟设备使用配套两线网关时填写None',
                         default=config_manager.get_value('配置生成器', 'Did', fallback='None'))
    vDev = cf_parser.add_argument_group('测试设备信息', gooey_options={'columns': 1})
    zigbee_vDevs = ["虚拟设备1（204|208|209）", "虚拟设备2（206|207|213）",
                    "虚拟设备3（210|211|212）", "虚拟设备4（214|215|217）",
                    "虚拟设备5（216|218|219）", "虚拟设备6（220|222|223）"]
    vDev.add_argument('Zigbee虚拟设备', type=str, widget='Dropdown', choices=zigbee_vDevs,
                      default=config_manager.get_value('配置生成器', 'Zigbee虚拟设备'))
    tp_bus_vDevs = ['None', "配套网关虚拟设备1（111）", "配套网关虚拟设备2（112）", "虚拟设备1（111）", "虚拟设备2（112）"]
    vDev.add_argument('tp_bus虚拟设备', type=str, widget='Dropdown', choices=tp_bus_vDevs,
                      default=config_manager.get_value('配置生成器', 'tp_bus虚拟设备'))
    path = cf_parser.add_argument_group('配置存储路径')
    path.add_argument('Path', type=str, widget='DirChooser', default=config_manager.get_value('配置生成器', 'Path'))

    direct_connect_dev = subs.add_parser('直连桩注册绑定')
    env = direct_connect_dev.add_argument_group('预注册环境信息', gooey_options={'columns': 2})
    envs = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=envs,
                     default=config_manager.get_value('直连桩注册绑定', '测试环境', fallback='iotpre'))
    app = direct_connect_dev.add_argument_group('预绑定APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('直连桩注册绑定', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('直连桩注册绑定', '密码', fallback='test'))
    app.add_argument('住家名称', type=str, widget='TextField',
                     default=config_manager.get_value('直连桩注册绑定', '住家名称', fallback='我的家'))
    app.add_argument('房间', type=str, widget='TextField',
                     default=config_manager.get_value('直连桩注册绑定', '房间', fallback='客厅'))
    stake = direct_connect_dev.add_argument_group('预注册直连桩信息', gooey_options={'columns': 2})
    stake.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('直连桩注册绑定', 'Did'))
    stake.add_argument('IP', type=str, widget='TextField',
                       default=config_manager.get_value('直连桩注册绑定', 'IP', fallback='192.168.1.100'))
    # soft_model = ["Zigbee无线网关3.0:HAZB-CE-R15-112:355", "智能空开:HA-CE-R31-001:7"]  智能空开待调试
    soft_model = ["Zigbee无线网关3.0:HAZB-CE-R15-112:355"]
    stake.add_argument('产品_软件模型_profileId', type=str, widget='Dropdown', choices=soft_model,
                       default=config_manager.get_value('直连桩注册绑定', '产品_软件模型_profileId'))
    subDev = direct_connect_dev.add_argument_group('预注册子设备桩信息', gooey_options={'columns': 1})
    subDev.add_argument('subDevDid', type=str, widget='TextField',
                        default=config_manager.get_value('直连桩注册绑定', 'subDevDid'))
    subDevs = ["T2智能筒射灯:HAZB-AD-R82-001"]
    subDev.add_argument('产品_软件模型', type=str, widget='Dropdown', choices=subDevs,
                        default=config_manager.get_value('直连桩注册绑定', '产品_软件模型'))

    # profile_parser = subs.add_parser('属性生成器', help='虚拟设备属性生成器')
    # default_txt = profile_example
    # profile_parser.add_argument('真实设备属性值', help='', type=str, widget='Textarea', gooey_options={'height': 300},
    #                             default=f"示例--抓包中subDevices值：\n{default_txt}")

    excel_parser = subs.add_parser('合并Excel', help='合并Excel为一个文件')
    env = excel_parser.add_argument_group("必填参数", gooey_options={'columns': 1})
    env.add_argument('Excel文件夹', type=str, widget='DirChooser', default=config_manager.get_value('合并Excel', 'Excel文件夹'))
    env.add_argument('保留列名', type=str, widget='TextField', help='All：保留所有，多个用空格分开（eg：列名1 列名2 列名3）',
                     default=config_manager.get_value('合并Excel', '保留列名', fallback='All'))

    zigbee_analyzer = subs.add_parser('正则过滤器')
    time_stamp = zigbee_analyzer.add_argument_group(gooey_options={'columns': 1})
    time_stamp.add_argument('文件', type=str, widget='FileChooser',
                            default=config_manager.get_value('正则过滤器', '文件'))
    time_stamp.add_argument('过滤正则', type=str, widget='TextField',
                            default=config_manager.get_value('正则过滤器', '过滤正则', fallback=''))
    path = zigbee_analyzer.add_argument_group('过滤文件存储路径')
    path.add_argument('Path', type=str, widget='DirChooser', default=config_manager.get_value('正则过滤器', 'Path'))

    data_pressure_tester = subs.add_parser('数据压测器')
    env = data_pressure_tester.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    scenes = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=scenes,
                     default=config_manager.get_value('数据压测器', '测试环境', fallback='iotpre'))
    protocol = ["HTTP", "MQTT", "TCP", "UDP", "MIX"]
    env.add_argument('压测协议', type=str, widget='Dropdown', choices=protocol,
                     default=config_manager.get_value('数据压测器', '压测协议', fallback='HTTP'))
    env.add_argument('APP用户名', type=str, widget='TextField',
                     default=config_manager.get_value('数据压测器', 'APP用户名', fallback='15606075512'))
    env.add_argument('APP密码', type=str, widget='TextField',
                     default=config_manager.get_value('数据压测器', 'APP密码', fallback='test'))
    other = data_pressure_tester.add_argument_group('测试关键信息', gooey_options={'columns': 3})
    models = ["遇错即停", "遇错不停"]
    other.add_argument('测试模型', type=str, widget='Dropdown', choices=models,
                       default=config_manager.get_value('数据压测器', '测试模型', fallback='遇错即停'))
    other.add_argument('测试间隔时长', type=float, widget='TextField',
                       default=config_manager.get_value('数据压测器', '测试间隔时长', fallback='30'))
    other.add_argument('测试轮询次数', type=int, widget='TextField',
                       default=config_manager.get_value('数据压测器', '测试轮询次数', fallback='100'))
    path = data_pressure_tester.add_argument_group('数据文件路径')
    path.add_argument('Path', type=str, widget='FileChooser', help='数据文件模板获取：文件-数据压测模板下载',
                      default=config_manager.get_value('数据压测器', 'Path'))

    log_path = f"{log_dir}check_for_update.txt"
    if not check_for_update(log_path):
        args = parser.parse_args()
        input_info = vars(args)
        config_manager.set_value(input_info)
        config_manager.save_config()
        day = datetime.now().strftime('%Y-%m-%d-%H%M')
        if args.tools == '真实设备链路监控':
            log_path = f"{log_dir}真实设备链路监控_{day}.txt"
            audio_check_for_update(log_path)
            t2_led(args, log_path)
        elif args.tools == 'T2筒射灯色温压测':
            log_path = f"{log_dir}T2筒射灯色温压测_{day}.txt"
            t2_colorTemperaTure(args, log_path)
        elif args.tools == '配置生成器':
            log_path = f"{log_dir}配置生成器_{day}.txt"
            profile_check_for_update(log_path)
            profile_rf7_check_for_update(log_path)
            conf_builder(args, log_path)
        elif args.tools == '属性生成器':
            log_path = f"{log_dir}属性生成器_{day}.txt"
            property_builder(args, log_path)
        elif args.tools == '解绑绑定压测':
            log_path = f"{log_dir}解绑绑定压测_{day}.txt"
            gw_bind_unbind_pressure(args, log_path)
        elif args.tools == '直连桩注册绑定':
            log_path = f"{log_dir}直连桩注册绑定_{day}.txt"
            direct_con_dev(args, log_path)
        elif args.tools == '合并Excel':
            log_path = f"{log_dir}合并Excel_{day}.txt"
            excel_tool(args, log_path)
        elif args.tools == 'web-OTA中断电压测':
            log_path = f"{log_dir}web-OTA中断电压测_{day}.txt"
            driver_check_for_update(log_path)
            web_ota_tool(args, log_path)
        elif args.tools == 'web-reboot':
            log_path = f"{log_dir}web-reboot_{day}.txt"
            driver_check_for_update(log_path)
            web_reboot_tool(args, log_path)
        elif args.tools == '虚拟设备链路监控':
            log_path = f"{log_dir}虚拟设备链路监控_{day}.txt"
            config_check_for_update(log_path)
            link_duration(args, log_path)
        elif args.tools == '正则过滤器':
            log_path = f"{log_dir}正则过滤器_{day}.txt"
            regular_filter(args, log_path)
        elif args.tools == '场景生成器':
            log_path = f"{log_dir}场景生成器_{day}.txt"
            scene_builder_tool(args, log_path)
        elif args.tools == '数据压测器':
            log_path = f"{log_dir}数据压测器_{day}.txt"
            data_pressure(args, log_path)
        elif args.tools == '从网关模拟器':
            log_path = f"{log_dir}从网关模拟器_{day}.txt"
            config_check_for_update(log_path)
            gw_simulator(args, log_path)
        else:
            pass


if __name__ == '__main__':
    main()
