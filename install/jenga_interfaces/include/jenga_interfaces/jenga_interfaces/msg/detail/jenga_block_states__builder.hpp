// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from jenga_interfaces:msg/JengaBlockStates.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATES__BUILDER_HPP_
#define JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATES__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "jenga_interfaces/msg/detail/jenga_block_states__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace jenga_interfaces
{

namespace msg
{

namespace builder
{

class Init_JengaBlockStates_blocks
{
public:
  explicit Init_JengaBlockStates_blocks(::jenga_interfaces::msg::JengaBlockStates & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::msg::JengaBlockStates blocks(::jenga_interfaces::msg::JengaBlockStates::_blocks_type arg)
  {
    msg_.blocks = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::msg::JengaBlockStates msg_;
};

class Init_JengaBlockStates_header
{
public:
  Init_JengaBlockStates_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaBlockStates_blocks header(::jenga_interfaces::msg::JengaBlockStates::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_JengaBlockStates_blocks(msg_);
  }

private:
  ::jenga_interfaces::msg::JengaBlockStates msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::msg::JengaBlockStates>()
{
  return jenga_interfaces::msg::builder::Init_JengaBlockStates_header();
}

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATES__BUILDER_HPP_
