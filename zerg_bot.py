import subprocess

import sc2
from sc2.position import Point2, Point3
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.constants import *


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

        hatch: Unit = self.townhalls[0]

        if(
            self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) == 0
            and self.can_afford(UnitTypeId.EXTRACTOR)
            and self.workers
        ):
            worker: Unit = self.workers.random
            gas: Unit = self.vespene_geyser.closest_to(worker)
            worker.build_gas(gas)

        if(
            self.gas_buildings.ready
            and self.workers
        ):
            gas: Unit = self.gas_buildings.first
            if gas.surplus_harvesters < 0:
                self.workers.random.gather(gas)

        if(
            self.can_afford(UnitTypeId.DRONE)
            and self.supply_workers < 19
        ):
            self.train(UnitTypeId.DRONE)

        if(
            self.can_afford(UnitTypeId.SPAWNINGPOOL)
            and not self.already_pending(UnitTypeId.SPAWNINGPOOL)
            and self.structures(UnitTypeId.SPAWNINGPOOL).amount == 0
        ):
            for d in range(4, 15):
                pos: Point2 = hatch.position.towards(self.game_info.map_center, d)
                if await self.can_place_single(UnitTypeId.SPAWNINGPOOL, pos):
                    worker: Unit = self.workers.closest_to(pos)
                    worker.build(UnitTypeId.SPAWNINGPOOL, pos)

        if(
            self.supply_left < 2
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.already_pending(UnitTypeId.OVERLORD) < 1
        ):
            self.train(UnitTypeId.OVERLORD)

        if(
            self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0
            and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED)
        ):
            spawn_pool: Unit = self.structures(UnitTypeId.SPAWNINGPOOL).ready
            if spawn_pool:
                self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)

        if(
            self.can_afford(UnitTypeId.QUEEN)
            and self.units(UnitTypeId.QUEEN).amount + self.already_pending(UnitTypeId.QUEEN) < self.townhalls.amount
            and self.structures(UnitTypeId.SPAWNINGPOOL).ready
        ):
            self.train(UnitTypeId.QUEEN)

        for queen in self.units(UnitTypeId.QUEEN):
            if queen.energy >= 25 and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                queen(AbilityId.EFFECT_INJECTLARVA, hatch)

        if (
            self.can_afford(UnitTypeId.ZERGLING)
            and self.structures(UnitTypeId.SPAWNINGPOOL).ready
            and self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED)
        ):
            self.train(UnitTypeId.ZERGLING)

        target: Point2 = self.enemy_structures.not_flying.random_or(self.enemy_start_locations[0]).position

        # Give all zerglings an attack command
        if self.units(UnitTypeId.ZERGLING).amount > 14:
            for zergling in self.units(UnitTypeId.ZERGLING):
                zergling.attack(target)



if __name__ == '__main__':
    dis_string = "netsh wlan disconnect"
    dis_con = subprocess.run(dis_string, capture_output=True, text=True).stdout
    sc2.run_game(
        sc2.maps.get("AcropolisLE"),
        [Bot(sc2.Race.Zerg, ZergBot()), Computer(sc2.Race.Zerg, sc2.Difficulty.Hard)],
        realtime=False,
    )
