# generated from rosidl_generator_py/resource/_idl.py.em
# with input from jenga_interfaces:srv/ProtrudeJengaBlock.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ProtrudeJengaBlock_Request(type):
    """Metaclass of message 'ProtrudeJengaBlock_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('jenga_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'jenga_interfaces.srv.ProtrudeJengaBlock_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__protrude_jenga_block__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__protrude_jenga_block__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__protrude_jenga_block__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__protrude_jenga_block__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__protrude_jenga_block__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ProtrudeJengaBlock_Request(metaclass=Metaclass_ProtrudeJengaBlock_Request):
    """Message class 'ProtrudeJengaBlock_Request'."""

    __slots__ = [
        '_block_index',
        '_distance_m',
        '_axis',
    ]

    _fields_and_field_types = {
        'block_index': 'uint32',
        'distance_m': 'double',
        'axis': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.block_index = kwargs.get('block_index', int())
        self.distance_m = kwargs.get('distance_m', float())
        self.axis = kwargs.get('axis', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.block_index != other.block_index:
            return False
        if self.distance_m != other.distance_m:
            return False
        if self.axis != other.axis:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def block_index(self):
        """Message field 'block_index'."""
        return self._block_index

    @block_index.setter
    def block_index(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'block_index' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'block_index' field must be an unsigned integer in [0, 4294967295]"
        self._block_index = value

    @builtins.property
    def distance_m(self):
        """Message field 'distance_m'."""
        return self._distance_m

    @distance_m.setter
    def distance_m(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'distance_m' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'distance_m' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._distance_m = value

    @builtins.property
    def axis(self):
        """Message field 'axis'."""
        return self._axis

    @axis.setter
    def axis(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'axis' field must be of type 'str'"
        self._axis = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ProtrudeJengaBlock_Response(type):
    """Metaclass of message 'ProtrudeJengaBlock_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('jenga_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'jenga_interfaces.srv.ProtrudeJengaBlock_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__protrude_jenga_block__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__protrude_jenga_block__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__protrude_jenga_block__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__protrude_jenga_block__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__protrude_jenga_block__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ProtrudeJengaBlock_Response(metaclass=Metaclass_ProtrudeJengaBlock_Response):
    """Message class 'ProtrudeJengaBlock_Response'."""

    __slots__ = [
        '_success',
        '_message',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())
        self.message = kwargs.get('message', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.success != other.success:
            return False
        if self.message != other.message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value

    @builtins.property
    def message(self):
        """Message field 'message'."""
        return self._message

    @message.setter
    def message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'message' field must be of type 'str'"
        self._message = value


class Metaclass_ProtrudeJengaBlock(type):
    """Metaclass of service 'ProtrudeJengaBlock'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('jenga_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'jenga_interfaces.srv.ProtrudeJengaBlock')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__protrude_jenga_block

            from jenga_interfaces.srv import _protrude_jenga_block
            if _protrude_jenga_block.Metaclass_ProtrudeJengaBlock_Request._TYPE_SUPPORT is None:
                _protrude_jenga_block.Metaclass_ProtrudeJengaBlock_Request.__import_type_support__()
            if _protrude_jenga_block.Metaclass_ProtrudeJengaBlock_Response._TYPE_SUPPORT is None:
                _protrude_jenga_block.Metaclass_ProtrudeJengaBlock_Response.__import_type_support__()


class ProtrudeJengaBlock(metaclass=Metaclass_ProtrudeJengaBlock):
    from jenga_interfaces.srv._protrude_jenga_block import ProtrudeJengaBlock_Request as Request
    from jenga_interfaces.srv._protrude_jenga_block import ProtrudeJengaBlock_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
