# -*- encoding=utf8 -*-
__author__ = "Administrator"
import itertools
import traceback

from airtest.core.api import *
from airtest.aircv import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import redis
import pymongo
import pandas as pd

import helper


class AirTestSpider:
    """
    airtest 抓取文本信息和触发点击事件，mitmproxy 抓取相关网络信息，通过 redis 通信
    """

    def __init__(self, device_host):
        auto_setup(__file__)

        self.device_1 = connect_device(f'android:///{device_host}?cap_method=javacap&touch_method=adb')
        self.poco = AndroidUiautomationPoco(self.device_1, screenshot_each_action=False)

        self.client = pymongo.MongoClient()
        self.dp_db = self.client['DianPing']

        self.wechat_db = self.client['WeChatOfficialAccount']
        self.wechat_col = self.wechat_db['wechat_search_info']
        self.pandas_col = self.wechat_db['pandas_info']

        self.redis_cli = redis.StrictRedis(decode_responses=True)
        self.biz_queue = 'wechat_biz'
        self.url_queue = 'article_url'

        self.wx_package_name = 'com.tencent.mm'
        self.city_en_list = ['星惠宝']

        self.count = 0

    def to_search_entrance(self):
        """
        进入微信搜索入口
        :return:
        """
        try:
            # poco('更多功能按钮').child("com.tencent.mm:id/iq").click()
            # poco(text='添加朋友').click()
            # poco(text='公众号').click()
            # 经过测试，下面代码速度同上面代码
            # poco("android.support.v7.widget.LinearLayoutCompat").child('更多功能按钮').child("com.tencent.mm:id/iq").click()
            # poco("com.tencent.mm:id/kp")[1].offspring('com.tencent.mm:id/cw').click()
            # poco('com.tencent.mm:id/d7v')[-2].offspring('android:id/title').click()

            # 点击首页搜索图标
            self.poco("com.tencent.mm:id/r_").wait_for_appearance()
            self.poco("com.tencent.mm:id/r_").click()
            # 搜索项选择公众号
            self.poco(text="公众号").click()
        except Exception as e:
            print('进入搜索入口失败')
            traceback.print_exc()

    def get_item_info(self, keyword):
        """
        获取搜索的公众号基础信息，不包括 biz 和 第一篇文章 url
        :param keyword:
        :return:
        """
        # 清空输入框
        self.poco("com.tencent.mm:id/m7").set_text('')
        # 点击输入框
        self.poco("com.tencent.mm:id/m7").click()
        # 输入关键词
        text(keyword, search=True)
        sleep(3)
        self.poco(name="搜一搜").wait_for_appearance()
        nodes = self.poco(name="搜一搜").children()
        print(len(nodes))

        gzhs_list = []

        last_first_name = ''
        while True:
            index_i = 0
            end_flag = False
            for node in nodes:
                gzh_dic = {}
                name = node.get_name()

                #判断是否开始
                if name in ["公众号"]:
                    continue
                
                # 判断是否结束
                if name in ["没有更多的搜索结果"]:
                    break
                if index_i == 0:
                    if last_first_name == name:
                        end_flag = True
                        break
                    index_i = index_i + 1
                    last_first_name = name
                print(name)
                if not keyword in name:
                    continue
                
                # 进入公众号
                node.focus([0.1, 0.1]).click()

                # 保存图像
                self.poco("com.tencent.mm:id/b7j").click()
                snapshot(filename=r"test.jpg")
                img_width, img_height = self.poco("android.widget.ImageView").get_position()
                img_size = self.poco("android.widget.ImageView").get_size()


                # self.poco("android.widget.ImageView").long_click()
                # self.poco("com.tencent.mm:id/dd").click()
                self.poco("android.widget.ImageView").click()

                # 获取公众号名称
                gzh_dic['名称'] = self.poco("com.tencent.mm:id/b7k").get_text()
                
                # 进入公众号具体页面
                try:
                    self.poco("com.tencent.mm:id/b7f").wait_for_appearance(timeout=5)
                except:
                    continue
                self.poco("com.tencent.mm:id/b7f").click()
                self.poco(name="关于公众号").wait_for_appearance()
                about_nodes = self.poco(name="关于公众号").children()

                # 获取公众号其他信息
                len_about_nodes = len(about_nodes)
                # tempalte = Template(r'qiye.png')
                # if exists(tempalte):
                #     print("企业单位")
                for i in range(len_about_nodes):
                    name = about_nodes[i].get_name()
                    if name == "公众号简介":
                        desc = about_nodes[i+1].get_name()
                        gzh_dic['简介'] = desc
                    if name == "微信号":
                        wechat_id = about_nodes[i+1].get_name()
                        gzh_dic['微信号'] = wechat_id
                    if name == "客服电话":
                        phone = about_nodes[i+1].get_name()
                        gzh_dic['电话'] = phone
                    if name == "帐号主体":
                        owner_node = about_nodes[i+1]
                        about_nodes[i].focus([0,0]).click()

                        self.poco(name="帐号主体").wait_for_appearance()
                        owner_nodes = self.poco(name="帐号主体").child("android.widget.ListView")[0].children()
                        owner_nodes_len = len(owner_nodes)
                        for owner_node_j in owner_nodes:
                            child_node = owner_node_j.children()
                            if child_node[0].get_name() == "企业全称":
                                full_name = child_node[1].get_name()
                                gzh_dic['full_name'] = full_name
                            if child_node[0].get_name() == "认证时间于":
                                auth_time = child_node[1].get_name()
                                gzh_dic['auth_time'] = auth_time
                            # if owner_nodes[i].get_name() == "企业全称":
                            #     full_name = owner_nodes[i+1].get_name()
                            #     print(full_name)
                            # if owner_nodes[i].get_name() == "企业全称":
                            #     full_name = owner_nodes[i+1].get_name()
                            #     print(full_name)
                            # if owner_nodes[i].get_name() == "企业全称":
                            #     full_name = owner_nodes[i+1].get_name()
                            #     print(full_name)

                gzhs_list.append(gzh_dic)

                self.poco("com.tencent.mm:id/m1").click()
                self.poco("com.tencent.mm:id/m1").click()

            end = self.poco(name="没有更多的搜索结果")

            if end_flag or end.exists():
                return gzhs_list
                break

            x, y = self.poco(name="搜一搜").get_position()
            end = [x, 0.1]
            start = [x, 0.99]
            self.poco.swipe(start, end)
            nodes = self.poco(name="搜一搜").children()
            sleep(1)

    def restart_app_to_search(self):
        stop_app(self.wx_package_name)
        start_app(self.wx_package_name)
        sleep(3)
        self.to_search_entrance()

    def inspect_current_page(self):
        """
        检测当前页面
        :return:
        """
        if self.poco("当前所在页面,与的聊天").exists():
            print('现在 app 在首页位置，准备进入搜索入口')
            self.to_search_entrance()
        elif self.poco("当前所在页面,搜一搜").exists():
            print('现在 app 在搜索入口，准备进行搜索')
        elif self.poco('com.tencent.mm:id/b1o').exists():
            print('现在在公众号信息页面，准备返回搜索入口')
            self.poco("com.tencent.mm:id/kb").click()
        else:
            print('app 页面未检测到，准备重启')
            self.restart_app_to_search()
        return

    def pandas_run_help(self, data):
        print('准备搜索公众号: ', data[0])
        if data[0] != '惠民宝':
            return
        self.inspect_current_page()
        item_info_dic = []
        while True:
            try:
                item_info_dic = self.get_item_info(data[0])
                break
            except Exception as e:
                    traceback.print_exc()
                    self.inspect_current_page()
        if len(item_info_dic):
            write = pd.ExcelWriter(os.getcwd() + "/wechat_app_spider/" + data[0]+".xlsx")
            df = pd.DataFrame(item_info_dic)
            df.to_excel(write, 'Sheet1')
            write.save()
        return

    def pandas_run(self):
        path = r'gzh.xlsx'
        print(os.getcwd())
        df = pd.read_excel(os.getcwd() + "/wechat_app_spider/" + path, header=None)
        df.apply(lambda x: self.pandas_run_help(x), axis=1)

        print("搜索完成")


def main():
    device_host = '127.0.0.1:7555'
    air_spider = AirTestSpider(device_host)
    air_spider.pandas_run()
    # air_spider.inspect_current_page()
    # air_spider.pandas_run()
    # air_spider.test_run()


if __name__ == '__main__':
    main()