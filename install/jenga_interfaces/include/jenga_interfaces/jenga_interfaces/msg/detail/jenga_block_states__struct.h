// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from jenga_interfaces:msg/JengaBlockStates.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATES__STRUCT_H_
#define JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATES__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'blocks'
#include "jenga_interfaces/msg/detail/jenga_block_state__struct.h"

/// Struct defined in msg/JengaBlockStates in the package jenga_interfaces.
typedef struct jenga_interfaces__msg__JengaBlockStates
{
  std_msgs__msg__Header header;
  jenga_interfaces__msg__JengaBlockState__Sequence blocks;
} jenga_interfaces__msg__JengaBlockStates;

// Struct for a sequence of jenga_interfaces__msg__JengaBlockStates.
typedef struct jenga_interfaces__msg__JengaBlockStates__Sequence
{
  jenga_interfaces__msg__JengaBlockStates * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} jenga_interfaces__msg__JengaBlockStates__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATES__STRUCT_H_
