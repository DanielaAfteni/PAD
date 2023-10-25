# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import log_pb2 as log__pb2


class NotificationStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SaveLogToRabbit = channel.unary_unary(
                '/log.Notification/SaveLogToRabbit',
                request_serializer=log__pb2.LogRequest.SerializeToString,
                response_deserializer=log__pb2.LogReply.FromString,
                )


class NotificationServicer(object):
    """The greeting service definition.
    """

    def SaveLogToRabbit(self, request, context):
        """Sends a greeting
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NotificationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SaveLogToRabbit': grpc.unary_unary_rpc_method_handler(
                    servicer.SaveLogToRabbit,
                    request_deserializer=log__pb2.LogRequest.FromString,
                    response_serializer=log__pb2.LogReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'log.Notification', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Notification(object):
    """The greeting service definition.
    """

    @staticmethod
    def SaveLogToRabbit(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/log.Notification/SaveLogToRabbit',
            log__pb2.LogRequest.SerializeToString,
            log__pb2.LogReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
