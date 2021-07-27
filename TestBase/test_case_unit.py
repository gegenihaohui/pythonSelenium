# -*- coding:utf-8 -*-
import unittest
from TestBase.browser_action import get_driver_func
from Common.com_func import log
from Config import global_var as gv
from Tools.mongodb import MongodbUtils
from Env import env_config as cfg
from Common.test_func import mongo_exception_send_DD


class ParaCase(unittest.TestCase):

    def __init__(self, pro_name, test_method="test_", browser_name="Chrome", remote=False, driver=None):
        """
        :param pro_name:
        :param test_method:
        :param browser_name:
        :param remote:
        :param driver:
         【 注意：'test_method'这个参数必须是测试类中存在的以'test_'开头的方法 】
        """
        super(ParaCase, self).__init__(test_method)
        self.driver = driver
        self.log = log
        self.pro_name = pro_name
        self.test_method = test_method
        self.screen_shot_id_list = []  # 截图ID列表
        self.screen_shot_id_list_name = self.__class__.__name__ + "." + test_method  # 截图ID列表名称
        self.class_method_path = self.__class__.__name__ + "/" + test_method + "/"  # 获取当前的'类名/方法名/'(提供截屏路径)
        self.driver_func = get_driver_func(pro_name=pro_name, browser_name=browser_name, remote=remote)  # 获取浏览器驱动方法
        self.thread_name_index = 0  # 记录当前线程名的索引（目的：不同线程使用不同的登录账号）

    def setUp(self):
        self.driver = self.driver_func()  # 启动浏览器驱动
        self.driver.implicitly_wait(gv.IMPLICITY_WAIT)  # 隐式等待时间
        self.driver.set_page_load_timeout(gv.PAGE_LOAD_TIME)  # 页面加载超时

        # 通过线程名的索引 获取登录账号
        from Config.pro_config import get_login_accout
        self.user, self.passwd = get_login_accout(self.thread_name_index)

        # 通过 cookie 进行登录
        # self.driver.add_cookie({"name": "xxxxx", "value": "xxxxxxx"})

        # self.driver.maximize_window()
        # self.driver.set_window_size(width=2000, height=1300)
        # self.driver.set_script_timeout()  # 页面异步js执行超时

    def tearDown(self):
        self.driver.quit()

    @staticmethod
    def get_online_case_to_suite(pro_name, browser_name="Chrome", remote=False, driver=None):
        """
        将'测试类'列表中的'上线'的'测试方法'添加入 suite 实例对象中
        :param pro_name:
        :param browser_name:
        :param remote:
        :param driver:
        :return:
        【 添 加 步 骤 】
        1.从mongo中获取'上线'状态的'测试用例'列表
        2.重置 上线用例的'运行状态：pending、开始时间：----、运行时间：----'
        3.通过'项目名称'获取'测试类'列表
        4.循环获取'测试类'列表中的所有'测试方法名称'
        5.将这些'测试方法名称'与mongo中'上线'的'测试方法名称'作比较
        6.匹配成功的，则实例化'测试用例'（一个实例对象仅包含一个测试类中的测试方法），并添加入'suite'实例对象中
        【 备 注 】
          实例化'测试类'时，必须带上该类中存在的以'test_'开头的方法名
        """
        with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
            try:
                # 获取上线用例列表
                query_dict = {"case_status": True}
                results = pro_db.find(query_dict, {"_id": 0})
                on_line_test_method_name_list = [result.get("test_method_name") for result in results]
                # 重置 上线用例的'运行状态：pending、开始时间：----、运行时间：----'
                update_dict = {"$set": {"run_status": "pending", "start_time": "----", "run_time": "----"}}
                pro_db.update(query_dict, update_dict, multi=True)
            except Exception as e:
                on_line_test_method_name_list = []
                mongo_exception_send_DD(e=e, msg="获取'" + pro_name + "'项目'上线'测试用例数据")
                return "mongo error", on_line_test_method_name_list

        from Config.pro_config import get_test_class_list
        test_class_list = get_test_class_list(pro_name)
        test_loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        for test_class in test_class_list:
            test_methods_name = test_loader.getTestCaseNames(test_class)
            for test_method_name in test_methods_name:
                # 匹配'测试方法'名称
                if test_method_name in on_line_test_method_name_list:
                    # 实例化测试用例对象（通过 self.driver_func 属性，将打开浏览器的操作进行了延迟处理）
                    test_instance = test_class(pro_name=pro_name, test_method=test_method_name,
                                               browser_name=browser_name, remote=remote, driver=driver)
                    suite.addTest(test_instance)
        return suite, on_line_test_method_name_list

