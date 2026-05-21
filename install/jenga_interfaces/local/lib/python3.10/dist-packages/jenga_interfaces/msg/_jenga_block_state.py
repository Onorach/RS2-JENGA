# generated from rosidl_generator_py/resource/_idl.py.em
# with input from jenga_interfaces:msg/JengaBlockState.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_JengaBlockState(type):
    """Metaclass of message 'JengaBlockState'."""

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
                'jenga_interfaces.msg.JengaBlockState')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__jenga_block_state
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__jenga_block_state
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__jenga_block_state
            cls._TYPE_SUPPORT = module.type_support_msg__msg__jenga_block_state
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__jenga_block_state

            from geometry_msgs.msg import Pose
            if Pose.__class__._TYPE_SUPPORT is None:
                Pose.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class JengaBlockState(metaclass=Metaclass_JengaBlockState):
    """Message class 'JengaBlockState'."""

    __slots__ = [
        '_block_id',
        '_colour',
        '_layer',
        '_layer_position',
        '_pose',
    ]

    _fields_and_field_types = {
        'block_id': 'uint32',
        'colour': 'string',
        'layer': 'uint32',
        'layer_position': 'uint8',
        'pose': 'geometry_msgs/Pose',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Pose'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.block_id = kwargs.get('block_id', int())
        self.colour = kwargs.get('colour', str())
        self.layer = kwargs.get('layer', int())
        self.layer_position = kwargs.get('layer_position', int())
        from geometry_msgs.msg import Pose
        self.pose = kwargs.get('pose', Pose())

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
        if self.block_id != other.block_id:
            return False
        if self.colour != other.colour:
            return False
        if self.layer != other.layer:
            return False
        if self.layer_position != other.layer_position:
            return False
        if self.pose != other.pose:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def block_id(self):
        """Message field 'block_id'."""
        return self._block_id

    @block_id.setter
    def block_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'block_id' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'block_id' field must be an unsigned integer in [0, 4294967295]"
        self._block_id = value

    @builtins.property
    def colour(self):
        """Message field 'colour'."""
        return self._colour

    @colour.setter
    def colour(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'colour' field must be of type 'str'"
        self._colour = value

    @builtins.property
    def layer(self):
        """Message field 'layer'."""
        return self._layer

    @layer.setter
    def layer(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'layer' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'layer' field must be an unsigned integer in [0, 4294967295]"
        self._layer = value

    @builtins.property
    def layer_position(self):
        """Message field 'layer_position'."""
        return self._layer_position

    @layer_position.setter
    def layer_position(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'layer_position' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'layer_position' field must be an unsigned integer in [0, 255]"
        self._layer_position = value

    @builtins.property
    def pose(self):
        """Message field 'pose'."""
        return self._pose

    @pose.setter
    def pose(self, value):
        if __debug__:
            from geometry_msgs.msg import Pose
            assert \
                isinstance(value, Pose), \
                "The 'pose' field must be a sub message of type 'Pose'"
        self._pose = value
