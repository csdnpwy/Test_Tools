import os

# 软件信息
version = 24012516

# 常规变量
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
log_dir = "D:\\pwy_log\\Leelen-ATT\\"
hfs_url = 'http://10.54.56.56/'
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
    '云端DB_用户名_v': 'leelendb',
    '云端DB_密码_v': 'leelendb',
    '云端DB_Host_v': '10.160.0.55',
    '云端DB_Port_v': '3306',
    '云端DB_库名_v': 'account',
    '云端MQTT_Host_v': 'iotst-home.leelen.net',
    'MQTT常用服务器端口_v': '1883'
}
iot58 = {
    '云端环境_v': 'http://iotst-home2.leelen.net:80',
    '云端DB_用户名_v': 'leelendb',
    '云端DB_密码_v': 'leelendb',
    '云端DB_Host_v': '10.160.0.57',
    '云端DB_Port_v': '3306',
    '云端DB_库名_v': 'account',
    '云端MQTT_Host_v': 'iotst-home2.leelen.net',
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
    '子设备IP地址1_v': '10.54.57.210',
    '子设备IP地址2_v': '10.54.57.211',
    '子设备IP地址3_v': '10.54.57.212',
    'zigbee设备did后缀_v': '1c34f1fffeec7796',
    'zigbee设备did后缀2_v': '1c34f1fffeec74a3',
    'zigbee设备did后缀3_v': '1c34f1fffeec742e',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:77:96',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:74:a3',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:74:2e'
}
vDev204 = {
    '子设备IP地址1_v': '10.54.57.204',
    '子设备IP地址2_v': '10.54.57.208',
    '子设备IP地址3_v': '10.54.57.209',
    'zigbee设备did后缀_v': '1c34f1fffeec73f4',
    'zigbee设备did后缀2_v': '1c34f1fffeec7835',
    'zigbee设备did后缀3_v': '1c34f1fffeec74c9',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:73:f4',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:78:35',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:74:c9'
}
vDev206 = {
    '子设备IP地址1_v': '10.54.57.206',
    '子设备IP地址2_v': '10.54.57.207',
    '子设备IP地址3_v': '10.54.57.213',
    'zigbee设备did后缀_v': '1c34f1fffeec78a2',
    'zigbee设备did后缀2_v': '1c34f1fffef0f5b7',
    'zigbee设备did后缀3_v': '1c34f1fffef0f095',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:78:a2',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:f0:f5:b7',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:f0:f0:95'
}
vDev214 = {
    '子设备IP地址1_v': '10.54.57.214',
    '子设备IP地址2_v': '10.54.57.215',
    '子设备IP地址3_v': '10.54.57.217',
    'zigbee设备did后缀_v': '1c34f1fffef0f10f',
    'zigbee设备did后缀2_v': '1c34f1fffeec7688',
    'zigbee设备did后缀3_v': '1c34f1fffeec707a',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:f0:f1:0f',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:76:88',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:70:7a'
}
vDev216 = {
    '子设备IP地址1_v': '10.54.57.216',
    '子设备IP地址2_v': '10.54.57.218',
    '子设备IP地址3_v': '10.54.57.219',
    'zigbee设备did后缀_v': '1c34f1fffeec8683',
    'zigbee设备did后缀2_v': '1c34f1fffeec76b2',
    'zigbee设备did后缀3_v': '1c34f1fffeec762d',
    'zigbee设备did后缀IEEE_v': '1c:34:f1:ff:fe:ec:86:83',
    'zigbee设备did后缀2IEEE_v': '1c:34:f1:ff:fe:ec:76:b2',
    'zigbee设备did后缀3IEEE_v': '1c:34:f1:ff:fe:ec:76:2d'
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
              "\n" \
              "测试链路时长获取：\n" \
              "1、通过群组和联动的方式控制一个或多个测试设备（默认网关下挂所有设备）并监测全链路各个节点的用时；\n" \
              "修订记录；\n" \
              "231114：新增超时显示上报失败测试设备及失败率\n" \
              "231116：修订测试设备支持不同模型，以适配多模型混测情况\n" \
              "231129：新增单控场景，支持单/多设备测试，支持多设备混测\n" \
              "23112916：修订为默认单控网关下所有设备，亦可输入单控did\n" \
              "24012509：修订测试间隔时长支持浮点型\n" \
              "\n" \
              "T2筒射灯色温压测：\n" \
              "1、调节筒射灯色温至最高和最低，并截图保存；\n" \
              "\n" \
              "网关解绑绑定压测：\n" \
              "1、指定网关在住家下解绑-绑定压测；\n" \
              "\n"

readme_develop = "**************************** 使用说明 ****************************\n" \
                 "\n" \
                 "配置生成器：\n" \
                 "1、自动生成配置文件工具；\n" \
                 "修订记录；\n" \
                 "23113015：修订配置文件模板和修复mqtt_handler传参bug\n" \
                 "23120516：修订配置文件开启自动远程更新\n" \
                 "23120610：修订配置文件模板\n" \
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
