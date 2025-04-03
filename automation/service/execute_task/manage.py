import time

from selenium.webdriver.chrome.webdriver import WebDriver

from automation.request_config import RequestConfig
from automation.port import CollectApi, SecKillApi


class Manage:
    __driver: WebDriver
    __config: RequestConfig
    cookies: dict

    handlers: dict

    def __init__(self, driver: WebDriver, config: RequestConfig):
        self.cookies = config.getCookie()
        self.__driver = driver
        self.__config = config

        self.handlers = {
            'collect': CollectApi(config),
            'secKillApi': SecKillApi(config),
        }
        collect: CollectApi = self.handlers.get('collect')
        time.sleep(10)
        taskList = collect.sent()
        data: dict = taskList.get('data')
        if data:
            filtered_task_list = [
                {"id": item["id"], 'title': item['title']} for item in data.get('items', [])
                if item['itemStatus'] == 0
            ]
        secKill: SecKillApi = self.handlers.get('secKillApi')
        if filtered_task_list:
            # 进行日期排序
            secKill.sent(sorted(filtered_task_list,key=lambda x:x['title']),driver=driver)
