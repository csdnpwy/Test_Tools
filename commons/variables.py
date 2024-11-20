import os

# 软件信息
version = 24112013

# 常规变量
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
conf_file_path = os.path.join(project_root, "configs", "config.cnf")
welcome_mes = r"""
                                                       ↑        ↑
                                                    ↖↑↗  ↖↑↗
                                                  _.-^^.......^^-._
                                                _                     _
                                               (<    ◔       ◔    >)
                                                |           Ω          |
                                                 \._  ↖___|___↗ _./
                                                   ```--. . . . .--'''
                                                         ||    ||
                                                  .-=+||     ||+=-.
                                                 `-=- +++++ -=-'
                                                          |:  :|
                                                          
                                            ___.,~-林恩欢迎您-~,.___
                                      ............................................................
                                            让人们生活在五星级的家
                                      ............................................................
"""
log_dir = "D:\\pwy_log\\Leelen-ATT\\"
hfs_url = 'http://10.58.71.56/'
item_about = {
    'type': 'AboutDialog',
    'menuTitle': '关于',
    'name': 'Test-Tools',
    'description': '          自动化测试工具和自动化开发助手          ',
    'version': f'{version}',
    'copyright': '2023',
    'website': '',
    'developer': 'panweiyang@leelen.cn',
    'license': 'Leelen'
}
item_env = {
    'type': 'Link',
    'menuTitle': '自动化环境搭建',
    'url': 'https://note.youdao.com/s/FH3BvRhn'
}
item_vdev = {
    'type': 'Link',
    'menuTitle': '虚拟设备接口协议',
    'url': 'https://note.youdao.com/s/It3xmL3y'
}
item_sys = {
    'type': 'Link',
    'menuTitle': '平台系统方案',
    'url': 'https://note.youdao.com/s/FRNrCvju'
}
item_data_pressure_test_template = {
    'type': 'Link',
    'menuTitle': '数据压测模板下载',
    'url': f'{hfs_url}data_pressure_test_template.xlsx'
}
item_subDev_info_template = {
    'type': 'Link',
    'menuTitle': '虚拟子设备信息模板下载',
    'url': f'{hfs_url}subDev_info_template.xlsx'
}
item_script_link = {
    'type': 'Link',
    'menuTitle': '常用脚本下载',
    'url': f'{hfs_url}Scripts/'
}
item_rttys = {
    'type': 'Link',
    'menuTitle': 'Rtty',
    'url': 'https://dbg.leelen.com:5913/'
}
item_json = {
    'type': 'Link',
    'menuTitle': 'Json编辑器',
    'url': 'https://www.bejson.com/jsoneditoronline/'
}
item_guide_web = {
    'type': 'Link',
    'menuTitle': '在线使用指南',
    'url': 'https://note.youdao.com/s/NPKpqYVo'
}
item_guide = {
    'type': 'Link',
    'menuTitle': '使用指南下载',
    'url': f'{hfs_url}Test-Tools_instructions.docx'
}

# IOT组件
dev_manage_moduleID = "00000001000000000000"

