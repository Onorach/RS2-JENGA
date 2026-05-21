// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from jenga_interfaces:action/JengaExtractMiddleBlock.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_Goal_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_Goal(_init);
}

void JengaExtractMiddleBlock_Goal_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_Goal *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_Goal();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_Goal_message_member_array[4] = {
  {
    "block_index",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Goal, block_index),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "block_pose",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::PoseStamped>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Goal, block_pose),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "place_pose",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::PoseStamped>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Goal, place_pose),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "extract_axis",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Goal, extract_axis),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_Goal_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_Goal",  // message name
  4,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_Goal),
  JengaExtractMiddleBlock_Goal_message_member_array,  // message members
  JengaExtractMiddleBlock_Goal_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_Goal_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_Goal_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_Goal_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_Goal>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_Goal_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_Goal)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_Goal_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_Result_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_Result(_init);
}

void JengaExtractMiddleBlock_Result_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_Result *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_Result();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_Result_message_member_array[3] = {
  {
    "success",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Result, success),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "message",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Result, message),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "error_code",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Result, error_code),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_Result_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_Result",  // message name
  3,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_Result),
  JengaExtractMiddleBlock_Result_message_member_array,  // message members
  JengaExtractMiddleBlock_Result_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_Result_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_Result_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_Result_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_Result>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_Result_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_Result)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_Result_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_Feedback_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_Feedback(_init);
}

void JengaExtractMiddleBlock_Feedback_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_Feedback *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_Feedback();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_Feedback_message_member_array[2] = {
  {
    "current_stage",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Feedback, current_stage),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "progress_pct",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_Feedback, progress_pct),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_Feedback_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_Feedback",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_Feedback),
  JengaExtractMiddleBlock_Feedback_message_member_array,  // message members
  JengaExtractMiddleBlock_Feedback_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_Feedback_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_Feedback_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_Feedback_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_Feedback>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_Feedback_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_Feedback)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_Feedback_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_SendGoal_Request_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request(_init);
}

void JengaExtractMiddleBlock_SendGoal_Request_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_SendGoal_Request();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_SendGoal_Request_message_member_array[2] = {
  {
    "goal_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request, goal_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "goal",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_Goal>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request, goal),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_SendGoal_Request_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_SendGoal_Request",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request),
  JengaExtractMiddleBlock_SendGoal_Request_message_member_array,  // message members
  JengaExtractMiddleBlock_SendGoal_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_SendGoal_Request_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_SendGoal_Request_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_SendGoal_Request_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_SendGoal_Request_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_SendGoal_Request)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_SendGoal_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_SendGoal_Response_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response(_init);
}

void JengaExtractMiddleBlock_SendGoal_Response_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_SendGoal_Response();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_SendGoal_Response_message_member_array[2] = {
  {
    "accepted",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response, accepted),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "stamp",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<builtin_interfaces::msg::Time>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response, stamp),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_SendGoal_Response_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_SendGoal_Response",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response),
  JengaExtractMiddleBlock_SendGoal_Response_message_member_array,  // message members
  JengaExtractMiddleBlock_SendGoal_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_SendGoal_Response_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_SendGoal_Response_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_SendGoal_Response_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_SendGoal_Response_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_SendGoal_Response)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_SendGoal_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/service_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/service_type_support_decl.hpp"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

// this is intentionally not const to allow initialization later to prevent an initialization race
static ::rosidl_typesupport_introspection_cpp::ServiceMembers JengaExtractMiddleBlock_SendGoal_service_members = {
  "jenga_interfaces::action",  // service namespace
  "JengaExtractMiddleBlock_SendGoal",  // service name
  // these two fields are initialized below on the first access
  // see get_service_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal>()
  nullptr,  // request message
  nullptr  // response message
};

static const rosidl_service_type_support_t JengaExtractMiddleBlock_SendGoal_service_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_SendGoal_service_members,
  get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal>()
{
  // get a handle to the value to be returned
  auto service_type_support =
    &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_SendGoal_service_type_support_handle;
  // get a non-const and properly typed version of the data void *
  auto service_members = const_cast<::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
    static_cast<const ::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
      service_type_support->data));
  // make sure that both the request_members_ and the response_members_ are initialized
  // if they are not, initialize them
  if (
    service_members->request_members_ == nullptr ||
    service_members->response_members_ == nullptr)
  {
    // initialize the request_members_ with the static function from the external library
    service_members->request_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request
      >()->data
      );
    // initialize the response_members_ with the static function from the external library
    service_members->response_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response
      >()->data
      );
  }
  // finally return the properly initialized service_type_support handle
  return service_type_support;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_SendGoal)() {
  return ::rosidl_typesupport_introspection_cpp::get_service_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal>();
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_GetResult_Request_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request(_init);
}

