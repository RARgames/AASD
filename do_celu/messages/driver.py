#
# do_celu
#
# Copyright 2022 Agenty 007
#
from dataclasses import dataclass
from spade.message import Message
from spade.template import Template

from do_celu.utils.performatives import Performatives
from do_celu.messages.base_message import BaseMessage


class _RequestDriverDataMessageBase(BaseMessage):

    def _set_custom_properties(self) -> None:
        self.set_metadata("performative", Performatives.REQUEST.value)
        self.set_metadata("ontology", self._config.ONTOLOGY)
        self.set_metadata("language", "JSON")
        self.set_metadata('behaviour', 'request_driver_data')


class RequestDriverDataTemplate(_RequestDriverDataMessageBase, Template):
    pass


class RequestDriverDataMessage(_RequestDriverDataMessageBase, Message):
    pass


class _RequestPathChangeMessageBase(BaseMessage):

    def _set_custom_properties(self) -> None:
        self.set_metadata("performative", Performatives.INFORM.value)
        self.set_metadata("ontology", self._config.ONTOLOGY)
        self.set_metadata("language", "JSON")
        self.set_metadata('behaviour', 'request_path_change')


class RequestPathChangeTemplate(_RequestPathChangeMessageBase, Template):
    pass


class RequestPathChangeMessage(_RequestPathChangeMessageBase, Message):
    pass


@dataclass(frozen=True)
class PathChangeBody():
    path: object
