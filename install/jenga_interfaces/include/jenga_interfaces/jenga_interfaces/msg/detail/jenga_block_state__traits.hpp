// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from jenga_interfaces:msg/JengaBlockState.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__TRAITS_HPP_
#define JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "jenga_interfaces/msg/detail/jenga_block_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__traits.hpp"

namespace jenga_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const JengaBlockState & msg,
  std::ostream & out)
{
  out << "{";
  // member: block_id
  {
    out << "block_id: ";
    rosidl_generator_traits::value_to_yaml(msg.block_id, out);
    out << ", ";
  }

  // member: colour
  {
    out << "colour: ";
    rosidl_generator_traits::value_to_yaml(msg.colour, out);
    out << ", ";
  }

  // member: layer
  {
    out << "layer: ";
    rosidl_generator_traits::value_to_yaml(msg.layer, out);
    out << ", ";
  }

  // member: layer_position
  {
    out << "layer_position: ";
    rosidl_generator_traits::value_to_yaml(msg.layer_position, out);
    out << ", ";
  }

  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaBlockState & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: block_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "block_id: ";
    rosidl_generator_traits::value_to_yaml(msg.block_id, out);
    out << "\n";
  }

  // member: colour
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "colour: ";
    rosidl_generator_traits::value_to_yaml(msg.colour, out);
    out << "\n";
  }

  // member: layer
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "layer: ";
    rosidl_generator_traits::value_to_yaml(msg.layer, out);
    out << "\n";
  }

  // member: layer_position
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "layer_position: ";
    rosidl_generator_traits::value_to_yaml(msg.layer_position, out);
    out << "\n";
  }

  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaBlockState & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::msg::JengaBlockState & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::msg::JengaBlockState & msg)
{
  return jenga_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::msg::JengaBlockState>()
{
  return "jenga_interfaces::msg::JengaBlockState";
}

template<>
inline const char * name<jenga_interfaces::msg::JengaBlockState>()
{
  return "jenga_interfaces/msg/JengaBlockState";
}

template<>
struct has_fixed_size<jenga_interfaces::msg::JengaBlockState>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<jenga_interfaces::msg::JengaBlockState>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<jenga_interfaces::msg::JengaBlockState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__TRAITS_HPP_
