// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:action/JengaArmReady.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_ARM_READY__STRUCT_H_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_ARM_READY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'target_state'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_Goal
{
  rosidl_runtime_c__String target_state;
} jenga_interfaces__action__JengaArmReady_Goal;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_Goal.
typedef struct jenga_interfaces__action__JengaArmReady_Goal__Sequence
{
  jenga_interfaces__action__JengaArmReady_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_Result
{
  bool success;
  rosidl_runtime_c__String message;
  uint8_t error_code;
} jenga_interfaces__action__JengaArmReady_Result;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_Result.
typedef struct jenga_interfaces__action__JengaArmReady_Result__Sequence
{
  jenga_interfaces__action__JengaArmReady_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'current_stage'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_Feedback
{
  rosidl_runtime_c__String current_stage;
  float progress_pct;
} jenga_interfaces__action__JengaArmReady_Feedback;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_Feedback.
typedef struct jenga_interfaces__action__JengaArmReady_Feedback__Sequence
{
  jenga_interfaces__action__JengaArmReady_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "jenga_interfaces/action/detail/jenga_arm_ready__struct.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaArmReady_Goal goal;
} jenga_interfaces__action__JengaArmReady_SendGoal_Request;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_SendGoal_Request.
typedef struct jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence
{
  jenga_interfaces__action__JengaArmReady_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} jenga_interfaces__action__JengaArmReady_SendGoal_Response;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_SendGoal_Response.
typedef struct jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence
{
  jenga_interfaces__action__JengaArmReady_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} jenga_interfaces__action__JengaArmReady_GetResult_Request;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_GetResult_Request.
typedef struct jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence
{
  jenga_interfaces__action__JengaArmReady_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "jenga_interfaces/action/detail/jenga_arm_ready__struct.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_GetResult_Response
{
  int8_t status;
  jenga_interfaces__action__JengaArmReady_Result result;
} jenga_interfaces__action__JengaArmReady_GetResult_Response;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_GetResult_Response.
typedef struct jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence
{
  jenga_interfaces__action__JengaArmReady_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "jenga_interfaces/action/detail/jenga_arm_ready__struct.h"

/// Struct defined in action/JengaArmReady in the package jenga_interfaces.
typedef struct jenga_interfaces__action__JengaArmReady_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  jenga_interfaces__action__JengaArmReady_Feedback feedback;
} jenga_interfaces__action__JengaArmReady_FeedbackMessage;

// Struct for a sequence of jenga_interfaces__action__JengaArmReady_FeedbackMessage.
typedef struct jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence
{
  jenga_interfaces__action__JengaArmReady_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_ARM_READY__STRUCT_H_
