import json
import requests
import rumps
import hashlib
import time
import random
from datetime import datetime
from ImageCache import load_image
from GeshinNotifier import GenshinNotifier


API_APP_VERSION = "2.12.1"
API_SALT = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"


class GeshinStatusBarApp(rumps.App):
    base_url = "https://api-takumi.mihoyo.com/game_record/app/genshin/api/dailyNote"
    headers = {
        "Host": "api-takumi.mihoyo.com",
        "x-rpc-client_type": "5",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://webstatic.mihoyo.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/" + API_APP_VERSION,
        "Connection": "keep-alive",
        "x-rpc-app_version": API_APP_VERSION,
        "Referer": "https://webstatic.mihoyo.com/"
    }
    
    def __init__(self):
        super(GeshinStatusBarApp, self).__init__("Geshin", icon='Paimon.jpeg', quit_button="退出")
        self.resin_notifier = GenshinNotifier(40)
        self.resin_full_notifier = GenshinNotifier(160, GenshinNotifier.NOTIFY_TYPE_UNTIL)
        self.plugins = [self._get_resin, self._get_week_boss, self._get_task,  self._get_expedition, self._get_update_time]
        
        updater = rumps.Timer(self.update_menu, 30)
        updater.start()
    
    def update_menu(self, _):
        self.menu.clear()
        self.menu = self._update_data() + [None] + [rumps.MenuItem("刷新", self.update_menu), self.quit_button]
    
    def _update_data(self):
        try:
            self._load_config()
        except Exception as e:
            return ["读取配置错误", str(e)]
        try:
            res = requests.get(self.url, headers=self.headers).json()
        except Exception as e:
            return ["网络请求错误", str(e)]
        
        if res['retcode'] != 0:
            return [
                "请求错误",
                f"返回值为: {res['retcode']}"
            ]
        data = res['data']
        info_lst = sum([f.__call__(data) for f in self.plugins], [])
        
        return [rumps.MenuItem(item, callback=self._do_nothing) if isinstance(item, str) else item for item in info_lst]
    
    def _get_resin(self, data):
        current_resin = data['current_resin']
        max_resin = data['max_resin']
        resin_recovery_second = int(data['resin_recovery_time'])
        resin_recovery_hh = resin_recovery_second // 3600
        resin_recovery_mm = resin_recovery_second % 3600 // 60
        if self.resin_notifier.trigger(current_resin):
            rumps.notification("Genshin", "体力已恢复40", f"树脂：{current_resin} / {max_resin}")
        
        if self.resin_full_notifier.trigger(current_resin):
            rumps.notification("Genshin", "体力已满", f"树脂：{current_resin} / {max_resin}")
        
        return [
            f"原萃树脂：{current_resin} / {max_resin}",
            f"完全恢复：{resin_recovery_hh}小时{resin_recovery_mm}分后"
        ]
    
    def _get_task(self, data):
        finished_task_num = data['finished_task_num']
        total_task_num = data['total_task_num']
        is_extra_task_reward_received = data['is_extra_task_reward_received']
        return [f"每日任务：{finished_task_num} / {total_task_num}",
                f"额外奖励：{'已领取' if is_extra_task_reward_received else '未领取'}"]
    
    def _get_expedition(self, data):
        current_expedition_num = data['current_expedition_num']
        max_expedition_num = data['max_expedition_num']

        expeditions = data['expeditions']

        expeditions_arr = []
        for exp in expeditions:
            icon = exp["avatar_side_icon"]
            status = exp['status']
            remained_second = int(exp['remained_time'])
            remained_hh = remained_second // 3600
            remained_mm = remained_second % 3600 // 60
            item = rumps.MenuItem(f"{status}: 剩余{remained_hh}小时{remained_mm}分", icon=load_image(icon), callback=self._do_nothing)
            if status != 'Ongoing':
                item.state = 1
            expeditions_arr.append(item)
        
        return [{f"探索派遣：{current_expedition_num} / {max_expedition_num}": expeditions_arr}]
    
    def _get_week_boss(self, data):
        remain_resin_discount_num = data['remain_resin_discount_num']
        resin_discount_num_limit = data['resin_discount_num_limit']
        return [f"剩余周本：{remain_resin_discount_num} / {resin_discount_num_limit}"]
    
    def _get_update_time(self, _):
        return [f"更新时间：{datetime.now().strftime('%H:%M:%S')}"]

    def _do_nothing(self, sender):
        pass

    def _load_config(self):
        with open("config.json") as f:
            config = json.load(f)
            query = f"role_id={config['UID']}&server={config['server']}"
            self.url = self.base_url + "?" + query
            self.headers['Cookie'] = config['Cookie']
            self.headers['DS'] = self._get_DS(q=query)
    
    def _get_DS(self, q="", b=""):
        timestamp = str(int(time.time()))
        randomStr = (''.join(random.sample('123456789', 6))).upper()
        s = f"salt={API_SALT}&t={timestamp}&r={randomStr}&b={b}&q={q}"
        m = hashlib.md5()
        m.update(s.encode())
        return ",".join(map(str, [timestamp, randomStr, m.hexdigest()]))


if __name__ == "__main__":
    app = GeshinStatusBarApp()
    app.run()
