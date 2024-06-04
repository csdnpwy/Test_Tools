#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import sys
import time
from tkinter import messagebox
import numpy as np
from ping3 import ping

from handlers.app_handler import get_terminal_info
from handlers.log_handler import get_log
from commons.variables import *
from handlers.mysql_tool import MyPymysqlPool
from lib.tcpRes import usr_tcp232_t2_tool, usr_tcp232_t2_tool_clear_buff, usr_tcp232_t2_tool_recv
from lib.zhsh_appRes import add_subDevices


def link_duration(args, log_path):
    """
    传感器联动链路时长获取
    :param args: 前端参数
    :param log_path: 日志路径
    """
    get_log(log_path).debug(args)
    get_log(log_path).info(f'Step 1：检测测试环境...')
    # 检测测试环境
    envs = {
        'iotpre': iotpre,
        'iottest': iottest,
        '56': iot56,
        '58': iot58,
    }
    evn = args.测试环境
    if evn in envs:
        mysql_info = {'host': f'{envs[evn]["云端DB_Host_v"]}', 'port': f'{envs[evn]["云端DB_Port_v"]}',
                      'user': f'{envs[evn]["云端DB_用户名_v"]}',
                      'password': f'{envs[evn]["云端DB_密码_v"]}', 'db_name': f'{envs[evn]["云端DB_库名_v"]}',
                      'charset': 'utf8'}
    else:
        get_log(log_path).error(f'未找到{evn}环境下的任何配置，请联系管理员处理！')
        sys.exit()
    # APP信息获取
    # 判断用户名密码是否正确
    db_tool = MyPymysqlPool(mysql_info)
    username = f"{args.APP用户名}"
    password = hashlib.sha256(f'{args.APP密码}'.encode('utf-8')).hexdigest()
    user_pw_sql = f"select password from lbl_app_account where username = '{username}'"
    try:
        user_pw_sql_res = db_tool.getAll(user_pw_sql)
        get_log(log_path).info(f'    ----    数据库访问正常')
        time.sleep(2)
        if not user_pw_sql_res:
            get_log(log_path).error(f'    !!!!    APP用户名不存在')
            sys.exit()
        else:
            if password == user_pw_sql_res[0]['password']:
                get_log(log_path).info(f'    ----    APP用户名、密码正确')
                time.sleep(2)
            else:
                get_log(log_path).error(f'    !!!!    APP密码错误')
                sys.exit()
    except Exception as e:
        get_log(log_path).error(f"    !!!!    数据库连通性异常 {e}")
        sys.exit()
    # 虚拟设备检测
    vdevs = {
        '虚拟设备1（204|208|209）': vDev204,
        '虚拟设备2（206|207|213）': vDev206,
        '虚拟设备3（210|211|212）': vDev210,
        '虚拟设备4（214|215|217）': vDev214,
        '虚拟设备5（216|218|219）': vDev216
    }
    vdev = args.虚拟设备
    ips = []
    if vdev in vdevs:
        ips = list(vdevs[vdev].values())[:3]
        for ip in ips:
            ping_res = ping(f"{ip}")
            if ping_res is not None:
                get_log(log_path).info(f'    ----    虚拟设备ip={ip}连通性正常')
                time.sleep(2)
            else:
                get_log(log_path).info(f'    !!!!    虚拟设备ip={ip}无法连通,请检查设备')
                sys.exit()
    if args.测试场景 == "联动场景":
        # 网关信息处理
        get_log(log_path).info(f'    ----    获取网关所在住家信息')
        sql_group_id = f"select group_id from newiot_device_group ndg  where biz_id = (select id from iot_dc_logic_device idld  where did = '{args.条件设备所在网关}' and siid = '2')"
        group_id = db_tool.getAll(sql_group_id)
        sql = f"select id, parent_id, name  from newiot_group ng  where id = '{group_id[0]['group_id']}'"
        res = db_tool.getAll(sql)
        condition_homeId = res[0]['parent_id']
        condition_room = res[0]['name']
        condition_roomID = res[0]['id']
        sql_group_id = f"select group_id from newiot_device_group ndg  where biz_id = (select id from iot_dc_logic_device idld  where did = '{args.动作设备所在网关}' and siid = '2')"
        group_id = db_tool.getAll(sql_group_id)
        sql = f"select id, parent_id, name  from newiot_group ng  where id = '{group_id[0]['group_id']}'"
        res = db_tool.getAll(sql)
        action_homeId = res[0]['parent_id']
        action_room = res[0]['name']
        action_roomID = res[0]['id']
        time.sleep(2)
        get_log(log_path).info(f'Step 2：测试环境初始化...')
        get_log(log_path).info(f'    ----    添加条件执行设备中，请耐心等待')
        dev_num = args.条件设备个数
        dev_type = args.条件执行设备
        terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.APP用户名, args.APP密码, log_path)
        directDid = args.条件设备所在网关
        if directDid.startswith("00012004"):
            direct_dev_type = "gw"
        elif directDid.startswith("00011002"):
            direct_dev_type = "mini"
        else:
            direct_dev_type = "gw"
        for dev in range(0, int(dev_num)):
            add_subDevices(args, log_path, dev_type, condition_homeId, terminal_info, directDid=directDid, dev=dev, direct_dev_type=direct_dev_type)
            get_log(log_path).info(f'       ----       第 {dev+1} 个条件执行设备添加完成')
        get_log(log_path).info(f'    ----    添加动作执行设备中，请耐心等待')
        dev_type = args.动作执行设备
        terminal_info = get_terminal_info(envs[evn]["云端环境_v"], mysql_info, args.APP用户名, args.APP密码, log_path)
        directDid = args.动作设备所在网关
        add_subDevices(args, log_path, dev_type, action_homeId, terminal_info, directDid=directDid, dev=2, direct_dev_type=direct_dev_type)
        get_log(log_path).info(f'       ----       动作执行设备添加完成')
        time.sleep(2)
        if args.执行动作 == "手动配置":
            # 创建确认对话框
            message = f"设备已添加成功，请手动配置联动场景，配置完成后点击'确认'按钮！"
            confirmed = messagebox.askyesno("确认", message)
            # 根据用户的选择执行操作
            if confirmed:
                pass
            else:
                get_log(log_path).info(f'    !!!!    取消配置，停止测试')
                sys.exit()
        elif args.执行动作 == "开关":
            pass
        else:
            get_log(log_path).error(f'    !!!!    不支持的联动执行动作，停止测试')
            sys.exit()
        get_log(log_path).info(f'Step 3：开始执行测试并进行监控...')
        nums = args.测试轮询次数
        interval = args.测试间隔时长
        if args.条件执行设备 == "人体存在传感器":
            time_summary = {"someone": [], "noone": []}
            for num in range(0, int(nums)):
                action_ip = ips[2]
                get_log(log_path).info(f'    ----    第{num+1}次触发有人状态')
                usr_tcp232_t2_tool_clear_buff(log_path, action_ip)
                start_time = time.time()
                usr_tcp232_t2_tool_clear_buff(log_path, action_ip)
                for dev_n in range(0, int(dev_num)):
                    send_data = "01 04 06 18 4A 0A 00 00 18 01"
                    condition_ip = ips[dev_n]
                    usr_tcp232_t2_tool(log_path, condition_ip, send_data=send_data)
                recv_mes = usr_tcp232_t2_tool_recv(log_path, action_ip)
                end_time = time.time()
                spend_time = end_time - start_time
                get_log(log_path).info(f"    ----    接收到动作设备被控数据{recv_mes}，用时 {spend_time} S")
                time_summary['someone'].append(spend_time)
                time.sleep(10)
                get_log(log_path).info(f'    ----    第{num + 1}次触发无人状态')
                usr_tcp232_t2_tool_clear_buff(log_path, action_ip)
                start_time = time.time()
                for dev_n in range(0, int(dev_num)):
                    send_data = "01 04 06 18 4B 0A 00 00 18 00"
                    condition_ip = ips[dev_n]
                    usr_tcp232_t2_tool(log_path, condition_ip, send_data=send_data)
                recv_mes = usr_tcp232_t2_tool_recv(log_path, action_ip)
                end_time = time.time()
                spend_time = end_time - start_time
                get_log(log_path).info(f"    ----    接收到动作设备被控数据{recv_mes}，用时 {spend_time} S")
                time_summary['noone'].append(spend_time)
                if num != int(nums-1):
                    get_log(log_path).info(f' ---- {interval}S后进行下一轮测试')
                    time.sleep(int(interval))
            get_log(log_path).info(f'Step 4：测试结束，测试数据整理中...')
            for k, v in time_summary.items():
                time_data = v
                interval2 = 0.5
                max_time = max(time_data)
                # 计算区间数
                num_intervals = int(np.ceil(max_time / interval2))
                interval_counts = [0] * num_intervals  # 初始化区间计数器
                for t in time_data:  # 统计每个区间的数据个数
                    interval_index = int(t // interval2)
                    interval_counts[interval_index] += 1
                total_count = len(time_data)
                interval_percentages = [(count / total_count) * 100 for count in interval_counts]
                # 打印每个区间的占比
                get_log(log_path).info(f'    ----    {k}联动场景共计测试{int(nums)}次，用时统计如下：')
                for i, (count, percentage) in enumerate(zip(interval_counts, interval_percentages)):
                    lower_bound = i * interval2
                    upper_bound = (i + 1) * interval2
                    get_log(log_path).info(f"      ----      {lower_bound}-{upper_bound}s: {percentage:.2f}% ({count} 次)")
        elif args.条件执行设备 == "温湿度传感器":
            time_summary = {"high_temperature": [], "low_temperature": []}
            for num in range(0, int(nums)):
                action_ip = ips[2]
                get_log(log_path).info(f'    ----    第{num + 1}次触发温度高于26℃（27℃）')
                usr_tcp232_t2_tool_clear_buff(log_path, action_ip)
                start_time = time.time()
                usr_tcp232_t2_tool_clear_buff(log_path, action_ip)
                for dev_n in range(0, int(dev_num)):
                    send_data = "01 04 02 08 40 0A 00 00 29 8C 0A"
                    condition_ip = ips[dev_n]
                    usr_tcp232_t2_tool(log_path, condition_ip, send_data=send_data)
                recv_mes = usr_tcp232_t2_tool_recv(log_path, action_ip)
                end_time = time.time()
                spend_time = end_time - start_time
                get_log(log_path).info(f"    ----    接收到动作设备被控数据{recv_mes}，用时 {spend_time} S")
                time_summary['high_temperature'].append(spend_time)
                time.sleep(10)
                get_log(log_path).info(f'    ----    第{num + 1}次触发温度低于26℃（21℃）')
                usr_tcp232_t2_tool_clear_buff(log_path, action_ip)
                start_time = time.time()
                for dev_n in range(0, int(dev_num)):
                    send_data = "01 04 02 08 40 0A 00 00 29 34 08"
                    condition_ip = ips[dev_n]
                    usr_tcp232_t2_tool(log_path, condition_ip, send_data=send_data)
                recv_mes = usr_tcp232_t2_tool_recv(log_path, action_ip)
                end_time = time.time()
                spend_time = end_time - start_time
                get_log(log_path).info(f"    ----    接收到动作设备被控数据{recv_mes}，用时 {spend_time} S")
                time_summary['low_temperature'].append(spend_time)
                if num != int(nums - 1):
                    get_log(log_path).info(f' ---- {interval}S后进行下一轮测试')
                    time.sleep(int(interval))
            get_log(log_path).info(f'Step 4：测试结束，测试数据整理中...')
            for k, v in time_summary.items():
                time_data = v
                interval2 = 0.5
                max_time = max(time_data)
                # 计算区间数
                num_intervals = int(np.ceil(max_time / interval2))
                interval_counts = [0] * num_intervals  # 初始化区间计数器
                for t in time_data:  # 统计每个区间的数据个数
                    interval_index = int(t // interval2)
                    interval_counts[interval_index] += 1
                total_count = len(time_data)
                interval_percentages = [(count / total_count) * 100 for count in interval_counts]
                # 打印每个区间的占比
                get_log(log_path).info(f'    ----    {k}联动场景共计测试{int(nums)}次，用时统计如下：')
                for i, (count, percentage) in enumerate(zip(interval_counts, interval_percentages)):
                    lower_bound = i * interval2
                    upper_bound = (i + 1) * interval2
                    get_log(log_path).info(
                        f"      ----      {lower_bound}-{upper_bound}s: {percentage:.2f}% ({count} 次)")
        else:
            get_log(log_path).error(f'    !!!!    暂不支持此条件执行设备，敬请期待')
            sys.exit()
        # 关闭数据库、mqtt链接
        try:
            db_tool.dispose()
        except Exception as e:
            get_log(log_path).debug(f'关闭数据库链接发生如下错误：{e}')
    else:
        get_log(log_path).error(f'    !!!!    暂不支持此场景的测试监控，敬请期待')
        sys.exit()
