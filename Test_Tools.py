"""
Example program to demonstrate Gooey's presentation of subparsers
"""

import argparse
from datetime import datetime

from gooey import Gooey, GooeyParser
from commons.variables import *
from handlers.check_for_update import check_for_update
from handlers.configReader import ConfigReader
from tools.conf_builder import conf_builder
from tools.direct_con_dev import direct_con_dev
from tools.gw_bind_unbind_pressure import gw_bind_unbind_pressure
from tools.property_builder import property_builder
from tools.t2_colorTemperaTure import t2_colorTemperaTure
from tools.t2_led import t2_led

running = True


@Gooey(
    encoding='utf-8',
    required_cols=2,
    optional_cols=2,
    program_name="Test-Tools",
    language='chinese',
    default_size=(750, 700),
    header_show_title=False,
    menu=[{'name': '文件', 'items': [item_env, item_vdev, item_sys]}, {'name': '工具', 'items': [item_rttys, item_json]},
          {'name': '帮助', 'items': [item_about]}]
)
def main():
    input_info = os.path.join(project_root, "input_info.ini")
    config_manager = ConfigReader(input_info)

    settings_msg = f'版本：{version}\n执行日志：D:\pwy_log\Leelen-ATT'
    parser = GooeyParser(description=settings_msg)
    subs = parser.add_subparsers(help='tools', dest='tools')

    readme_parser = subs.add_parser('******测试助手*******')
    default_txt = readme_test
    readme_parser.add_argument(' ', help='', type=str, widget='Textarea', gooey_options={'height': 600},
                               default=f"{default_txt}")

    time_parser = subs.add_parser('测试链路时长获取')
    env = time_parser.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    scenes = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=scenes,
                     default=config_manager.get_value('测试链路时长获取', '测试环境', fallback='iotpre'))
    envs = ["单控", "集中式-联动", "分布式-群组"]
    env.add_argument('场景', type=str, widget='Dropdown', choices=envs,
                     default=config_manager.get_value('测试链路时长获取', '场景', fallback='单控'))
    env.add_argument('联动条件did', type=str, widget='TextField', default='none', help='仅联动场景填写，其他场景默认即可')
    env.add_argument('单控did', type=str, widget='TextField', default='All', help='仅单控场景填写，All默认对网关下挂所有设备进行单控')
    app = time_parser.add_argument_group('测试APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('测试链路时长获取', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('测试链路时长获取', '密码', fallback='test'))
    gateway = time_parser.add_argument_group('测试网关信息', gooey_options={'columns': 2})
    gateway.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('测试链路时长获取', 'Did'))
    other = time_parser.add_argument_group('其他信息', gooey_options={'columns': 2})
    other.add_argument('测试间隔时长', type=float, widget='TextField',
                       default=config_manager.get_value('测试链路时长获取', '测试间隔时长', fallback='30'), help='每轮测试超时时长')
    other.add_argument('测试轮询次数', type=int, widget='TextField',
                       default=config_manager.get_value('测试链路时长获取', '测试轮询次数', fallback='100'))

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

    readme_parser = subs.add_parser('******开发助手*******')
    default_txt = readme_develop
    readme_parser.add_argument(' ', help='', type=str, widget='Textarea', gooey_options={'height': 600},
                               default=f"{default_txt}")

    cf_parser = subs.add_parser('配置生成器')
    env = cf_parser.add_argument_group('测试环境信息', gooey_options={'columns': 2})
    envs = ["iotpre", "iottest", "56", "58"]
    env.add_argument('测试环境', type=str, widget='Dropdown', choices=envs,
                     default=config_manager.get_value('配置生成器', '测试环境', fallback='iotpre'))
    app = cf_parser.add_argument_group('测试APP信息', gooey_options={'columns': 2})
    app.add_argument('用户名', type=str, widget='TextField',
                     default=config_manager.get_value('配置生成器', '用户名', fallback='15606075512'))
    app.add_argument('密码', type=str, widget='TextField',
                     default=config_manager.get_value('配置生成器', '密码', fallback='test'))
    gateway = cf_parser.add_argument_group('测试网关信息', gooey_options={'columns': 2})
    gateway.add_argument('Did', type=str, widget='TextField', default=config_manager.get_value('配置生成器', 'Did'))
    vDev = cf_parser.add_argument_group('测试设备信息', gooey_options={'columns': 1})
    vDevs = ["虚拟设备1（204|208|209）", "虚拟设备2（206|207|213）",
             "虚拟设备3（210|211|212）", "虚拟设备4（214|215|217）",
             "虚拟设备5（216|218|219）"]
    vDev.add_argument('虚拟设备', type=str, widget='Dropdown', choices=vDevs,
                      default=config_manager.get_value('配置生成器', '虚拟设备'))
    stake = cf_parser.add_argument_group('云端桩信息（无特殊需求，注册以下默认值即可）', gooey_options={'columns': 2})
    stake.add_argument('Did1', type=str, widget='TextField',
                       default=config_manager.get_value('配置生成器', 'Did1', fallback='12300001000000000001'))
    stake.add_argument('Did2', type=str, widget='TextField',
                       default=config_manager.get_value('配置生成器', 'Did2', fallback='12300001000000000002'))
    stake.add_argument('桩外设备did', type=str, widget='TextField',
                       default=config_manager.get_value('配置生成器', '桩外设备did', fallback='12300001000000000003'))
    stake.add_argument('Did100', type=str, widget='TextField',
                       default=config_manager.get_value('配置生成器', 'Did100', fallback='12300001000000000100'))
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
    subDev.add_argument('subDid', type=str, widget='TextField', default=config_manager.get_value('直连桩注册绑定', 'subDid'))
    subDevs = ["T2智能筒射灯:HAZB-AD-R82-001"]
    subDev.add_argument('产品_软件模型', type=str, widget='Dropdown', choices=subDevs,
                        default=config_manager.get_value('直连桩注册绑定', '产品_软件模型'))

    profile_parser = subs.add_parser('属性生成器', help='虚拟设备属性生成器')
    default_txt = profile_example
    profile_parser.add_argument('真实设备属性值', help='', type=str, widget='Textarea', gooey_options={'height': 300},
                                default=f"示例--抓包中subDevices值：\n{default_txt}")

    log_path = f"{log_dir}check_for_update.txt"
    if not check_for_update(log_path):
        args = parser.parse_args()
        input_info = vars(args)
        config_manager.set_value(input_info)
        config_manager.save_config()
        day = datetime.now().strftime('%Y-%m-%d')
        if args.tools == '测试链路时长获取':
            log_path = f"{log_dir}t2_led_{day}.txt"
            t2_led(args, log_path)
        elif args.tools == 'T2筒射灯色温压测':
            log_path = f"{log_dir}t2_colorTemperaTure_{day}.txt"
            t2_colorTemperaTure(args, log_path)
        elif args.tools == '配置生成器':
            log_path = f"{log_dir}conf_builder_{day}.txt"
            conf_builder(args, log_path)
        elif args.tools == '属性生成器':
            log_path = f"{log_dir}conf_builder_{day}.txt"
            property_builder(args, log_path)
        elif args.tools == '解绑绑定压测':
            log_path = f"{log_dir}gw_bind_unbind_{day}.txt"
            gw_bind_unbind_pressure(args, log_path)
        elif args.tools == '直连桩注册绑定':
            log_path = f"{log_dir}direct_connect_dev_{day}.txt"
            direct_con_dev(args, log_path)
        else:
            pass


if __name__ == '__main__':
    main()
