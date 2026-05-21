// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from jenga_interfaces:msg/JengaBlockStates.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "jenga_interfaces/msg/detail/jenga_block_states__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace jenga_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void JengaBlockStates_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) jenga_interfaces::msg::JengaBlockStates(_init);
}

void JengaBlockStates_fini_function(void * message_memory)
{
  auto typed_message = static_cast<jenga_interfaces::msg::JengaBlockStates *>(message_memory);
  typed_message->~JengaBlockStates();
}

size_t size_function__JengaBlockStates__blocks(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<jenga_interfaces::msg::JengaBlockState> *>(untyped_member);
  return member->size();
}

const void * get_const_function__JengaBlockStates__blocks(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<jenga_interfaces::msg::JengaBlockState> *>(untyped_member);
  return &member[index];
}

void * get_function__JengaBlockStates__blocks(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<jenga_interfaces::msg::JengaBlockState> *>(untyped_member);
  return &member[index];
}

void fetch_function__JengaBlockStates__blocks(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const jenga_interfaces::msg::JengaBlockState *>(
    get_const_function__JengaBlockStates__blocks(untyped_member, index));
  auto & value = *reinterpret_cast<jenga_interfaces::msg::JengaBlockState *>(untyped_value);
  value = item;
}

void assign_function__JengaBlockStates__blocks(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<jenga_interfaces::msg::JengaBlockState *>(
    get_function__JengaBlockStates__blocks(untyped_member, index));
  const auto & value = *reinterpret_cast<const jenga_interfaces::msg::JengaBlockState *>(untyped_value);
  item = value;
}

void resize_function__JengaBlockStates__blocks(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<jenga_interfaces::msg::JengaBlockState> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember JengaBlockStates_message_member_array[2] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::msg::JengaBlockStates, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "blocks",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<jenga_interfaces::msg::JengaBlockState>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(jenga_interfaces::msg::JengaBlockStates, blocks),  // bytes offset in struct
    nullptr,  // default value
    size_function__JengaBlockStates__blocks,  // size() function pointer
    get_const_function__JengaBlockStates__blocks,  // get_const(index) function pointer
    get_function__JengaBlockStates__blocks,  // get(index) function pointer
    fetch_function__JengaBlockStates__blocks,  // fetch(index, &value) function pointer
    assign_function__JengaBlockStates__blocks,  // assign(index, value) function pointer
    resize_function__JengaBlockStates__blocks  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers JengaBlockStates_message_members = {
  "jenga_interfaces::msg",  // message namespace
  "JengaBlockStates",  // message name
  2,  // number of fields
  sizeof(jenga_interfaces::msg::JengaBlockStates),
  JengaBlockStates_message_member_array,  // message members
  JengaBlockStates_init_function,  // function to initialize message memory (memory has to be allocated)
  JengaBlockStates_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t JengaBlockStates_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &JengaBlockStates_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace jenga_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<jenga_interfaces::msg::JengaBlockStates>()
{
  return &::jenga_interfaces::msg::rosidl_typesupport_introspection_cpp::JengaBlockStates_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, jenga_interfaces, msg, JengaBlockStates)() {
  return &::jenga_interfaces::msg::rosidl_typesupport_introspection_cpp::JengaBlockStates_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
