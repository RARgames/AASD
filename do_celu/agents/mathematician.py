#
# do_celu
#
# Copyright 2022 Agenty 007
#

from time import sleep
from spade import agent, quit_spade
from do_celu.behaviours import BaseOneShotBehaviour
from spade.message import Message
from logging import Logger
from do_celu.utils.performatives import Performatives
from do_celu.entities.connection import ConnectionRequest, Connection
from do_celu.utils.job_exit_code import JobExitCode
from do_celu.config import Config, get_config
from do_celu.context import get_logger

graph=[ [ 0 , 4 ,20 ,16 ,14 ,17 , 3 , 8 ,19 ,19 ],
        [ 4 , 0 , 6 ,11 ,20 , 1 ,13 ,10 , 8 , 3 ],
        [ 20 , 6 , 0 , 1 , 1 , 7 , 5 ,19 ,13 ,19],
        [ 16 ,11 , 1 , 0 ,10 ,15 , 4 , 2 ,10 , 6],
        [ 14 ,20 , 1 ,10 , 0 , 3 , 8 , 7 , 8 , 5],
        [ 17 , 1 , 7 ,15 , 3 , 0 , 3 ,15 , 7 ,12],
        [ 3 ,13 , 5 , 4 , 8 , 3 , 0 ,15 ,12 , 6 ],
        [ 8 ,10 ,19 , 2 , 7 ,15 ,15 , 0 ,15 ,11 ],
        [19 , 8 ,13 ,10 , 8 , 7 ,12 ,15 , 0 , 9 ],
        [19 , 3 ,19 , 6 , 5 ,12 , 6 ,11 , 9 , 0 ]]

LOGGER_NAME = get_config().MATHEMATICIAN_LOGGER_NAME


class MathematicianAgent(agent.Agent):
    # Behaviours:
    inform_best_path: 'InformBestPath'
    receive_client_demand: 'ReciveClientDemand'
    receive_bus_routes: 'ReceiveBusRoutes'

    # Agent state:
    _logger: Logger
    _config: Config

    def __init__(self, jid: str, password: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security=verify_security)
        self._config = get_config()
        self._logger = get_logger(LOGGER_NAME)

    class InformBestPath(BaseOneShotBehaviour):
        agent: 'MathematicianAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('InformBestPath running...')

        def tsp(needed, busroutes):
            nbuses = len(busroutes)
            for i in range (len(needed)):
                temp = 0
                mincost = 9999
                for j in range (nbuses):
                    currcost = 0
                    busroute = busroutes[j]
                    if len(busroutes[j]) == 1:
                        temp = j
                        break
                    else:
                        temp2 = needed[i]
                        for k in range (len(busroutes[j])-1):
                            currcost += graph[busroute[k]][busroute[k+1]]
                        if temp2[0] == busroute[len(busroute)-1]:
                            currcost = currcost + graph[busroute[len(busroute)-1]][needed[i][1]]
                        else:
                            currcost = currcost + graph[busroute[len(busroute)-1]][needed[i][0]] + graph[needed[i][0]][needed[i][1]]
                        if currcost<mincost:
                            mincost = currcost
                            temp = j

            busroute = busroutes[temp]
            temp2 = needed[i]
            if busroute[len(busroute)-1] != temp2[0]:
                busroute.append(0)
                busroute[len(busroute)-1] = temp2[0]
            busroute.append(0)
            busroute[len(busroute)-1] = temp2[1]
            busroutes.pop(temp)
            busroutes.insert(temp,busroute)
            return busroutes

        async def run(self):
            self._logger.debug("Calculating the best route.")
            # busroutes = tsp()
            msg = Message(to=self._config.MANAGER_JID)
            msg.set_metadata("performative", Performatives.INFORM)
            #msg.body = 
            try:
                await self.send(msg)
                self._logger.debug("Sending the best routes!")
            except Exception as e:
                self._logger.error(e)
                self.kill(JobExitCode.FAILURE)
                return

        async def on_end(self):
            self._logger.debug(f'InformBestPath ended')

    class ReciveClientDemand(BaseOneShotBehaviour):
        agent: 'MathematicianAgent'

        def __init__(self, ):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('ReciveClientDemand running...')

        async def run(self):
            msg = await self.receive(timeout=30)
            msg.set_metadata("performative", Performatives.REQUEST)
            if msg:
                self._logger.debug(f'ReciveClientDemand msg received with body: {msg.body}')
                # TODO trigger getting the data
                self.exit_code = JobExitCode.SUCCESS
            else:
                self.exit_code = JobExitCode.FAILURE

        async def on_end(self):
            self._logger.debug(f'ReciveClientDemand ended with status: {self.exit_code.name}')

    class ReceiveBusRoutes(BaseOneShotBehaviour):
        agent: 'MathematicianAgent'

        def __init__(self, ):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('ReceiveBusRoutes running...')

        async def run(self):
            msg = await self.receive(timeout=30)
            msg.set_metadata("performative", Performatives.REQUEST)
            if msg:
                self._logger.debug(f'ReceiveBusRoutes msg received with body: {msg.body}')
                # TODO trigger getting the data
                self.exit_code = JobExitCode.SUCCESS
            else:
                self.exit_code = JobExitCode.FAILURE

        async def on_end(self):
            self._logger.debug(f'ReceiveBusRoutes ended with status: {self.exit_code.name}')

    async def setup(self):
        self._logger.info('MathematicianAgent started')

        self._logger.info('MathAgent started')
        await self._setup_ReciveClientDemand()
        await self._setup_ReceiveBusRoutes()
        await self._setup_InformBestPath()

        self.add_behaviour(self.ReciveClientDemand)
        self.add_behaviour(self.ReceiveBusRoutes)
        self.add_behaviour(self.InformBestPath)

    async def _setup_ReciveClientDemand(self):
        self.receive_client_demand = self.RequestAvailableConnections()
    async def _setup_ReceiveBusRoutes(self):
        self.receive_bus_routes = self.RequestAvailableConnections()
    async def _setup_InformBestPath(self):
        self.inform_best_path = self.RequestAvailableConnections()


if __name__ == '__main__':
    config = get_config()
    logger = get_logger(config.MATHEMATICIAN_LOGGER_NAME)
    mathematician = MathematicianAgent(
        config.MATHEMATICIAN_JID,
        config.MATHEMATICIAN_PASSWORD,
    )

    future = mathematician.start()
    future.result()

    while mathematician.is_alive():
        try:
            sleep(1)
        except KeyboardInterrupt:
            break

    mathematician.stop()
    logger.debug('Mathematician agent stopped')
    quit_spade()