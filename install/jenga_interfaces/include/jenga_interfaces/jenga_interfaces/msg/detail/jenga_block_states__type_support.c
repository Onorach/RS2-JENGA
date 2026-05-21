// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from jenga_interfaces:msg/JengaBlockStates.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "jenga_interfaces/msg/detail/jenga_block_states__rosidl_typesupport_introspection_c.h"
#include "jenga_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "jenga_interfaces/msg/detail/jenga_block_states__functions.h"
#include "jenga_interfaces/msg/detail/jenga_block_states__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `blocks`
#include "jenga_interfaces/msg/jenga_block_state.h"
// Member `blocks`
#include "jenga_interfaces/msg/detail/jenga_block_state__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  jenga_interfaces__msg__JengaBlockStates__init(message_memory);
}

void jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_fini_function(void * message_memory)
{
  jenga_interfaces__msg__JengaBlockStates__fini(message_memory);
}

size_t jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__size_function__JengaBlockStates__blocks(
  const void * untyped_member)
{
  const jenga_interfaces__msg__JengaBlockState__Sequence * member =
    (const jenga_interfaces__msg__JengaBlockState__Sequence *)(untyped_member);
  return member->size;
}

const void * jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__get_const_function__JengaBlockStates__blocks(
  const void * untyped_member, size_t index)
{
  const jenga_interfaces__msg__JengaBlockState__Sequence * member =
    (const jenga_interfaces__msg__JengaBlockState__Sequence *)(untyped_member);
  return &member->data[index];
}

void * jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__get_function__JengaBlockStates__blocks(
  void * untyped_member, size_t index)
{
  jenga_interfaces__msg__JengaBlockState__Sequence * member =
    (jenga_interfaces__msg__JengaBlockState__Sequence *)(untyped_member);
  return &member->data[index];
}

void jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__fetch_function__JengaBlockStates__blocks(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const jenga_interfaces__msg__JengaBlockState * item =
    ((const jenga_interfaces__msg__JengaBlockState *)
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__get_const_function__JengaBlockStates__blocks(untyped_member, index));
  jenga_interfaces__msg__JengaBlockState * value =
    (jenga_interfaces__msg__JengaBlockState *)(untyped_value);
  *value = *item;
}

void jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__assign_function__JengaBlockStates__blocks(
  void * untyped_member, size_t index, const void * untyped_value)
{
  jenga_interfaces__msg__JengaBlockState * item =
    ((jenga_interfaces__msg__JengaBlockState *)
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__get_function__JengaBlockStates__blocks(untyped_member, index));
  const jenga_interfaces__msg__JengaBlockState * value =
    (const jenga_interfaces__msg__JengaBlockState *)(untyped_value);
  *item = *value;
}

bool jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__resize_function__JengaBlockStates__blocks(
  void * untyped_member, size_t size)
{
  jenga_interfaces__msg__JengaBlockState__Sequence * member =
    (jenga_interfaces__msg__JengaBlockState__Sequence *)(untyped_member);
  jenga_interfaces__msg__JengaBlockState__Sequence__fini(member);
  return jenga_interfaces__msg__JengaBlockState__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__msg__JengaBlockStates, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "blocks",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__msg__JengaBlockStates, blocks),  // bytes offset in struct
    NULL,  // default value
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__size_function__JengaBlockStates__blocks,  // size() function pointer
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__get_const_function__JengaBlockStates__blocks,  // get_const(index) function pointer
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__get_function__JengaBlockStates__blocks,  // get(index) function pointer
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__fetch_function__JengaBlockStates__blocks,  // fetch(index, &value) function pointer
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__assign_function__JengaBlockStates__blocks,  // assign(index, value) function pointer
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__resize_function__JengaBlockStates__blocks  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_members = {
  "jenga_interfaces__msg",  // message namespace
  "JengaBlockStates",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces__msg__JengaBlockStates),
  jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_member_array,  // message members
  jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_init_function,  // function to initialize message memory (memory has to be allocated)
  jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_type_support_handle = {
  0,
  &jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_jenga_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, msg, JengaBlockStates)() {
  jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, msg, JengaBlockState)();
  if (!jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_type_support_handle.typesupport_identifier) {
    jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &jenga_interfaces__msg__JengaBlockStates__rosidl_typesupport_introspection_c__JengaBlockStates_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
