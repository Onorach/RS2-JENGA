// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:action/JengaProbeBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__STRUCT_H_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__STRUCT_H_

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
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_Goal
{
  uint32_t block_index;
  geometry_msgs__msg__PoseStamped block_pose;
} jenga_interfaces__action__JengaProbeBlock_Goal;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_Goal.
typedef struct jenga_interfaces__action__JengaProbeBlock_Goal__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_Result
{
  bool success;
  rosidl_runtime_c__String message;
  uint8_t error_code;
  float score;
  /// 0=UNKNOWN, 1=LOOSE, 2=STUCK, 3=ERROR
  uint8_t probe_outcome;
  /// actual distance pushed along probe axis
  float displacement_m;
  /// peak contact force observed during push
  float max_force_n;
} jenga_interfaces__action__JengaProbeBlock_Result;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_Result.
typedef struct jenga_interfaces__action__JengaProbeBlock_Result__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'current_stage'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_Feedback
{
  rosidl_runtime_c__String current_stage;
  float progress_pct;
} jenga_interfaces__action__JengaProbeBlock_Feedback;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_Feedback.
typedef struct jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "jenga_interfaces/action/detail/jenga_probe_block__struct.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaProbeBlock_Goal goal;
} jenga_interfaces__action__JengaProbeBlock_SendGoal_Request;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_SendGoal_Request.
typedef struct jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} jenga_interfaces__action__JengaProbeBlock_SendGoal_Response;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_SendGoal_Response.
typedef struct jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} jenga_interfaces__action__JengaProbeBlock_GetResult_Request;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_GetResult_Request.
typedef struct jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "jenga_interfaces/action/detail/jenga_probe_block__struct.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_GetResult_Response
{
  int8_t status;
  jenga_interfaces__action__JengaProbeBlock_Result result;
} jenga_interfaces__action__JengaProbeBlock_GetResult_Response;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_GetResult_Response.
typedef struct jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "jenga_interfaces/action/detail/jenga_probe_block__struct.h"

/// Struct defined in action/JengaProbeBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaProbeBlock_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaProbeBlock_Feedback feedback;
} jenga_interfaces__action__JengaProbeBlock_FeedbackMessage;

// Struct for a sequence of jenga_interfaces__action__JengaProbeBlock_FeedbackMessage.
typedef struct jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence
{
  jenga_interfaces__action__JengaProbeBlock_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__STRUCT_H_
