from concurrent.futures import ThreadPoolExecutor, Future

import asyncio
class XyTask:

    def __init__(self, max_workers=20):
        """
        初始化线程池
        :param max_workers: 最大并发线程数
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []  # 用于存储任务的 Future 对象

    def submit_task(self, func, data, secKillStart,title:str) -> Future:
        """
        提交任务到线程池
        :param func: 任务函数
        :param args: 任务函数的位置参数
        :param kwargs: 任务函数的关键字参数
        :return: Future 对象（可用于获取任务执行结果）
        """
        future = self.executor.submit(func, data, secKillStart,title)
        # self.futures.append(future)
        return future

    def get_results(self, wait=True):
        """
        获取所有任务的执行结果
        :param wait: 是否等待所有任务完成
        :return: 任务执行结果的列表
        """
        results = []
        for future in self.futures:
            if wait:
                results.append(future.result())  # 阻塞等待结果
            elif future.done():
                results.append(future.result())  # 仅获取已完成的任务
        return results

    def shutdown(self):
        """ 关闭线程池，释放资源 """
        self.executor.shutdown(wait=True)