# 测试环境配置信息
iotpre = {
    '云端环境_v': 'http://iotpre.leelen.net:80',
    '云端DB_用户名_v': 'leelenread',
    '云端DB_密码_v': 'dOlbms1Cpgu&5wpN',
    '云端DB_Host_v': '47.99.129.175',
    '云端DB_Port_v': '63506',
    '云端DB_库名_v': 'account',
    '云端MQTT_Host_v': 'iotpre.leelen.net',
    'MQTT常用服务器端口_v': '1883'
}
iottest = {
    '云端环境_v': 'http://iottest.leelen.net:80',
    '云端DB_用户名_v': 'leelenread',
    '云端DB_密码_v': 'leelenread',
    '云端DB_Host_v': '10.160.1.16',
    '云端DB_Port_v': '3306',
    '云端DB_库名_v': 'account',
    '云端MQTT_Host_v': 'iottest.leelen.net',
    'MQTT常用服务器端口_v': '1883'
}
iot56 = {
    '云端环境_v': 'http://iotst-home.leelen.net:80',
    # '云端环境_v': 'http://10.160.0.56:80',
    '云端DB_用户名_v': 'leelendb',
    '云端DB_密码_v': 'leelendb',
    '云端DB_Host_v': '10.160.0.55',
    '云端DB_Port_v': '3306',
    '云端DB_库名_v': 'account',
    '云端MQTT_Host_v': 'iotst-home.leelen.net',
    # '云端MQTT_Host_v': '10.160.0.56',
    'MQTT常用服务器端口_v': '1883'
}
iot58 = {
    '云端环境_v': 'http://iotst-home2.leelen.net:80',
    # '云端环境_v': 'http://10.160.0.58:80',
    '云端DB_用户名_v': 'leelendb',
    '云端DB_密码_v': 'leelendb',
    '云端DB_Host_v': '10.160.0.57',
    '云端DB_Port_v': '3306',
    '云端DB_库名_v': 'account',
    '云端MQTT_Host_v': 'iotst-home2.leelen.net',
    # '云端MQTT_Host_v': '10.160.0.58',
    'MQTT常用服务器端口_v': '1883'
}
envs = {
    'iotpre': iotpre,
    'iottest': iottest,
    '56': iot56,
    '58': iot58,
}
# 虚拟设备信息
vDev210 = {
    '子设备IP地址1_v': '10.58.71.210',
    '子设备IP地址2_v': '10.58.71.211',
    '子设备IP地址3_v': '10.58.71.212',
    'zigbee设备did后缀_v': '1c34f1fffeec7796',
    'zigbee设备did后缀2_v': '1c34f1fffeec74a3',
    'zigbee设备did后缀3_v': '1c34f1fffeec742e',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:77:96',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:74:a3',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:74:2e',
    '设备did_v': '12300001000000test01',
    '设备did2_v': '12300001000000test02',
    '桩外设备did1_v': '12300001000000test03',
    '设备did100_v': '12300001000000test04'
}
vDev204 = {
    '子设备IP地址1_v': '10.25.25.204',
    '子设备IP地址2_v': '10.25.25.208',
    '子设备IP地址3_v': '10.25.25.209',
    'zigbee设备did后缀_v': '1c34f1fffeec73f4',
    'zigbee设备did后缀2_v': '1c34f1fffeec7835',
    'zigbee设备did后缀3_v': '1c34f1fffeec74c9',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:73:f4',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:78:35',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:74:c9',
    '设备did_v': '12300001000000test05',
    '设备did2_v': '12300001000000test06',
    '桩外设备did1_v': '12300001000000test07',
    '设备did100_v': '12300001000000test08'
}
vDev206 = {
    '子设备IP地址1_v': '10.25.25.206',
    '子设备IP地址2_v': '10.25.25.207',
    '子设备IP地址3_v': '10.25.25.213',
    'zigbee设备did后缀_v': '1c34f1fffef0f095',
    'zigbee设备did后缀2_v': '1c34f1fffef0f5b7',
    'zigbee设备did后缀3_v': '1c34f1fffeec78a2',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:f0:f0:95',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:f0:f5:b7',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:78:a2',
    '设备did_v': '12300001000000test09',
    '设备did2_v': '12300001000000test10',
    '桩外设备did1_v': '12300001000000test11',
    '设备did100_v': '12300001000000test12'
}
vDev214 = {
    '子设备IP地址1_v': '10.58.71.214',
    '子设备IP地址2_v': '10.58.71.215',
    '子设备IP地址3_v': '10.58.71.217',
    'zigbee设备did后缀_v': '1c34f1fffef0f20a',
    'zigbee设备did后缀2_v': '1c34f1fffeec8763',
    'zigbee设备did后缀3_v': '94deb8fffecb08f8',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:f0:f2:0a',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:87:63',
    'zigbee设备did后缀3IEEE_v': '94:de:b8:ff:fe:cb:08:f8',
    '设备did_v': '12300001000000test13',
    '设备did2_v': '12300001000000test14',
    '桩外设备did1_v': '12300001000000test15',
    '设备did100_v': '12300001000000test16'
}
vDev216 = {
    '子设备IP地址1_v': '10.58.71.216',
    '子设备IP地址2_v': '10.58.71.218',
    '子设备IP地址3_v': '10.58.71.219',
    'zigbee设备did后缀_v': '1c34f1fffeec8683',
    'zigbee设备did后缀2_v': '1c34f1fffeec76b2',
    'zigbee设备did后缀3_v': '1c34f1fffeec762d',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:86:83',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:76:b2',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:76:2d',
    '设备did_v': '12300001000000test17',
    '设备did2_v': '12300001000000test18',
    '桩外设备did1_v': '12300001000000test19',
    '设备did100_v': '12300001000000test20'
}
vDev220 = {
    '子设备IP地址1_v': '10.58.71.220',
    '子设备IP地址2_v': '10.58.71.222',
    '子设备IP地址3_v': '10.58.71.223',
    'zigbee设备did后缀_v': '1c34f1fffeec7936',
    'zigbee设备did后缀2_v': '1c34f1fffef0f043',
    'zigbee设备did后缀3_v': '94deb8fffec5ceb9',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:79:36',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:f0:f0:43',
    'zigbee设备did后缀3IEEE_v': '94:de:b8:ff:fe:c5:ce:b9',
    '设备did_v': '12300001000000test21',
    '设备did2_v': '12300001000000test22',
    '桩外设备did1_v': '12300001000000test23',
    '设备did100_v': '12300001000000test24'
}
vDev111 = {
    '子设备IP地址4_v': '10.58.71.111',
    'did最后字节': '11'
}
vDev112 = {
    '子设备IP地址4_v': '10.58.71.112',
    'did最后字节': '22'
}
gw_vDev111 = {
    '子设备IP地址4_v': '10.58.71.111',
    'did最后字节': '11',
    '网关did_v': f'00012004e8a788ba36b9'
}
gw_vDev112 = {
    '子设备IP地址4_v': '10.58.71.112',
    'did最后字节': '22',
    '网关did_v': f'00012004e8a788ba36a4'
}
# 界面布局
gap_num = 95
# 其他信息
readme_test = "**************************** 使用说明 ****************************\n" \
              "\n" \
              "公共功能：\n" \
              "修订记录；\n" \
              "23120516：修订输入框记忆功能-启动自动填充上一次填写记录\n" \
              "23121419：修订GUI图标以及增加菜单按钮\n" \
              "24010310：修订预生产环境信息\n" \
              "24012516：修订56、58测试环境信息\n" \
              "24031816：修订虚拟设备4did后缀信息\n" \
              "24041910：环境切换（修订虚拟设备IP、远程服务器IP）\n" \
              "24080211：添加数据压测模板链接、常用脚本下载链接\n" \
              "24080614：新增全局获取监听桩did，解决监听did多处登录bug\n" \
              "24080717：新增欢迎页面\n" \
              "24080813：日志存储文件修订为以分钟为粒度，解决同一天测试日志挤在同一个文件中\n" \
              "24080916：修复mqtt监听桩意外断开后触发重连且重新订阅之前主题\n" \
              "24081410：修复mqtt发送报文为json格式\n" \
              "\n" \
              "真实设备链路监控：\n" \
              "1、通过群组和联动的方式控制一个或多个测试设备（默认网关下挂所有设备）并监测全链路各个节点的用时；\n" \
              "修订记录；\n" \
              "231114：新增超时显示上报失败测试设备及失败率\n" \
              "231116：修订测试设备支持不同模型，以适配多模型混测情况\n" \
              "231129：新增单控场景，支持单/多设备测试，支持多设备混测\n" \
              "23112916：修订为默认单控网关下所有设备，亦可输入单控did\n" \
              "24012509：修订测试间隔时长支持浮点型\n" \
              "24020113：修订测试设备对象为逻辑设备\n" \
              "24072317：1、新增手动场景 2、修订控制数据支持自定义\n" \
              "24080517：1、新增小立管家唤醒场景\n" \
              "24081416：1、修复单控无法指定具体did bug\n" \
              "24090210：兼容存在楼层的测试环境的住家ID获取\n" \
              "\n" \
              "T2筒射灯色温压测：\n" \
              "1、调节筒射灯色温至最高和最低，并截图保存；\n" \
              "\n" \
              "解绑绑定压测：\n" \
              "1、网关、灯带在住家下解绑-绑定压测；\n" \
              "修订记录；\n" \
              "24031419；新增灯带压测\n" \
              "\n" \
              "虚拟设备链路监控：\n" \
              "1、监控不同测试场景的控制链路时长\n" \
              "修订记录；\n" \
              "24060410：初版发行，支持联动场景\n" \
              "24060510：修订联动场景开始时间在清除缓存后\n" \
              "24061816：修订测试间隔时长为动态输入\n" \
              "24080211：兼容嵌入式红外幕帘传感器\n" \
              "\n" \
              "场景生成器：\n" \
              "1、自动生成指定数量的场景或群组，且支持对应删除操作\n" \
              "修订记录；\n" \
              "24072217：初版发行\n" \
              "24090210：兼容存在楼层的测试环境的住家ID获取\n" \
              "\n" \
              "从网关模拟器：\n" \
              "1、模拟虚拟从网关与局域网内主网关进行通信\n" \
              "修订记录；\n" \
              "24081410：初版发行\n" \
              "24082617：修订以Excel为数据驱动进行局域网tcp通信\n" \
              "\n"

