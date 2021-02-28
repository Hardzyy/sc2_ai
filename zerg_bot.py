import subprocess

import sc2
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId


class ZergBot(BotAI):
    def __init__(self):
        # чтобы достать name нужно в cmd
        # netsh wlan export profile name="Название сети" folder="C:\Users\Lenovo\Desktop\" key=clear
        # тут и найти name
        self.wifi_state = True
        self.wifi_ssid = "system_ANAList"
        self.wifi_name = "system_ANAList"

    async def on_step(self, iteration: int):
        # windows only!!!
        # сделано чтобы отключаться от wi-fi в момент запуска
        # если не сделать, теряем время из-за ping'ов до сервера
        if self.wifi_state:
            con_string = "netsh wlan connect ssid=system_ANAList name=system_ANAList"
            subprocess.run(con_string, capture_output=True, text=True).stdout
            self.wifi_state = False






if __name__=='__main__':
    dis_string = "netsh wlan disconnect"
    dis_con = subprocess.run(dis_string, capture_output=True, text=True).stdout
    sc2.run_game(
      sc2.maps.get("AcropolisLE"),
      [Bot(sc2.Race.Zerg, ZergBot()), Computer(sc2.Race.Zerg, sc2.Difficulty.Easy)],
      realtime=False,
    )




