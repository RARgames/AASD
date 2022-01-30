#
# do_celu
#
# Copyright 2022 Agenty 007
#
import pytest

from do_celu.agents.manager import ManagerAgent
from do_celu.config import get_config
from do_celu.messages.client import ReservationAvailabilityMessage
from do_celu.messages.manager import ReceiveDriverDataMessage, ReceiveDriverDataTemplate


@pytest.fixture
def manager_agent() -> ManagerAgent:
    config = get_config()
    manager = ManagerAgent(
        config.MANAGER_JID,
        config.MANAGER_PASSWORD,
    )

    future = manager.start()
    future.result()

    return manager


def test_driver_data_template_match():
    assert ReceiveDriverDataTemplate().match(ReceiveDriverDataMessage(to='test'))


def test_driver_data_template_not_match():
    assert not ReceiveDriverDataTemplate().match(ReservationAvailabilityMessage(to='test'))
