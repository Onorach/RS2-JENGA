// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:msg/JengaBlockState.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__STRUCT_H_
#define JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'colour'
#include "rosidl_runtime_c/string.h"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.h"

/// Struct defined in msg/JengaBlockState in the package jenga_interfaces.
typedef struct jenga_interfaces__msg__JengaBlockState
{
  uint32_t block_id;
  rosidl_runtime_c__String colour;
  uint32_t layer;
  uint8_t layer_position;
  geometry_msgs__msg__Pose pose;
} jenga_interfaces__msg__JengaBlockState;

// Struct for a sequence of jenga_interfaces__msg__JengaBlockState.
typedef struct jenga_interfaces__msg__JengaBlockState__Sequence
{
  jenga_interfaces__msg__JengaBlockState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__msg__JengaBlockState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__STRUCT_H_
