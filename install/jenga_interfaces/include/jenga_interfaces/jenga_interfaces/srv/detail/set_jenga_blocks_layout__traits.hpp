// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from jenga_interfaces:srv/SetJengaBlocksLayout.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__TRAITS_HPP_
#define JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace jenga_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetJengaBlocksLayout_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: block_indices
  {
    if (msg.block_indices.size() == 0) {
      out << "block_indices: []";
    } else {
      out << "block_indices: [";
      size_t pending_items = msg.block_indices.size();
      for (auto item : msg.block_indices) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: target_layout
  {
    out << "target_layout: ";
    rosidl_generator_traits::value_to_yaml(msg.target_layout, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetJengaBlocksLayout_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: block_indices
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.block_indices.size() == 0) {
      out << "block_indices: []\n";
    } else {
      out << "block_indices:\n";
      for (auto item : msg.block_indices) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: target_layout
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "target_layout: ";
    rosidl_generator_traits::value_to_yaml(msg.target_layout, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetJengaBlocksLayout_Request & msg, bool use_flow_style = false)
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
  const jenga_interfaces::srv::SetJengaBlocksLayout_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::srv::SetJengaBlocksLayout_Request & msg)
{
  return jenga_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::srv::SetJengaBlocksLayout_Request>()
{
  return "jenga_interfaces::srv::SetJengaBlocksLayout_Request";
}

template<>
inline const char * name<jenga_interfaces::srv::SetJengaBlocksLayout_Request>()
{
  return "jenga_interfaces/srv/SetJengaBlocksLayout_Request";
}

template<>
struct has_fixed_size<jenga_interfaces::srv::SetJengaBlocksLayout_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<jenga_interfaces::srv::SetJengaBlocksLayout_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<jenga_interfaces::srv::SetJengaBlocksLayout_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace jenga_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetJengaBlocksLayout_Response & msg,
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
  const SetJengaBlocksLayout_Response & msg,
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

inline std::string to_yaml(const SetJengaBlocksLayout_Response & msg, bool use_flow_style = false)
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
  const jenga_interfaces::srv::SetJengaBlocksLayout_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::srv::SetJengaBlocksLayout_Response & msg)
{
  return jenga_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::srv::SetJengaBlocksLayout_Response>()
{
  return "jenga_interfaces::srv::SetJengaBlocksLayout_Response";
}

template<>
inline const char * name<jenga_interfaces::srv::SetJengaBlocksLayout_Response>()
{
  return "jenga_interfaces/srv/SetJengaBlocksLayout_Response";
}

template<>
struct has_fixed_size<jenga_interfaces::srv::SetJengaBlocksLayout_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<jenga_interfaces::srv::SetJengaBlocksLayout_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<jenga_interfaces::srv::SetJengaBlocksLayout_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<jenga_interfaces::srv::SetJengaBlocksLayout>()
{
  return "jenga_interfaces::srv::SetJengaBlocksLayout";
}

template<>
inline const char * name<jenga_interfaces::srv::SetJengaBlocksLayout>()
{
  return "jenga_interfaces/srv/SetJengaBlocksLayout";
}

template<>
struct has_fixed_size<jenga_interfaces::srv::SetJengaBlocksLayout>
  : std::integral_constant<
    bool,
    has_fixed_size<jenga_interfaces::srv::SetJengaBlocksLayout_Request>::value &&
    has_fixed_size<jenga_interfaces::srv::SetJengaBlocksLayout_Response>::value
  >
{
};

template<>
struct has_bounded_size<jenga_interfaces::srv::SetJengaBlocksLayout>
  : std::integral_constant<
    bool,
    has_bounded_size<jenga_interfaces::srv::SetJengaBlocksLayout_Request>::value &&
    has_bounded_size<jenga_interfaces::srv::SetJengaBlocksLayout_Response>::value
  >
{
};

template<>
struct is_service<jenga_interfaces::srv::SetJengaBlocksLayout>
  : std::true_type
{
};

template<>
struct is_service_request<jenga_interfaces::srv::SetJengaBlocksLayout_Request>
  : std::true_type
{
};

template<>
struct is_service_response<jenga_interfaces::srv::SetJengaBlocksLayout_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__TRAITS_HPP_
