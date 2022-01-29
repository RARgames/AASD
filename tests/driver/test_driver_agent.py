#
# do_celu
#
# Copyright 2022 Agenty 007
#
import asyncio
import json
from typing import Any

import pytest
from spade import agent, quit_spade
from spade.behaviour import OneShotBehaviour

from do_celu.agents.driver import DriverAgent
from do_celu.config import get_config
from do_celu.messages.driver import RequestDriverDataMessage, RequestDriverDataTemplate, RequestPathChangeMessage, RequestPathChangeTemplate


@pytest.fixture
def driver_agent() -> DriverAgent:
    config = get_config()
    driver = DriverAgent(
        config.DRIVER_JID,
        config.DRIVER_PASSWORD,
        capacity=50,
        geolocation={
            'x': 52.21905021340178,
            'y': 21.011905061692943,
        },
    )

    future = driver.start()
    future.result()

    return driver


def test_driver_data_template_match():
    assert RequestDriverDataTemplate().match(RequestDriverDataMessage(to='test'))


def test_driver_data_template_not_match():
    assert not RequestDriverDataTemplate().match(RequestPathChangeMessage(to='test'))


def test_path_change_template_match():
    assert RequestPathChangeTemplate().match(RequestPathChangeMessage(to='test'))


def test_path_change_template_not_match():
    assert not RequestPathChangeTemplate().match(RequestDriverDataMessage(to='test'))


@pytest.mark.asyncio
async def test_request_driver_data_one_shot_behaviour(driver_agent: DriverAgent):
    await driver_agent.receive_request_driver_data.enqueue(RequestDriverDataMessage(to='test'))
    await asyncio.sleep(0.1)

    assert driver_agent.inform_driver_data.is_done() is True
    assert driver_agent.inform_driver_data.is_killed() is True


@pytest.mark.asyncio
async def test_request_driver_data_(driver_agent: DriverAgent):
    config = get_config()

    class DummyAgent(agent.Agent):
        result: Any

        class TestBehaviour(OneShotBehaviour):
            agent: 'DummyAgent'

            async def run(self):
                msg = await self.receive(timeout=3)
                self.agent.result = msg

        async def setup(self):
            test_behaviour = self.TestBehaviour()
            self.add_behaviour(test_behaviour)

    dummy = DummyAgent(config.MANAGER_JID, config.MANAGER_PASSWORD)
    future = dummy.start()
    future.result()

    await driver_agent.receive_request_driver_data.enqueue(RequestDriverDataMessage(to=config.MANAGER_JID))
    await asyncio.sleep(0.1)

    dummy.stop()
    driver_agent.stop()
    quit_spade()

    assert dummy.result.body == json.dumps(driver_agent._get_state())


@pytest.mark.asyncio
async def test_path_change(driver_agent: DriverAgent):
    new_path = 'new_path'
    await driver_agent.receive_inform_path_change.enqueue(
        RequestPathChangeMessage(
            to='test',
            body=json.dumps({'path': new_path}),
        ))
    await asyncio.sleep(0.1)

    driver_agent.stop()
    quit_spade()

    state = driver_agent._get_state()
    assert state['current_path'] == new_path
