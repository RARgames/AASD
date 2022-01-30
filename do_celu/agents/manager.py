#
# do_celu
#
# Copyright 2022 Agenty 007
#

import json
import re
from datetime import datetime
from logging import Logger
from time import sleep
from typing import Dict, Optional

import aioxmpp
from spade import agent, quit_spade
from spade.message import Message
from spade.presence import PresenceShow

from do_celu.behaviours import BasePeriodicBehaviour, BaseOneShotBehaviour, BaseCyclicBehaviour
from do_celu.messages.driver import RequestDriverDataMessage, PathChangeBody, RequestPathChangeMessage
from do_celu.messages.manager import ReceiveDriverDataBody, ReceiveDriverDataTemplate
from do_celu.utils.dataclass_json_encoder import DataclassJSONEncoder
from do_celu.utils.performatives import Performatives
from do_celu.config import Config, get_config
from do_celu.context import get_logger
from do_celu.utils.job_exit_code import JobExitCode

LOGGER_NAME = get_config().MANAGER_LOGGER_NAME
DRIVER_JID_REGEXP = re.compile(fr'^\w+{get_config().DRIVER_JID_SUFFIX}(/\d+)?$')


class ManagerAgent(agent.Agent):
    # Behaviours:
    request_all_drivers_data: 'RequestAllDriversData'
    request_driver_data: 'RequestDriverData'
    receive_driver_data: 'ReceiveDriverData'
    request_best_paths: 'RequestBestPaths'
    receive_best_paths: 'ReceiveBestPaths'
    inform_client_best_paths: 'InformClientBestPaths'
    cfp_client_choose_path: 'CFPClientChoosePath'
    receive_client_path_proposal: 'ReceiveClientPathProposal'
    inform_driver_path_change: 'InformDriverPathChange'
    accept_client_path_proposal: 'AcceptClientPathProposal'
    handle_subscriptions: 'HandleSubscriptions'

    # Agent state:
    _logger: Logger
    _config: Config
    _drivers_data: Dict[str, ReceiveDriverDataBody]

    def __init__(self, jid: str, password: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security=verify_security)
        self._config = get_config()
        self._logger = get_logger(LOGGER_NAME)
        self._drivers_data = {}

    def set_driver_data(self, jid: str, data: ReceiveDriverDataBody) -> None:
        self._drivers_data[jid] = data

    class RequestAllDriversData(BaseOneShotBehaviour):
        """
        Request data from all available dirvers.
        """
        agent: 'ManagerAgent'

        def __init__(self):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.info('RequestAllDriversData running...')

        async def run(self):
            for jid, info in self.agent.presence.get_contacts().items():
                self._logger.debug(f'Quering {jid}')
                presence: aioxmpp.Presence = info.get('presence', None)
                self._logger.debug(f'Presence {presence}')
                if DRIVER_JID_REGEXP.match(str(jid)) and presence and presence.type_ == aioxmpp.PresenceType.AVAILABLE:
                    self.agent._add_request_driver_data(jid=str(jid))

            self.exit_code = JobExitCode.SUCCESS

        async def on_end(self):
            self._logger.info(f'RequestAllDriversData ended with status: {self.exit_code}')

    class RequestDriverData(BaseOneShotBehaviour):
        """Request a specified (jid) driver data."""
        agent: 'ManagerAgent'
        _jid: str

        def __init__(self, jid: str):
            super().__init__(LOGGER_NAME)
            self._jid = jid

        async def on_start(self):
            self._logger.info('RequestDriverData running...')

        async def run(self):
            msg = RequestDriverDataMessage(to=self._jid)
            await self.send(msg)
            self.exit_code = JobExitCode.SUCCESS

        async def on_end(self):
            self._logger.info(f'RequestDriverData ended with status: {self.exit_code}')

    class ReceiveDriverData(BaseCyclicBehaviour):
        """Handle data recivied from drivers and save it to dictionary (_drivers_data)."""
        agent: 'ManagerAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.info('ReceiveDriverData running...')

        async def run(self):
            msg = await self.receive()
            if msg:
                self._logger.debug(f'Message received with content: {msg.body}')
                sender = str(msg.sender).split('/')[0]
                body = json.loads(msg.body)
                data = ReceiveDriverDataBody(**body)
                self._logger.debug(f'Sender: {sender} - Driver data: {vars(data)}')
                self.agent.set_driver_data(jid=sender, data=data)
                self.exit_code = JobExitCode.SUCCESS

        async def on_end(self):
            self._logger.info(f'ReceiveDriverData ended with status: {self.exit_code}')

    class RequestBestPaths(BaseOneShotBehaviour):
        agent: 'ManagerAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('RequestBestPaths running...')

        async def run(self):
            msg = Message(to=self._config.MATHEMATICIAN_JID)
            msg.set_metadata('performative', Performatives.REQUEST)
            await self.send(msg)

        async def on_end(self):
            self._logger.debug(f'RequestBestPaths ended with status: {self.exit_code.name}')

    class ReceiveBestPaths(BaseOneShotBehaviour):
        agent: 'ManagerAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('ReceiveBestPaths running...')

        async def run(self):
            msg = await self.receive(timeout=30)
            if msg:
                self._logger.debug(f'ReceiveBestPaths msg received with body: {msg.body}')
                # TODO send to client
                self.exit_code = JobExitCode.SUCCESS
            else:
                self.exit_code = JobExitCode.FAILURE

        async def on_end(self):
            self._logger.debug(f'ReceiveBestPaths ended with status: {self.exit_code.name}')

    class InformClientBestPaths(BaseOneShotBehaviour):
        agent: 'ManagerAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('InformClientBestPaths running...')

        async def run(self):
            msg = Message(to='client@localhost')  # TODO select good client
            msg.set_metadata('performative', Performatives.INFORM)
            # msg.body = #TODO
            await self.send(msg)
            self.exit_code = JobExitCode.SUCCESS

        async def on_end(self):
            self._logger.debug(f'InformClientBestPaths ended with status: {self.exit_code.name}')

    class CFPClientChoosePath(BaseOneShotBehaviour):
        agent: 'ManagerAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('CFPClientChoosePath running...')

        async def run(self):
            msg = Message(to='client@localhost')  # TODO select good client
            msg.set_metadata('performative', Performatives.CALL_FOR_PROPOSAL)
            # msg.body = #TODO
            await self.send(msg)
            self.exit_code = JobExitCode.SUCCESS

        async def on_end(self):
            self._logger.debug(f'CFPClientChoosePath ended with status: {self.exit_code.name}')

    class ReceiveClientPathProposal(BaseOneShotBehaviour):
        agent: 'ManagerAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('ReceiveClientPathProposal running...')

        async def run(self):
            msg = await self.receive(timeout=30)
            if msg:
                self._logger.debug(f'ReceiveClientPathProposal msg received with body: {msg.body}')
                # TODO send info to driver
                # TODO after that accept proposal
                self.exit_code = JobExitCode.SUCCESS
            else:
                self.exit_code = JobExitCode.FAILURE

        async def on_end(self):
            self._logger.debug(f'ReceiveClientPathProposal ended with status: {self.exit_code.name}')

    class InformDriverPathChange(BaseOneShotBehaviour):
        """Infrom a specific (jid) driver about his new path."""
        agent: 'ManagerAgent'
        _jid: str
        _data: PathChangeBody

        def __init__(self, jid: str, data: PathChangeBody):
            super().__init__(LOGGER_NAME)
            self._jid = jid
            self._data = data

        async def on_start(self):
            self._logger.info('InformDriverPathChange running...')

        async def run(self):
            msg = RequestPathChangeMessage(to=self._jid)
            msg.body = json.dumps(self._data, cls=DataclassJSONEncoder)
            await self.send(msg)
            self.exit_code = JobExitCode.SUCCESS

        async def on_end(self):
            self._logger.info(f'InformDriverPathChange ended with status: {self.exit_code}')

    class AcceptClientPathProposal(BaseOneShotBehaviour):
        agent: 'ManagerAgent'

        def __init__(self,):
            super().__init__(LOGGER_NAME)

        async def on_start(self):
            self._logger.debug('AcceptClientPathProposal running...')

        async def run(self):
            msg = Message(to='client@localhost')  # TODO select good client
            msg.set_metadata('performative', Performatives.ACCEPT_PROPOSAL)
            await self.send(msg)
            self.exit_code = JobExitCode.SUCCESS

        async def on_end(self):
            self._logger.debug(f'AcceptClientPathProposal ended with status: {self.exit_code.name}')

    class HandleSubscriptions(BasePeriodicBehaviour):
        """Monitor subscriptions to manager."""
        agent: 'ManagerAgent'

        def __init__(
            self,
            period: float,
            start_at: Optional[datetime] = None,
        ):
            super().__init__(period, logger_name=LOGGER_NAME, start_at=start_at)

        async def on_start(self):
            self._logger.info('SubscribeToManager running...')
            self.agent.presence.on_subscribe = self.on_subscribe
            self.agent.presence.on_unsubscribe = self.on_unsubscribe
            self.agent.presence.on_unsubscribed = self.on_unsubscribed
            self.agent.presence.on_subscribed = self.on_subscribed

        async def run(self):
            self._logger.debug('Checking contact list...')
            for jid, info in self.agent.presence.get_contacts().items():
                self._logger.debug(f"JID: {jid} - type: {info.get('presence', None)}")

        async def on_end(self):
            self._logger.info('SubscribeToManager ending...')

        def on_subscribe(self, jid: str):
            self._logger.info(f'Agent {jid} asked for subscription.')

            # Match dirvers JIDs
            if DRIVER_JID_REGEXP.match(jid):
                self.presence.approve(jid)
                self.presence.subscribe(jid)

        def on_unsubscribe(self, jid: str):
            self._logger.info(f'Agent {jid} asked for removeing subscription.')

            # Match dirvers JIDs
            if DRIVER_JID_REGEXP.match(jid):
                self.presence.approve(jid)
                self.presence.unsubscribe(jid)

        def on_unsubscribed(self, jid: str):
            self._logger.info(f'Agent {jid} asked for unsubscribed.')

        def on_subscribed(self, jid: str):
            self._logger.info(f'Agent {jid} accepted subscription.')

    async def setup(self):
        self._logger.info('ManagerAgent started')
        self._add_handle_subscriptions()
        self._add_receive_driver_data()

        # self.add_behaviour(self.RequestDriverData())
        # self.add_behaviour(self.ReceiveAvailableDriversRequest())
        # self.add_behaviour(self.ReceiveWelcomeDriverMsg())
        # self.add_behaviour(self.ReceiveDriverData())
        # self.add_behaviour(self.RequestBestPaths())
        # self.add_behaviour(self.ReceiveBestPaths())
        # self.add_behaviour(self.CFPClientChoosePath())
        # self.add_behaviour(self.ReceiveClientPathProposal())
        # self.add_behaviour(self.InformDriverPathChange())
        # self.add_behaviour(self.AcceptClientPathProposal())

        self._logger.info('Setting presence to AVAILABLE')
        self.presence.set_available(show=PresenceShow.FREE_FOR_CHAT)

    def _add_handle_subscriptions(self):
        self.handle_subscriptions = self.HandleSubscriptions(period=3)
        self.add_behaviour(self.handle_subscriptions)

    def _add_inform_driver_path_change(self, jid: str, data: PathChangeBody):
        self.inform_driver_path_change = self.InformDriverPathChange(jid=jid, data=data)
        self.add_behaviour(self.inform_driver_path_change)

    def _add_request_driver_data(self, jid: str):
        self.request_driver_data = self.RequestDriverData(jid=jid)
        self.add_behaviour(self.request_driver_data)

    def _add_request_all_drivers_data(self):
        self.request_all_drivers_data = self.RequestAllDriversData()
        self.add_behaviour(self.request_all_drivers_data)

    def _add_receive_driver_data(self):
        self.receive_inform_path_change_template = ReceiveDriverDataTemplate()
        self.receive_driver_data = self.ReceiveDriverData()
        self.add_behaviour(self.receive_driver_data, self.receive_inform_path_change_template)


if __name__ == '__main__':
    config = get_config()
    logger = get_logger(config.MANAGER_LOGGER_NAME)
    manager = ManagerAgent(
        config.MANAGER_JID,
        config.MANAGER_PASSWORD,
    )

    future = manager.start()
    future.result()

    sleep(10)
    manager._add_inform_driver_path_change(jid='1_driver@localhost', data=PathChangeBody(path=[1, 2, 1]))
    manager._add_inform_driver_path_change(jid='2_driver@localhost', data=PathChangeBody(path=[2, 2, 2]))
    manager._add_inform_driver_path_change(jid='3_driver@localhost', data=PathChangeBody(path=[3, 2, 3]))
    sleep(10)
    manager._add_request_all_drivers_data()

    while manager.is_alive():
        try:
            sleep(1)
        except KeyboardInterrupt:
            break

    manager.stop()
    logger.debug('Manager agent stopped')
    quit_spade()
