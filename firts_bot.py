import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE


class myBot(sc2.BotAI):
	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.buid_workers()


run_game(maps.get('AbyssalReefLE'), [
	Bot(Race.Protoss, myBot()),
	Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)