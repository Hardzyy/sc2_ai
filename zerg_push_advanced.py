import subprocess

import sc2
from sc2.position import Point2, Point3
from sc2.bot_ai import BotAI
from sc2.player import Bot, Computer
# from sc2.ids.unit_typeid import UnitTypeId
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
        self.ITER_PER_MIN = 165

    async def on_step(self, iteration: int):
        # windows only!!!
        # сделано чтобы отключаться от wi-fi в момент запуска
        # если не сделать, теряем время из-за ping'ов до сервера
        self.iteration = iteration
        if self.wifi_state:
            try:
                con_string = "netsh wlan connect ssid=system_ANAList name=system_ANAList"
                subprocess.run(con_string, capture_output=True, text=True).stdout
                self.wifi_state = False
            except Exception:
                print(Exception)

        hatch: Unit = self.townhalls[0]
        target: Point2 = self.enemy_structures.not_flying.random_or(self.enemy_start_locations[0]).position
        # создаем все козявки
        await self.create_workers()
        await self.create_overlord()
        await self.create_gas()
        await self.create_queen()
        await self.create_lavra()
        await self.create_zergling()

        await self.create_hatch()
        #
        await self.distribute_workers()
        await self.get_movespeed()

        await self.build_spawning()
        await self.push(target)

    async def create_hatch(self):
        if (
           self.gas_buildings.amount
           and self.townhalls.amount * 16 + self.gas_buildings.amount * 3 == self.units(UnitTypeId.DRONE).amount
           and self.units(UnitTypeId.QUEEN)
        ):
            await self.expand_now()

    async def create_lavra(self):
        for hatch in self.townhalls:
            for queen in self.units(UnitTypeId.QUEEN):
                if queen.energy >= 25 and not self.townhalls[0].has_buff(BuffId.QUEENSPAWNLARVATIMER):
                    queen(AbilityId.EFFECT_INJECTLARVA, hatch)


    async def create_zergling(self):
        if (
            self.can_afford(UnitTypeId.ZERGLING)
            and self.structures(UnitTypeId.SPAWNINGPOOL).ready
            and self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED)
        ):
            self.train(UnitTypeId.ZERGLING)

    async def create_queen(self):
        if (
            self.can_afford(UnitTypeId.QUEEN)
            and self.units(UnitTypeId.QUEEN).amount + self.already_pending(UnitTypeId.QUEEN) < self.townhalls.amount
            and self.structures(UnitTypeId.SPAWNINGPOOL).ready
        ):
            self.train(UnitTypeId.QUEEN)

    async def build_spawning(self):
        for hatch in self.townhalls:
            if (
                self.can_afford(UnitTypeId.SPAWNINGPOOL)
                and not self.already_pending(UnitTypeId.SPAWNINGPOOL)
                and self.structures(UnitTypeId.SPAWNINGPOOL).amount == 0
            ):
                for d in range(4, 15):
                    pos: Point2 = hatch.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.SPAWNINGPOOL, pos):
                        worker: Unit = self.workers.closest_to(pos)
                        worker.build(UnitTypeId.SPAWNINGPOOL, pos)

    async def create_overlord(self):
        if (
            self.supply_left < 2
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.already_pending(UnitTypeId.OVERLORD) < 1
        ):
            self.train(UnitTypeId.OVERLORD)

    async def create_workers(self):
        if (
            self.can_afford(UnitTypeId.DRONE)
            and not self.already_pending(UnitTypeId.DRONE)
            and self.townhalls.amount * 16 + self.gas_buildings.amount*3
                >= self.units(UnitTypeId.DRONE).amount
        ):
            self.train(UnitTypeId.DRONE)

    # Give all zerglings an attack command
    async def push(self, target):
        if self.units(UnitTypeId.ZERGLING).amount > 14:
            for zergling in self.units(UnitTypeId.ZERGLING):
                zergling.attack(target)

    async def get_movespeed(self):
        if (
            self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0
            and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED)
        ):
            spawn_pool: Unit = self.structures(UnitTypeId.SPAWNINGPOOL).ready
            if spawn_pool:
                self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)

    async def harvest_gas(self):
        if (
            self.gas_buildings.ready
            and self.workers
        ):
            gas: Unit = self.gas_buildings.first
            if gas.surplus_harvesters < 0:
                self.workers.random.gather(gas)

    # creating extractor if doesn't exists and can apply
    async def create_gas(self):
        if (
            self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) == 0
            and self.can_afford(UnitTypeId.EXTRACTOR)
            and self.workers
            and self.townhalls.amount * 16 + self.gas_buildings.amount * 3
                == self.units(UnitTypeId.DRONE).amount
        ):
            worker: Unit = self.workers.random
            gas: Unit = self.vespene_geyser.closest_to(worker)
            worker.build_gas(gas)


if __name__ == '__main__':
    dis_string = "netsh wlan disconnect"
    dis_con = subprocess.run(dis_string, capture_output=True, text=True).stdout
    sc2.run_game(
        sc2.maps.get("AcropolisLE"),
        [Bot(sc2.Race.Zerg, ZergBot()), Computer(sc2.Race.Protoss, sc2.Difficulty.Hard)],
        realtime=False,
    )
