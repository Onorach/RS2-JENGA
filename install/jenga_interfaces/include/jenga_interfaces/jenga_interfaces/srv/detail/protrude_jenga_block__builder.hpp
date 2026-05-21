// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from jenga_interfaces:srv/ProtrudeJengaBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__BUILDER_HPP_
#define JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "jenga_interfaces/srv/detail/protrude_jenga_block__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace jenga_interfaces
{

namespace srv
{

namespace builder
{

class Init_ProtrudeJengaBlock_Request_axis
{
public:
  explicit Init_ProtrudeJengaBlock_Request_axis(::jenga_interfaces::srv::ProtrudeJengaBlock_Request & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::srv::ProtrudeJengaBlock_Request axis(::jenga_interfaces::srv::ProtrudeJengaBlock_Request::_axis_type arg)
  {
    msg_.axis = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::srv::ProtrudeJengaBlock_Request msg_;
};

class Init_ProtrudeJengaBlock_Request_distance_m
{
public:
  explicit Init_ProtrudeJengaBlock_Request_distance_m(::jenga_interfaces::srv::ProtrudeJengaBlock_Request & msg)
  : msg_(msg)
  {}
  Init_ProtrudeJengaBlock_Request_axis distance_m(::jenga_interfaces::srv::ProtrudeJengaBlock_Request::_distance_m_type arg)
  {
    msg_.distance_m = std::move(arg);
    return Init_ProtrudeJengaBlock_Request_axis(msg_);
  }

private:
  ::jenga_interfaces::srv::ProtrudeJengaBlock_Request msg_;
};

class Init_ProtrudeJengaBlock_Request_block_index
{
public:
  Init_ProtrudeJengaBlock_Request_block_index()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ProtrudeJengaBlock_Request_distance_m block_index(::jenga_interfaces::srv::ProtrudeJengaBlock_Request::_block_index_type arg)
  {
    msg_.block_index = std::move(arg);
    return Init_ProtrudeJengaBlock_Request_distance_m(msg_);
  }

private:
  ::jenga_interfaces::srv::ProtrudeJengaBlock_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::srv::ProtrudeJengaBlock_Request>()
{
  return jenga_interfaces::srv::builder::Init_ProtrudeJengaBlock_Request_block_index();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace srv
{

namespace builder
{

class Init_ProtrudeJengaBlock_Response_message
{
public:
  explicit Init_ProtrudeJengaBlock_Response_message(::jenga_interfaces::srv::ProtrudeJengaBlock_Response & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::srv::ProtrudeJengaBlock_Response message(::jenga_interfaces::srv::ProtrudeJengaBlock_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::srv::ProtrudeJengaBlock_Response msg_;
};

class Init_ProtrudeJengaBlock_Response_success
{
public:
  Init_ProtrudeJengaBlock_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ProtrudeJengaBlock_Response_message success(::jenga_interfaces::srv::ProtrudeJengaBlock_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_ProtrudeJengaBlock_Response_message(msg_);
  }

private:
  ::jenga_interfaces::srv::ProtrudeJengaBlock_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::srv::ProtrudeJengaBlock_Response>()
{
  return jenga_interfaces::srv::builder::Init_ProtrudeJengaBlock_Response_success();
}

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__BUILDER_HPP_