readme_access_ctl = "**************************** 使用说明 ****************************\n" \
              "\n" \
              "web-OTA中断电压测：\n" \
              "1、登录门禁产品web端下发软件升级，升级过程中断电-重启压测；\n" \
              "修订记录；\n" \
              "24051517：新版发布\n" \
              "24062016：修订web重新加载url因未停止当前的加载导致失败的bug\n" \
              "24062416：修订每轮测试完关闭浏览器（暂时修复检测页面加载是否成功遗留bug）\n" \
              "24062509：修订不同win ping结果不同（False、None）导致的误判\n" \
              "24071814：兼容不做断电的升级压测\n" \
              "\n" \
              "web-reboot：\n" \
              "1、登录门禁产品web端点击保存按钮软重启压测；\n" \
              "修订记录；\n" \
              "24052115：新版发布\n" \

readme_develop = "**************************** 使用说明 ****************************\n" \
                 "\n" \
                 "配置生成器：\n" \
                 "1、自动生成配置文件工具；\n" \
                 "修订记录；\n" \
                 "23113015：修订配置文件模板和修复mqtt_handler传参bug\n" \
                 "23120516：修订配置文件开启自动远程更新\n" \
                 "23120610：修订配置文件模板\n" \
                 "24041615：配置文件新增“第二房间id”键值\n" \
                 "24090210：兼容存在楼层的测试环境的住家ID获取\n" \
                 "24092610：弃用桩did选框，修订监听桩和虚拟设备绑定配套使用，避免使用相同监听桩did多处登录造成的测试失败\n" \
                 "24101216：新增测试框架选框，兼容新框架RF7.0配置文件生成；更新虚拟盒子IP" \
                 "24111416：兼容多虚拟子设备新框架RF7.0配置文件生成" \
                 "24112013：增加住家信息与账号信息是否匹配判断" \
                 "\n" \
                 "直连桩注册绑定：\n" \
                 "1、直连设备注册并绑定到对应APP；\n" \
                 "修订记录；\n" \
                 "24012417：初版发行\n" \
                 "24012514：修复一些已知bug\n" \
                 "\n" \
                 "属性生成器：\n" \
                 "1、根据真实设备获取的属性值自动生成可传入虚拟设备格式的属性字符串；\n" \
                 "修订记录；\n" \
                 "\n" \
                 "合并Excel：\n" \
                 "1、多个Excel合并操作；\n" \
                 "修订记录；\n" \
                 "24050615：初版发行\n" \
                 "\n" \
                 "正则过滤器：\n" \
                 "1、正则表达式执行器：\n" \
                 "修订记录；\n" \
                 "24062815：初版发行\n" \
                 "\n" \
                 "数据压测器：\n" \
                 "1、实现通过excel为数据驱动对http、mqtt、tcp等协议的数据进行请求判断的压测\n" \
                 "修订记录；\n" \
                 "24080211：初版发行\n" \
                 "24081616：支持mqtt协议数据压测\n" \
                 "24111217：支持讯威控制模块上下电\n" \
                 "\n"

profile_example = "{\n  " \
                  "'errCode': 'null',\n" \
                  "  'fatherDid': '0001200424140702c4f7',\n" \
                  "  'did': '000b2012b4e3f9fffe326a65',\n" \
                  "   'profileId': 165,\n" \
                  "   'manufacturer': 'MULTIR',\n" \
                  "   'productModel': 'HAZB-SD-R28-001',\n" \
                  "   'softModel': 'HAZB-SD-R28-001',\n" \
                  "   'softVersion': 'MAIN:1.1',\n" \
                  "   'productSn': '',\n" \
                  "   'softProjectNo': 'HA-2020'\n" \
                  "}"
