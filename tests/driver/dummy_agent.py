#
# do_celu
#
# Copyright 2022 Agenty 007
#
import asyncio
import json
import time

from spade import agent, quit_spade
from spade.behaviour import CyclicBehaviour

from do_celu.messages.driver import RequestDriverDataMessage, RequestPathChangeMessage


class DummyAgent(agent.Agent):
    path_change: 'PathChange'
    driver_data: 'DriverData'

    class PathChange(CyclicBehaviour):
        iterator = 0

        async def run(self):
            msg = RequestPathChangeMessage(to='driver@localhost')
            msg.body = json.dumps({'iterator': self.iterator, 'path': 'new_path'})
            try:
                await self.send(msg)
                print(f'Message PathChange send! Iteration {self.iterator}')
            except Exception:
                return
            if self.iterator > 1 and self.iterator % 5 == 0:
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(1)
            self.iterator += 1

        async def on_end(self) -> None:
            await self.agent.stop()
            print(f'Behaviour finished with exit code {self.exit_code}.')

    class DriverData(CyclicBehaviour):
        iterator = 0

        async def run(self):
            msg = RequestDriverDataMessage(to='driver@localhost')
            msg.body = json.dumps({
                'iterator': self.iterator,
            })
            try:
                await self.send(msg)
                print(f'Message DriverData send! Iteration {self.iterator}')
            except Exception:
                return
            if self.iterator > 1 and self.iterator % 5 == 0:
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(2)
            self.iterator += 1

        async def on_end(self) -> None:
            await self.agent.stop()
            print(f'Behaviour finished with exit code {self.exit_code}.')

    def on_available(self, jid, stanza):
        print("[{}] Agent {} is available.".format(self.name, jid.split("@")[0]))

    def on_subscribed(self, jid):
        print("[{}] Agent {} has accepted the subscription.".format(self.name, jid.split("@")[0]))
        print("[{}] Contacts List: {}".format(self.name, self.presence.get_contacts()))

    def on_subscribe(self, jid):
        print("[{}] Agent {} asked for subscription. Let's approve it.".format(self.name, jid.split("@")[0]))
        self.presence.approve(jid)
        self.presence.subscribe(jid)

    async def setup(self):
        print('Agent starting...')
        self.presence.on_subscribe = self.on_subscribe
        self.presence.on_subscribed = self.on_subscribed
        self.presence.on_available = self.on_available
        print(self.presence.get_contacts())


if __name__ == '__main__':
    dummy = DummyAgent("manager@localhost", "manager_password")
    future = dummy.start()
    dummy.path_change = dummy.PathChange()
    dummy.driver_data = dummy.DriverData()
    dummy.add_behaviour(dummy.path_change)
    dummy.add_behaviour(dummy.driver_data)
    future.result()

    print('Wait until user interrupts with ctrl+c')
    while dummy.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    dummy.stop()
    quit_spade()
