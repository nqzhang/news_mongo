from aiocache.serializers import BaseSerializer
import msgpack

class MsgPackSerializer(BaseSerializer):
    """
    Transform data to bytes using msgpack.dumps and msgpack.loads to retrieve it back. You need
    to have ``msgpack`` installed in order to be able to use this serializer.

    :param encoding: str. Can be used to change encoding param for ``msg.loads`` method.
        Default is utf-8.
    :param use_list: bool. Can be used to change use_list param for ``msgpack.loads`` method.
        Default is True.
    """
    DEFAULT_ENCODING = None
    def __init__(self, *args, use_list=True, **kwargs):
        self.use_list = use_list
        super().__init__(*args, **kwargs)

    def dumps(self, value):
        """
        Serialize the received value using ``msgpack.dumps``.

        :param value: obj
        :returns: bytes
        """
        return msgpack.packb(value,use_bin_type=True)

    def loads(self, value):
        """
        Deserialize value using ``msgpack.loads``.

        :param value: bytes
        :returns: obj
        """
        if value is None:
            return None
        return msgpack.unpackb(value,use_list=self.use_list,raw=False)
