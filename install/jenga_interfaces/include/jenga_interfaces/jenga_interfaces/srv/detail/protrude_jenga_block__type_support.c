// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from jenga_interfaces:srv/ProtrudeJengaBlock.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "jenga_interfaces/srv/detail/protrude_jenga_block__rosidl_typesupport_introspection_c.h"
#include "jenga_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "jenga_interfaces/srv/detail/protrude_jenga_block__functions.h"
#include "jenga_interfaces/srv/detail/protrude_jenga_block__struct.h"


// Include directives for member types
// Member `axis`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  jenga_interfaces__srv__ProtrudeJengaBlock_Request__init(message_memory);
}

void jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_fini_function(void * message_memory)
{
  jenga_interfaces__srv__ProtrudeJengaBlock_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_member_array[3] = {
  {
    "block_index",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__ProtrudeJengaBlock_Request, block_index),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "distance_m",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__ProtrudeJengaBlock_Request, distance_m),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "axis",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__ProtrudeJengaBlock_Request, axis),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_members = {
  "jenga_interfaces__srv",  // message namespace
  "ProtrudeJengaBlock_Request",  // message name
  3,  // number of fields
  sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Request),
  jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_member_array,  // message members
  jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_type_support_handle = {
  0,
  &jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_jenga_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, ProtrudeJengaBlock_Request)() {
  if (!jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_type_support_handle.typesupport_identifier) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &jenga_interfaces__srv__ProtrudeJengaBlock_Request__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "jenga_interfaces/srv/detail/protrude_jenga_block__rosidl_typesupport_introspection_c.h"
// already included above
// #include "jenga_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "jenga_interfaces/srv/detail/protrude_jenga_block__functions.h"
// already included above
// #include "jenga_interfaces/srv/detail/protrude_jenga_block__struct.h"


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  jenga_interfaces__srv__ProtrudeJengaBlock_Response__init(message_memory);
}

void jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_fini_function(void * message_memory)
{
  jenga_interfaces__srv__ProtrudeJengaBlock_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_member_array[2] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces__srv__ProtrudeJengaBlock_Response, success),  // bytes offset in struct
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
    offsetof(jenga_interfaces__srv__ProtrudeJengaBlock_Response, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_members = {
  "jenga_interfaces__srv",  // message namespace
  "ProtrudeJengaBlock_Response",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Response),
  jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_member_array,  // message members
  jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_type_support_handle = {
  0,
  &jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_jenga_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, ProtrudeJengaBlock_Response)() {
  if (!jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_type_support_handle.typesupport_identifier) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &jenga_interfaces__srv__ProtrudeJengaBlock_Response__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "jenga_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "jenga_interfaces/srv/detail/protrude_jenga_block__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_service_members = {
  "jenga_interfaces__srv",  // service namespace
  "ProtrudeJengaBlock",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Request_message_type_support_handle,
  NULL  // response message
  // jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_Response_message_type_support_handle
};

static rosidl_service_type_support_t jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_service_type_support_handle = {
  0,
  &jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, ProtrudeJengaBlock_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, ProtrudeJengaBlock_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_jenga_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, ProtrudeJengaBlock)() {
  if (!jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_service_type_support_handle.typesupport_identifier) {
    jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, ProtrudeJengaBlock_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, jenga_interfaces, srv, ProtrudeJengaBlock_Response)()->data;
  }

  return &jenga_interfaces__srv__detail__protrude_jenga_block__rosidl_typesupport_introspection_c__ProtrudeJengaBlock_service_type_support_handle;
}
