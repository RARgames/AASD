#
# do_celu
#
# Copyright 2022 Agenty 007
#

from time import sleep
from typing import List

from spade import quit_spade

from do_celu.config import get_config
from do_celu.context import get_logger
from do_celu.agents.driver import DriverAgent
from do_celu.agents.manager import ManagerAgent
from do_celu.messages.driver import PathChangeBody


def setup_manager() -> ManagerAgent:
    manager = ManagerAgent(
        config.MANAGER_JID,
        config.MANAGER_PASSWORD,
    )

    future = manager.start()
    future.result()

    return manager


def setup_drivers() -> List[DriverAgent]:
    driver_1 = (DriverAgent(
        '1_driver@localhost',
        config.DRIVER_PASSWORD,
        capacity=50,
        geolocation={
            'x': 52.21905021340178,
            'y': 21.011905061692943,
        },
    ))

    driver_2 = DriverAgent(
        '2_driver@localhost',
        config.DRIVER_PASSWORD,
        capacity=50,
        geolocation={
            'x': 52.21905021340178,
            'y': 21.011905061692943,
        },
    )

    driver_3 = DriverAgent(
        '3_driver@localhost',
        config.DRIVER_PASSWORD,
        capacity=50,
        geolocation={
            'x': 52.21905021340178,
            'y': 21.011905061692943,
        },
    )

    future = driver_1.start()
    future.result()

    future = driver_2.start()
    future.result()

    future = driver_3.start()
    future.result()

    return [driver_1, driver_2, driver_3]


if __name__ == '__main__':
    config = get_config()
    logger = get_logger('manager_driver_communication')

    logger.info('Start agetns')
    manager = setup_manager()
    driver_1, driver_2, driver_3 = setup_drivers()

    sleep(10)
    logger.info('Informs agents about new paths')
    manager._add_inform_driver_path_change(jid=str(driver_1.jid), data=PathChangeBody(path=[1, 4, 10]))
    manager._add_inform_driver_path_change(jid=str(driver_2.jid), data=PathChangeBody(path=[2, 6, 7]))
    manager._add_inform_driver_path_change(jid=str(driver_3.jid), data=PathChangeBody(path=[3, 1, 12]))
    sleep(10)
    logger.info('Request all drivers data')
    manager._add_request_all_drivers_data()
    sleep(5)
    logger.info('Stop driver 1')
    driver_1.stop()
    logger.info('Infrom driver 3 about path change')
    manager._add_inform_driver_path_change(jid=str(driver_3.jid), data=PathChangeBody(path=[13, 5, 3]))
    sleep(5)
    logger.info('Request all drivers data')
    manager._add_request_all_drivers_data()
    sleep(5)
    logger.info('Stop driver 2 and 3')
    driver_2.stop()
    driver_3.stop()
    sleep(5)
    logger.info('Request all drivers data')
    manager._add_request_all_drivers_data()

    while manager.is_alive() or driver_1.is_alive() or driver_2.is_alive() or driver_3.is_alive():
        try:
            sleep(1)
        except KeyboardInterrupt:
            break

    manager.stop()
    logger.debug('Example finished')
    quit_spade()
