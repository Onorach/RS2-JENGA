// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from jenga_interfaces:action/JengaProbeBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__TRAITS_HPP_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "jenga_interfaces/action/detail/jenga_probe_block__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'block_pose'
#include "geometry_msgs/msg/detail/pose_stamped__traits.hpp"

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_Goal & msg,
  std::ostream & out)
{
  out << "{";
  // member: block_index
  {
    out << "block_index: ";
    rosidl_generator_traits::value_to_yaml(msg.block_index, out);
    out << ", ";
  }

  // member: block_pose
  {
    out << "block_pose: ";
    to_flow_style_yaml(msg.block_pose, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_Goal & msg,
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

  // member: block_pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "block_pose:\n";
    to_block_style_yaml(msg.block_pose, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_Goal & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_Goal & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_Goal & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_Goal>()
{
  return "jenga_interfaces::action::JengaProbeBlock_Goal";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_Goal>()
{
  return "jenga_interfaces/action/JengaProbeBlock_Goal";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_Goal>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::PoseStamped>::value> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_Goal>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::PoseStamped>::value> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_Goal>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_Result & msg,
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
    out << ", ";
  }

  // member: error_code
  {
    out << "error_code: ";
    rosidl_generator_traits::value_to_yaml(msg.error_code, out);
    out << ", ";
  }

  // member: score
  {
    out << "score: ";
    rosidl_generator_traits::value_to_yaml(msg.score, out);
    out << ", ";
  }

  // member: probe_outcome
  {
    out << "probe_outcome: ";
    rosidl_generator_traits::value_to_yaml(msg.probe_outcome, out);
    out << ", ";
  }

  // member: displacement_m
  {
    out << "displacement_m: ";
    rosidl_generator_traits::value_to_yaml(msg.displacement_m, out);
    out << ", ";
  }

  // member: max_force_n
  {
    out << "max_force_n: ";
    rosidl_generator_traits::value_to_yaml(msg.max_force_n, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_Result & msg,
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

  // member: error_code
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "error_code: ";
    rosidl_generator_traits::value_to_yaml(msg.error_code, out);
    out << "\n";
  }

  // member: score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "score: ";
    rosidl_generator_traits::value_to_yaml(msg.score, out);
    out << "\n";
  }

  // member: probe_outcome
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "probe_outcome: ";
    rosidl_generator_traits::value_to_yaml(msg.probe_outcome, out);
    out << "\n";
  }

  // member: displacement_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "displacement_m: ";
    rosidl_generator_traits::value_to_yaml(msg.displacement_m, out);
    out << "\n";
  }

  // member: max_force_n
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "max_force_n: ";
    rosidl_generator_traits::value_to_yaml(msg.max_force_n, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_Result & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_Result & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_Result & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_Result>()
{
  return "jenga_interfaces::action::JengaProbeBlock_Result";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_Result>()
{
  return "jenga_interfaces/action/JengaProbeBlock_Result";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_Result>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_Result>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_Result>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_Feedback & msg,
  std::ostream & out)
{
  out << "{";
  // member: current_stage
  {
    out << "current_stage: ";
    rosidl_generator_traits::value_to_yaml(msg.current_stage, out);
    out << ", ";
  }

  // member: progress_pct
  {
    out << "progress_pct: ";
    rosidl_generator_traits::value_to_yaml(msg.progress_pct, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: current_stage
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "current_stage: ";
    rosidl_generator_traits::value_to_yaml(msg.current_stage, out);
    out << "\n";
  }

  // member: progress_pct
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "progress_pct: ";
    rosidl_generator_traits::value_to_yaml(msg.progress_pct, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_Feedback & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_Feedback & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_Feedback>()
{
  return "jenga_interfaces::action::JengaProbeBlock_Feedback";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_Feedback>()
{
  return "jenga_interfaces/action/JengaProbeBlock_Feedback";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_Feedback>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'goal'
#include "jenga_interfaces/action/detail/jenga_probe_block__traits.hpp"

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_SendGoal_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: goal
  {
    out << "goal: ";
    to_flow_style_yaml(msg.goal, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: goal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal:\n";
    to_block_style_yaml(msg.goal, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_SendGoal_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_SendGoal_Request & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>()
{
  return "jenga_interfaces::action::JengaProbeBlock_SendGoal_Request";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>()
{
  return "jenga_interfaces/action/JengaProbeBlock_SendGoal_Request";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>
  : std::integral_constant<bool, has_fixed_size<jenga_interfaces::action::JengaProbeBlock_Goal>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>
  : std::integral_constant<bool, has_bounded_size<jenga_interfaces::action::JengaProbeBlock_Goal>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_SendGoal_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: accepted
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << "\n";
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_SendGoal_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_SendGoal_Response & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>()
{
  return "jenga_interfaces::action::JengaProbeBlock_SendGoal_Response";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>()
{
  return "jenga_interfaces/action/JengaProbeBlock_SendGoal_Response";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_SendGoal>()
{
  return "jenga_interfaces::action::JengaProbeBlock_SendGoal";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_SendGoal>()
{
  return "jenga_interfaces/action/JengaProbeBlock_SendGoal";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_SendGoal>
  : std::integral_constant<
    bool,
    has_fixed_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>::value &&
    has_fixed_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>::value
  >
{
};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_SendGoal>
  : std::integral_constant<
    bool,
    has_bounded_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>::value &&
    has_bounded_size<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>::value
  >
{
};

template<>
struct is_service<jenga_interfaces::action::JengaProbeBlock_SendGoal>
  : std::true_type
{
};

template<>
struct is_service_request<jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>
  : std::true_type
{
};

template<>
struct is_service_response<jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_GetResult_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_GetResult_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_GetResult_Request & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>()
{
  return "jenga_interfaces::action::JengaProbeBlock_GetResult_Request";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>()
{
  return "jenga_interfaces/action/JengaProbeBlock_GetResult_Request";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>
  : std::integral_constant<bool, has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>
  : std::integral_constant<bool, has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'result'
// already included above
// #include "jenga_interfaces/action/detail/jenga_probe_block__traits.hpp"

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_GetResult_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: status
  {
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << ", ";
  }

  // member: result
  {
    out << "result: ";
    to_flow_style_yaml(msg.result, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << "\n";
  }

  // member: result
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "result:\n";
    to_block_style_yaml(msg.result, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_GetResult_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_GetResult_Response & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>()
{
  return "jenga_interfaces::action::JengaProbeBlock_GetResult_Response";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>()
{
  return "jenga_interfaces/action/JengaProbeBlock_GetResult_Response";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>
  : std::integral_constant<bool, has_fixed_size<jenga_interfaces::action::JengaProbeBlock_Result>::value> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>
  : std::integral_constant<bool, has_bounded_size<jenga_interfaces::action::JengaProbeBlock_Result>::value> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_GetResult>()
{
  return "jenga_interfaces::action::JengaProbeBlock_GetResult";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_GetResult>()
{
  return "jenga_interfaces/action/JengaProbeBlock_GetResult";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_GetResult>
  : std::integral_constant<
    bool,
    has_fixed_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>::value &&
    has_fixed_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>::value
  >
{
};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_GetResult>
  : std::integral_constant<
    bool,
    has_bounded_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>::value &&
    has_bounded_size<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>::value
  >
{
};

template<>
struct is_service<jenga_interfaces::action::JengaProbeBlock_GetResult>
  : std::true_type
{
};

template<>
struct is_service_request<jenga_interfaces::action::JengaProbeBlock_GetResult_Request>
  : std::true_type
{
};

template<>
struct is_service_response<jenga_interfaces::action::JengaProbeBlock_GetResult_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'feedback'
// already included above
// #include "jenga_interfaces/action/detail/jenga_probe_block__traits.hpp"

namespace jenga_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const JengaProbeBlock_FeedbackMessage & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: feedback
  {
    out << "feedback: ";
    to_flow_style_yaml(msg.feedback, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const JengaProbeBlock_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: feedback
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "feedback:\n";
    to_block_style_yaml(msg.feedback, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const JengaProbeBlock_FeedbackMessage & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace jenga_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use jenga_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const jenga_interfaces::action::JengaProbeBlock_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  jenga_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use jenga_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const jenga_interfaces::action::JengaProbeBlock_FeedbackMessage & msg)
{
  return jenga_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<jenga_interfaces::action::JengaProbeBlock_FeedbackMessage>()
{
  return "jenga_interfaces::action::JengaProbeBlock_FeedbackMessage";
}

template<>
inline const char * name<jenga_interfaces::action::JengaProbeBlock_FeedbackMessage>()
{
  return "jenga_interfaces/action/JengaProbeBlock_FeedbackMessage";
}

template<>
struct has_fixed_size<jenga_interfaces::action::JengaProbeBlock_FeedbackMessage>
  : std::integral_constant<bool, has_fixed_size<jenga_interfaces::action::JengaProbeBlock_Feedback>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<jenga_interfaces::action::JengaProbeBlock_FeedbackMessage>
  : std::integral_constant<bool, has_bounded_size<jenga_interfaces::action::JengaProbeBlock_Feedback>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<jenga_interfaces::action::JengaProbeBlock_FeedbackMessage>
  : std::true_type {};

}  // namespace rosidl_generator_traits


namespace rosidl_generator_traits
{

template<>
struct is_action<jenga_interfaces::action::JengaProbeBlock>
  : std::true_type
{
};

template<>
struct is_action_goal<jenga_interfaces::action::JengaProbeBlock_Goal>
  : std::true_type
{
};

template<>
struct is_action_result<jenga_interfaces::action::JengaProbeBlock_Result>
  : std::true_type
{
};

template<>
struct is_action_feedback<jenga_interfaces::action::JengaProbeBlock_Feedback>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits


#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__TRAITS_HPP_
