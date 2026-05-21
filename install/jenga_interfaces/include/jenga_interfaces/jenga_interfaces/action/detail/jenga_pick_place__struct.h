// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:action/JengaPickPlace.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_PICK_PLACE__STRUCT_H_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_PICK_PLACE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pick_pose'
// Member 'place_pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_Goal
{
  uint32_t block_index;
  geometry_msgs__msg__PoseStamped pick_pose;
  geometry_msgs__msg__PoseStamped place_pose;
} jenga_interfaces__action__JengaPickPlace_Goal;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_Goal.
typedef struct jenga_interfaces__action__JengaPickPlace_Goal__Sequence
{
  jenga_interfaces__action__JengaPickPlace_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_Result
{
  bool success;
  rosidl_runtime_c__String message;
  uint8_t error_code;
} jenga_interfaces__action__JengaPickPlace_Result;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_Result.
typedef struct jenga_interfaces__action__JengaPickPlace_Result__Sequence
{
  jenga_interfaces__action__JengaPickPlace_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'current_stage'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_Feedback
{
  rosidl_runtime_c__String current_stage;
  float progress_pct;
} jenga_interfaces__action__JengaPickPlace_Feedback;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_Feedback.
typedef struct jenga_interfaces__action__JengaPickPlace_Feedback__Sequence
{
  jenga_interfaces__action__JengaPickPlace_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "jenga_interfaces/action/detail/jenga_pick_place__struct.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaPickPlace_Goal goal;
} jenga_interfaces__action__JengaPickPlace_SendGoal_Request;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_SendGoal_Request.
typedef struct jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence
{
  jenga_interfaces__action__JengaPickPlace_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} jenga_interfaces__action__JengaPickPlace_SendGoal_Response;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_SendGoal_Response.
typedef struct jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence
{
  jenga_interfaces__action__JengaPickPlace_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} jenga_interfaces__action__JengaPickPlace_GetResult_Request;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_GetResult_Request.
typedef struct jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence
{
  jenga_interfaces__action__JengaPickPlace_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "jenga_interfaces/action/detail/jenga_pick_place__struct.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_GetResult_Response
{
  int8_t status;
  jenga_interfaces__action__JengaPickPlace_Result result;
} jenga_interfaces__action__JengaPickPlace_GetResult_Response;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_GetResult_Response.
typedef struct jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence
{
  jenga_interfaces__action__JengaPickPlace_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "jenga_interfaces/action/detail/jenga_pick_place__struct.h"

/// Struct defined in action/JengaPickPlace in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaPickPlace_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaPickPlace_Feedback feedback;
} jenga_interfaces__action__JengaPickPlace_FeedbackMessage;

// Struct for a sequence of jenga_interfaces__action__JengaPickPlace_FeedbackMessage.
typedef struct jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence
{
  jenga_interfaces__action__JengaPickPlace_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_PICK_PLACE__STRUCT_H_
