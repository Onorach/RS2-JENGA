# generated from rosidl_generator_py/resource/_idl.py.em
# with input from jenga_interfaces:srv/SetJengaBlocksLayout.idl
# generated code does not contain a copyright notice


# Import statements for member types

# Member 'block_indices'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SetJengaBlocksLayout_Request(type):
    """Metaclass of message 'SetJengaBlocksLayout_Request'."""

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
                'jenga_interfaces.srv.SetJengaBlocksLayout_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_jenga_blocks_layout__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_jenga_blocks_layout__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_jenga_blocks_layout__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_jenga_blocks_layout__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_jenga_blocks_layout__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SetJengaBlocksLayout_Request(metaclass=Metaclass_SetJengaBlocksLayout_Request):
    """Message class 'SetJengaBlocksLayout_Request'."""

    __slots__ = [
        '_block_indices',
        '_target_layout',
    ]

    _fields_and_field_types = {
        'block_indices': 'sequence<uint32>',
        'target_layout': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint32')),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.block_indices = array.array('I', kwargs.get('block_indices', []))
        self.target_layout = kwargs.get('target_layout', str())

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
        if self.block_indices != other.block_indices:
            return False
        if self.target_layout != other.target_layout:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def block_indices(self):
        """Message field 'block_indices'."""
        return self._block_indices

    @block_indices.setter
    def block_indices(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'I', \
                "The 'block_indices' array.array() must have the type code of 'I'"
            self._block_indices = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= 0 and val < 4294967296 for val in value)), \
                "The 'block_indices' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 4294967295]"
        self._block_indices = array.array('I', value)

    @builtins.property
    def target_layout(self):
        """Message field 'target_layout'."""
        return self._target_layout

    @target_layout.setter
    def target_layout(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'target_layout' field must be of type 'str'"
        self._target_layout = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_SetJengaBlocksLayout_Response(type):
    """Metaclass of message 'SetJengaBlocksLayout_Response'."""

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
                'jenga_interfaces.srv.SetJengaBlocksLayout_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__set_jenga_blocks_layout__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__set_jenga_blocks_layout__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__set_jenga_blocks_layout__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__set_jenga_blocks_layout__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__set_jenga_blocks_layout__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SetJengaBlocksLayout_Response(metaclass=Metaclass_SetJengaBlocksLayout_Response):
    """Message class 'SetJengaBlocksLayout_Response'."""

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


class Metaclass_SetJengaBlocksLayout(type):
    """Metaclass of service 'SetJengaBlocksLayout'."""

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
                'jenga_interfaces.srv.SetJengaBlocksLayout')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__set_jenga_blocks_layout

            from jenga_interfaces.srv import _set_jenga_blocks_layout
            if _set_jenga_blocks_layout.Metaclass_SetJengaBlocksLayout_Request._TYPE_SUPPORT is None:
                _set_jenga_blocks_layout.Metaclass_SetJengaBlocksLayout_Request.__import_type_support__()
            if _set_jenga_blocks_layout.Metaclass_SetJengaBlocksLayout_Response._TYPE_SUPPORT is None:
                _set_jenga_blocks_layout.Metaclass_SetJengaBlocksLayout_Response.__import_type_support__()


class SetJengaBlocksLayout(metaclass=Metaclass_SetJengaBlocksLayout):
    from jenga_interfaces.srv._set_jenga_blocks_layout import SetJengaBlocksLayout_Request as Request
    from jenga_interfaces.srv._set_jenga_blocks_layout import SetJengaBlocksLayout_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
