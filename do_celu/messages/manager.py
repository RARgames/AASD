#
# do_celu
#
# Copyright 2022 Agenty 007
#
from dataclasses import dataclass
from typing import Any, Dict, Optional
from spade.message import Message
from spade.template import Template

from do_celu.utils.performatives import Performatives
from do_celu.messages.base_message import BaseMessage


class _ReceiveDriverDataMessageBase(BaseMessage):

    def _set_custom_properties(self) -> None:
        self.set_metadata("performative", Performatives.REQUEST.value)
        self.set_metadata("ontology", self._config.ONTOLOGY)
        self.set_metadata("language", "JSON")
        self.set_metadata('behaviour', 'receive_driver_data')


class ReceiveDriverDataTemplate(_ReceiveDriverDataMessageBase, Template):
    pass


class ReceiveDriverDataMessage(_ReceiveDriverDataMessageBase, Message):
    pass


@dataclass(frozen=True)
class ReceiveDriverDataBody():
    capacity: int
    current_path: Optional[Any]
    geolocation: Dict[str, Any]
