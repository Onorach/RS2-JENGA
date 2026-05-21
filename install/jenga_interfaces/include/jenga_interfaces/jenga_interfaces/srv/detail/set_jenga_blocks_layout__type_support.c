// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from jenga_interfaces:srv/SetJengaBlocksLayout.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__rosidl_typesupport_introspection_c.h"
#include "jenga_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__functions.h"
#include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__struct.h"


// Include directives for member types
// Member `block_indices`
#include "rosidl_runtime_c/primitives_sequence_functions.h"
// Member `target_layout`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  jenga_interfaces__srv__SetJengaBlocksLayout_Request__init(message_memory);
}

void jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_fini_function(void * message_memory)
{
  jenga_interfaces__srv__SetJengaBlocksLayout_Request__fini(message_memory);
}

size_t jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__size_function__SetJengaBlocksLayout_Request__block_indices(
  const void * untyped_member)
{
  const rosidl_runtime_c__uint32__Sequence * member =
    (const rosidl_runtime_c__uint32__Sequence *)(untyped_member);
  return member->size;
}

const void * jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__get_const_function__SetJengaBlocksLayout_Request__block_indices(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__uint32__Sequence * member =
    (const rosidl_runtime_c__uint32__Sequence *)(untyped_member);
  return &member->data[index];
}

void * jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__get_function__SetJengaBlocksLayout_Request__block_indices(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__uint32__Sequence * member =
    (rosidl_runtime_c__uint32__Sequence *)(untyped_member);
  return &member->data[index];
}

void jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__fetch_function__SetJengaBlocksLayout_Request__block_indices(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const uint32_t * item =
    ((const uint32_t *)
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__get_const_function__SetJengaBlocksLayout_Request__block_indices(untyped_member, index));
  uint32_t * value =
    (uint32_t *)(untyped_value);
  *value = *item;
}

void jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__assign_function__SetJengaBlocksLayout_Request__block_indices(
  void * untyped_member, size_t index, const void * untyped_value)
{
  uint32_t * item =
    ((uint32_t *)
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__get_function__SetJengaBlocksLayout_Request__block_indices(untyped_member, index));
  const uint32_t * value =
    (const uint32_t *)(untyped_value);
  *item = *value;
}

bool jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__resize_function__SetJengaBlocksLayout_Request__block_indices(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__uint32__Sequence * member =
    (rosidl_runtime_c__uint32__Sequence *)(untyped_member);
  rosidl_runtime_c__uint32__Sequence__fini(member);
  return rosidl_runtime_c__uint32__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_member_array[2] = {
  {
    "block_indices",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__SetJengaBlocksLayout_Request, block_indices),  // bytes offset in struct
    NULL,  // default value
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__size_function__SetJengaBlocksLayout_Request__block_indices,  // size() function pointer
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__get_const_function__SetJengaBlocksLayout_Request__block_indices,  // get_const(index) function pointer
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__get_function__SetJengaBlocksLayout_Request__block_indices,  // get(index) function pointer
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__fetch_function__SetJengaBlocksLayout_Request__block_indices,  // fetch(index, &value) function pointer
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__assign_function__SetJengaBlocksLayout_Request__block_indices,  // assign(index, value) function pointer
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__resize_function__SetJengaBlocksLayout_Request__block_indices  // resize(index) function pointer
  },
  {
    "target_layout",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__SetJengaBlocksLayout_Request, target_layout),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_members = {
  "jenga_interfaces__srv",  // message namespace
  "SetJengaBlocksLayout_Request",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces__srv__SetJengaBlocksLayout_Request),
  jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_member_array,  // message members
  jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_type_support_handle = {
  0,
  &jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_jenga_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, SetJengaBlocksLayout_Request)() {
  if (!jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_type_support_handle.typesupport_identifier) {
    jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &jenga_interfaces__srv__SetJengaBlocksLayout_Request__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__rosidl_typesupport_introspection_c.h"
// already included above
// #include "jenga_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__functions.h"
// already included above
// #include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__struct.h"


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  jenga_interfaces__srv__SetJengaBlocksLayout_Response__init(message_memory);
}

void jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_fini_function(void * message_memory)
{
  jenga_interfaces__srv__SetJengaBlocksLayout_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_member_array[2] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__SetJengaBlocksLayout_Response, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__SetJengaBlocksLayout_Response, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_members = {
  "jenga_interfaces__srv",  // message namespace
  "SetJengaBlocksLayout_Response",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces__srv__SetJengaBlocksLayout_Response),
  jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_member_array,  // message members
  jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_type_support_handle = {
  0,
  &jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_jenga_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, SetJengaBlocksLayout_Response)() {
  if (!jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_type_support_handle.typesupport_identifier) {
    jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &jenga_interfaces__srv__SetJengaBlocksLayout_Response__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "jenga_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_service_members = {
  "jenga_interfaces__srv",  // service namespace
  "SetJengaBlocksLayout",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Request_message_type_support_handle,
  NULL  // response message
  // jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_Response_message_type_support_handle
};

static rosidl_service_type_support_t jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_service_type_support_handle = {
  0,
  &jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, SetJengaBlocksLayout_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, SetJengaBlocksLayout_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_jenga_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, SetJengaBlocksLayout)() {
  if (!jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_service_type_support_handle.typesupport_identifier) {
    jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, SetJengaBlocksLayout_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, SetJengaBlocksLayout_Response)()->data;
  }

  return &jenga_interfaces__srv__detail__set_jenga_blocks_layout__rosidl_typesupport_introspection_c__SetJengaBlocksLayout_service_type_support_handle;
}
