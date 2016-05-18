class RPCError(Exception):
    pass


class ConnectionError(RPCError):
    pass


class BadStatusCode(RPCError):
    pass


class BadJson(RPCError):
    pass


class BadResponse(RPCError):
    pass


class BadRequest(RPCError):
    pass
