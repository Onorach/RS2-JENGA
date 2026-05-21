// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from jenga_interfaces:srv/ProtrudeJengaBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__TRAITS_HPP_
#define JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "jenga_interfaces/srv/detail/protrude_jenga_block__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace jenga_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const ProtrudeJengaBlock_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: block_index
  {
    out << "block_index: ";
    rosidl_generator_traits::value_to_yaml(msg.block_index, out);
    out << ", ";
  }

  // member: distance_m
  {
    out << "distance_m: ";
    rosidl_generator_traits::value_to_yaml(msg.distance_m, out);
    out << ", ";
  }

  // member: axis
  {
    out << "axis: ";
    rosidl_generator_traits::value_to_yaml(msg.axis, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ProtrudeJengaBlock_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: block_index
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "block_index: ";
    rosidl_generator_traits::value_to_yaml(msg.block_index, out);
    out << "\n";
  }

  // member: distance_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "distance_m: ";
    rosidl_generator_traits::value_to_yaml(msg.distance_m, out);
    out << "\n";
  }

  // member: axis
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "axis: ";
    rosidl_generator_traits::value_to_yaml(msg.axis, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ProtrudeJengaBlock_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::srv::ProtrudeJengaBlock_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::srv::ProtrudeJengaBlock_Request & msg)
{
  return jenga_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::srv::ProtrudeJengaBlock_Request>()
{
  return "jenga_interfaces::srv::ProtrudeJengaBlock_Request";
}

template<>
inline const char * name<jenga_interfaces::srv::ProtrudeJengaBlock_Request>()
{
  return "jenga_interfaces/srv/ProtrudeJengaBlock_Request";
}

template<>
struct has_fixed_size<jenga_interfaces::srv::ProtrudeJengaBlock_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<jenga_interfaces::srv::ProtrudeJengaBlock_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<jenga_interfaces::srv::ProtrudeJengaBlock_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace jenga_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const ProtrudeJengaBlock_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ProtrudeJengaBlock_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ProtrudeJengaBlock_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::srv::ProtrudeJengaBlock_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::srv::ProtrudeJengaBlock_Response & msg)
{
  return jenga_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::srv::ProtrudeJengaBlock_Response>()
{
  return "jenga_interfaces::srv::ProtrudeJengaBlock_Response";
}

template<>
inline const char * name<jenga_interfaces::srv::ProtrudeJengaBlock_Response>()
{
  return "jenga_interfaces/srv/ProtrudeJengaBlock_Response";
}

template<>
struct has_fixed_size<jenga_interfaces::srv::ProtrudeJengaBlock_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<jenga_interfaces::srv::ProtrudeJengaBlock_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<jenga_interfaces::srv::ProtrudeJengaBlock_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<jenga_interfaces::srv::ProtrudeJengaBlock>()
{
  return "jenga_interfaces::srv::ProtrudeJengaBlock";
}

template<>
inline const char * name<jenga_interfaces::srv::ProtrudeJengaBlock>()
{
  return "jenga_interfaces/srv/ProtrudeJengaBlock";
}

template<>
struct has_fixed_size<jenga_interfaces::srv::ProtrudeJengaBlock>
  : std::integral_constant<
    bool,
    has_fixed_size<jenga_interfaces::srv::ProtrudeJengaBlock_Request>::value &&
    has_fixed_size<jenga_interfaces::srv::ProtrudeJengaBlock_Response>::value
  >
{
};

template<>
struct has_bounded_size<jenga_interfaces::srv::ProtrudeJengaBlock>
  : std::integral_constant<
    bool,
    has_bounded_size<jenga_interfaces::srv::ProtrudeJengaBlock_Request>::value &&
    has_bounded_size<jenga_interfaces::srv::ProtrudeJengaBlock_Response>::value
  >
{
};

template<>
struct is_service<jenga_interfaces::srv::ProtrudeJengaBlock>
  : std::true_type
{
};

template<>
struct is_service_request<jenga_interfaces::srv::ProtrudeJengaBlock_Request>
  : std::true_type
{
};

template<>
struct is_service_response<jenga_interfaces::srv::ProtrudeJengaBlock_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__TRAITS_HPP_
