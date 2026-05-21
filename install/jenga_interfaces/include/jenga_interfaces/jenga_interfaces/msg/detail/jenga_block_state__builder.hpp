// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from jenga_interfaces:msg/JengaBlockState.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__BUILDER_HPP_
#define JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "jenga_interfaces/msg/detail/jenga_block_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace jenga_interfaces
{

namespace msg
{

namespace builder
{

class Init_JengaBlockState_pose
{
public:
  explicit Init_JengaBlockState_pose(::jenga_interfaces::msg::JengaBlockState & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::msg::JengaBlockState pose(::jenga_interfaces::msg::JengaBlockState::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::msg::JengaBlockState msg_;
};

class Init_JengaBlockState_layer_position
{
public:
  explicit Init_JengaBlockState_layer_position(::jenga_interfaces::msg::JengaBlockState & msg)
  : msg_(msg)
  {}
  Init_JengaBlockState_pose layer_position(::jenga_interfaces::msg::JengaBlockState::_layer_position_type arg)
  {
    msg_.layer_position = std::move(arg);
    return Init_JengaBlockState_pose(msg_);
  }

private:
  ::jenga_interfaces::msg::JengaBlockState msg_;
};

class Init_JengaBlockState_layer
{
public:
  explicit Init_JengaBlockState_layer(::jenga_interfaces::msg::JengaBlockState & msg)
  : msg_(msg)
  {}
  Init_JengaBlockState_layer_position layer(::jenga_interfaces::msg::JengaBlockState::_layer_type arg)
  {
    msg_.layer = std::move(arg);
    return Init_JengaBlockState_layer_position(msg_);
  }

private:
  ::jenga_interfaces::msg::JengaBlockState msg_;
};

class Init_JengaBlockState_colour
{
public:
  explicit Init_JengaBlockState_colour(::jenga_interfaces::msg::JengaBlockState & msg)
  : msg_(msg)
  {}
  Init_JengaBlockState_layer colour(::jenga_interfaces::msg::JengaBlockState::_colour_type arg)
  {
    msg_.colour = std::move(arg);
    return Init_JengaBlockState_layer(msg_);
  }

private:
  ::jenga_interfaces::msg::JengaBlockState msg_;
};

class Init_JengaBlockState_block_id
{
public:
  Init_JengaBlockState_block_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaBlockState_colour block_id(::jenga_interfaces::msg::JengaBlockState::_block_id_type arg)
  {
    msg_.block_id = std::move(arg);
    return Init_JengaBlockState_colour(msg_);
  }

private:
  ::jenga_interfaces::msg::JengaBlockState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::msg::JengaBlockState>()
{
  return jenga_interfaces::msg::builder::Init_JengaBlockState_block_id();
}

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__BUILDER_HPP_
