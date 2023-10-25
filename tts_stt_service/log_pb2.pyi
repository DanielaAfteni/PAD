from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LogRequest(_message.Message):
    __slots__ = ["serviceName", "serviceMessage", "time"]
    SERVICENAME_FIELD_NUMBER: _ClassVar[int]
    SERVICEMESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    serviceName: str
    serviceMessage: str
    time: _timestamp_pb2.Timestamp
    def __init__(self, serviceName: _Optional[str] = ..., serviceMessage: _Optional[str] = ..., time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class LogReply(_message.Message):
    __slots__ = ["isSuccess"]
    ISSUCCESS_FIELD_NUMBER: _ClassVar[int]
    isSuccess: bool
    def __init__(self, isSuccess: bool = ...) -> None: ...
