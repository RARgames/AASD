#
# do_celu
#
# Copyright 2022 Agenty 007
#
from spade.message import Message
from spade.template import Template

from do_celu.messages.base_message import BaseMessage
from do_celu.utils.performatives import Performatives


class _BestConnectionsMessageBase(BaseMessage):

    def _set_custom_properties(self) -> None:
        self.set_metadata("performative", Performatives.REQUEST.value)
        self.set_metadata("ontology", self._config.ONTOLOGY)
        self.set_metadata("language", "JSON")
        self.set_metadata('behaviour', 'best_connections')


class BestConnectionsTemplate(_BestConnectionsMessageBase, Template):
    pass


class BestConnectionsMessage(_BestConnectionsMessageBase, Message):
    pass


class _ReservationAvailabilityMessageBase(BaseMessage):

    def _set_custom_properties(self) -> None:
        self.set_metadata("performative", Performatives.INFORM.value)
        self.set_metadata("ontology", self._config.ONTOLOGY)
        self.set_metadata("language", "JSON")
        self.set_metadata('behaviour', 'reservation_availability')


class ReservationAvailabilityTemplate(_ReservationAvailabilityMessageBase, Template):
    pass


class ReservationAvailabilityMessage(_ReservationAvailabilityMessageBase, Message):
    pass


class _AcceptProposalMessageBase(BaseMessage):

    def _set_custom_properties(self) -> None:
        self.set_metadata("performative", Performatives.INFORM.value)
        self.set_metadata("ontology", self._config.ONTOLOGY)
        self.set_metadata("language", "JSON")
        self.set_metadata('behaviour', 'accept_proposal')


class AcceptProposalTemplate(_AcceptProposalMessageBase, Template):
    pass


class AcceptProposalMessage(_AcceptProposalMessageBase, Message):
    pass
