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
            try:
                con_string = "netsh wlan connect ssid=system_ANAList name=system_ANAList"
                subprocess.run(con_string, capture_output=True, text=True).stdout
                self.wifi_state = False
            except Exception:
                print(Exception)

        await self.build_spawn()
        await self.build_extractor()
        await self.create_drones()
        await self.distribute_workers()

    async def create_drones(self):
        if self.can_afford(UnitTypeId.DRONE):
            await self.train(UnitTypeId.DRONE, amount=1)

    async def build_extractor(self):
        for hatchery in self.townhalls:
            vaspenes = self.vespene_geyser.closer_than(15.0, hatchery)
            if self.can_afford(UnitTypeId.EXTRACTOR):
                await self.build(UnitTypeId.EXTRACTOR, vaspenes[0])

    async def build_spawn(self):
        if self.can_afford(UnitTypeId.SPAWNINGPOOL) and self.already_pending(
                UnitTypeId.SPAWNINGPOOL) + self.structures.filter(
                lambda structure: structure.type_id == UnitTypeId.SPAWNINGPOOL and structure.is_ready).amount == 0:
            map_center = self.game_info.map_center
            position_towards_map_center = self.start_location.towards(map_center, distance=5)
            await self.build(UnitTypeId.SPAWNINGPOOL, near=position_towards_map_center, placement_step=1)


if __name__ == '__main__':
    dis_string = "netsh wlan disconnect"
    dis_con = subprocess.run(dis_string, capture_output=True, text=True).stdout
    sc2.run_game(
        sc2.maps.get("AcropolisLE"),
        [Bot(sc2.Race.Zerg, ZergBot()), Computer(sc2.Race.Zerg, sc2.Difficulty.Easy)],
        realtime=False,
    )
