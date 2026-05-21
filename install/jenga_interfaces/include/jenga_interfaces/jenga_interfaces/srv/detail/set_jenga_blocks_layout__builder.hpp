// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from jenga_interfaces:srv/SetJengaBlocksLayout.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__BUILDER_HPP_
#define JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace jenga_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetJengaBlocksLayout_Request_target_layout
{
public:
  explicit Init_SetJengaBlocksLayout_Request_target_layout(::jenga_interfaces::srv::SetJengaBlocksLayout_Request & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::srv::SetJengaBlocksLayout_Request target_layout(::jenga_interfaces::srv::SetJengaBlocksLayout_Request::_target_layout_type arg)
  {
    msg_.target_layout = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::srv::SetJengaBlocksLayout_Request msg_;
};

class Init_SetJengaBlocksLayout_Request_block_indices
{
public:
  Init_SetJengaBlocksLayout_Request_block_indices()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetJengaBlocksLayout_Request_target_layout block_indices(::jenga_interfaces::srv::SetJengaBlocksLayout_Request::_block_indices_type arg)
  {
    msg_.block_indices = std::move(arg);
    return Init_SetJengaBlocksLayout_Request_target_layout(msg_);
  }

private:
  ::jenga_interfaces::srv::SetJengaBlocksLayout_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::srv::SetJengaBlocksLayout_Request>()
{
  return jenga_interfaces::srv::builder::Init_SetJengaBlocksLayout_Request_block_indices();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace srv
{

namespace builder
{

class Init_SetJengaBlocksLayout_Response_message
{
public:
  explicit Init_SetJengaBlocksLayout_Response_message(::jenga_interfaces::srv::SetJengaBlocksLayout_Response & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::srv::SetJengaBlocksLayout_Response message(::jenga_interfaces::srv::SetJengaBlocksLayout_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::srv::SetJengaBlocksLayout_Response msg_;
};

class Init_SetJengaBlocksLayout_Response_success
{
public:
  Init_SetJengaBlocksLayout_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetJengaBlocksLayout_Response_message success(::jenga_interfaces::srv::SetJengaBlocksLayout_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_SetJengaBlocksLayout_Response_message(msg_);
  }

private:
  ::jenga_interfaces::srv::SetJengaBlocksLayout_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::srv::SetJengaBlocksLayout_Response>()
{
  return jenga_interfaces::srv::builder::Init_SetJengaBlocksLayout_Response_success();
}

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__BUILDER_HPP_