void JengaExtractMiddleBlock_GetResult_Request_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_GetResult_Request();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_GetResult_Request_message_member_array[1] = {
  {
    "goal_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request, goal_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_GetResult_Request_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_GetResult_Request",  // message name
  1,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request),
  JengaExtractMiddleBlock_GetResult_Request_message_member_array,  // message members
  JengaExtractMiddleBlock_GetResult_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_GetResult_Request_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_GetResult_Request_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_GetResult_Request_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_GetResult_Request_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_GetResult_Request)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_GetResult_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_GetResult_Response_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response(_init);
}

void JengaExtractMiddleBlock_GetResult_Response_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_GetResult_Response();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_GetResult_Response_message_member_array[2] = {
  {
    "status",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response, status),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "result",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_Result>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response, result),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_GetResult_Response_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_GetResult_Response",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response),
  JengaExtractMiddleBlock_GetResult_Response_message_member_array,  // message members
  JengaExtractMiddleBlock_GetResult_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_GetResult_Response_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_GetResult_Response_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_GetResult_Response_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_GetResult_Response_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_GetResult_Response)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_GetResult_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/service_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/service_type_support_decl.hpp"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

// this is intentionally not const to allow initialization later to prevent an initialization race
static ::rosidl_typesupport_introspection_cpp::ServiceMembers JengaExtractMiddleBlock_GetResult_service_members = {
  "jenga_interfaces::action",  // service namespace
  "JengaExtractMiddleBlock_GetResult",  // service name
  // these two fields are initialized below on the first access
  // see get_service_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_GetResult>()
  nullptr,  // request message
  nullptr  // response message
};

static const rosidl_service_type_support_t JengaExtractMiddleBlock_GetResult_service_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_GetResult_service_members,
  get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_GetResult>()
{
  // get a handle to the value to be returned
  auto service_type_support =
    &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_GetResult_service_type_support_handle;
  // get a non-const and properly typed version of the data void *
  auto service_members = const_cast<::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
    static_cast<const ::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
      service_type_support->data));
  // make sure that both the request_members_ and the response_members_ are initialized
  // if they are not, initialize them
  if (
    service_members->request_members_ == nullptr ||
    service_members->response_members_ == nullptr)
  {
    // initialize the request_members_ with the static function from the external library
    service_members->request_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request
      >()->data
      );
    // initialize the response_members_ with the static function from the external library
    service_members->response_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response
      >()->data
      );
  }
  // finally return the properly initialized service_type_support handle
  return service_type_support;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_GetResult)() {
  return ::rosidl_typesupport_introspection_cpp::get_service_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_GetResult>();
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaExtractMiddleBlock_FeedbackMessage_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage(_init);
}

void JengaExtractMiddleBlock_FeedbackMessage_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage *>(message_memory);
  typed_message->~JengaExtractMiddleBlock_FeedbackMessage();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaExtractMiddleBlock_FeedbackMessage_message_member_array[2] = {
  {
    "goal_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage, goal_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "feedback",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_Feedback>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage, feedback),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaExtractMiddleBlock_FeedbackMessage_message_members = {
  "jenga_interfaces::action",  // message namespace
  "JengaExtractMiddleBlock_FeedbackMessage",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage),
  JengaExtractMiddleBlock_FeedbackMessage_message_member_array,  // message members
  JengaExtractMiddleBlock_FeedbackMessage_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaExtractMiddleBlock_FeedbackMessage_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaExtractMiddleBlock_FeedbackMessage_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaExtractMiddleBlock_FeedbackMessage_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage>()
{
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_FeedbackMessage_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, action, JengaExtractMiddleBlock_FeedbackMessage)() {
  return &::jenga_interfaces::action::rosidl_typesupport_introspection_cpp::JengaExtractMiddleBlock_FeedbackMessage_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
