// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:action/JengaExtractSideBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_SIDE_BLOCK__STRUCT_H_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_SIDE_BLOCK__STRUCT_H_

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

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_Goal
{
  uint32_t block_index;
  geometry_msgs__msg__PoseStamped block_pose;
  geometry_msgs__msg__PoseStamped place_pose;
} jenga_interfaces__action__JengaExtractSideBlock_Goal;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_Goal.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_Result
{
  bool success;
  rosidl_runtime_c__String message;
  uint8_t error_code;
} jenga_interfaces__action__JengaExtractSideBlock_Result;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_Result.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'current_stage'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_Feedback
{
  rosidl_runtime_c__String current_stage;
  float progress_pct;
} jenga_interfaces__action__JengaExtractSideBlock_Feedback;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_Feedback.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "jenga_interfaces/action/detail/jenga_extract_side_block__struct.h"

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaExtractSideBlock_Goal goal;
} jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_side_block__struct.h"

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response
{
  int8_t status;
  jenga_interfaces__action__JengaExtractSideBlock_Result result;
} jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_side_block__struct.h"

/// Struct defined in action/JengaExtractSideBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaExtractSideBlock_Feedback feedback;
} jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage;

// Struct for a sequence of jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage.
typedef struct jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence
{
  jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_SIDE_BLOCK__STRUCT_H_
