// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:action/JengaExtractMiddleBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_MIDDLE_BLOCK__STRUCT_H_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_MIDDLE_BLOCK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'block_pose'
// Member 'place_pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"
// Member 'extract_axis'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_Goal
{
  uint32_t block_index;
  geometry_msgs__msg__PoseStamped block_pose;
  geometry_msgs__msg__PoseStamped place_pose;
  /// e.g. "x", "-x". Empty string → auto-detect from planning scene; explicit string → override.
  rosidl_runtime_c__String extract_axis;
} jenga_interfaces__action__JengaExtractMiddleBlock_Goal;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_Goal.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_Result
{
  bool success;
  rosidl_runtime_c__String message;
  uint8_t error_code;
} jenga_interfaces__action__JengaExtractMiddleBlock_Result;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_Result.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'current_stage'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_Feedback
{
  rosidl_runtime_c__String current_stage;
  float progress_pct;
} jenga_interfaces__action__JengaExtractMiddleBlock_Feedback;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_Feedback.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaExtractMiddleBlock_Goal goal;
} jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response
{
  int8_t status;
  jenga_interfaces__action__JengaExtractMiddleBlock_Result result;
} jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.h"

/// Struct defined in action/JengaExtractMiddleBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaExtractMiddleBlock_Feedback feedback;
} jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage;

// Struct for a sequence of jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage.
typedef struct jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence
{
  jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_MIDDLE_BLOCK__STRUCT_H_
