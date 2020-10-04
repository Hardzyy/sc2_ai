import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON


class myBot(sc2.BotAI):
	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.buid_workers()
		await self.buid_pylon()

	async def buid_pylon(self):
		for 

	async def buid_workers(self):
		for nexus in self.units(NEXUS).ready.noqueue:
			if self.can_afford(PROBE):
				await self.do(nexus.train(PROBE))



run_game(maps.get('AbyssalReefLE'), [
	Bot(Race.Protoss, myBot()),
	Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)