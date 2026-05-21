// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:srv/ProtrudeJengaBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__STRUCT_H_
#define JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'axis'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/ProtrudeJengaBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__srv__ProtrudeJengaBlock_Request
{
  uint32_t block_index;
  double distance_m;
  rosidl_runtime_c__String axis;
} jenga_interfaces__srv__ProtrudeJengaBlock_Request;

// Struct for a sequence of jenga_interfaces__srv__ProtrudeJengaBlock_Request.
typedef struct jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence
{
  jenga_interfaces__srv__ProtrudeJengaBlock_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/ProtrudeJengaBlock in the package jenga_interfaces.
typedef struct jenga_interfaces__srv__ProtrudeJengaBlock_Response
{
  bool success;
  rosidl_runtime_c__String message;
} jenga_interfaces__srv__ProtrudeJengaBlock_Response;

// Struct for a sequence of jenga_interfaces__srv__ProtrudeJengaBlock_Response.
typedef struct jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence
{
  jenga_interfaces__srv__ProtrudeJengaBlock_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__STRUCT_H_
