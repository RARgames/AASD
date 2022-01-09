from typing import List


class Connection:
    def __init__(self, connection_id, sth):
        self.id = connection_id
        self.sth = sth


class ConnectionRequest:
    def __init__(self, start_date, origin, destination):
        self.start_date = start_date
        self.origin = origin
        self.destination = destination


class ConnectionResponse:
    def __init__(self, best_connections: List[Connection]):
        self.best_connections = best_connections
