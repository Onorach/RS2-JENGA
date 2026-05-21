// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from jenga_interfaces:msg/JengaBlockState.idl
// generated code does not contain a copyright notice
#include "jenga_interfaces/msg/detail/jenga_block_state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `colour`
#include "rosidl_runtime_c/string_functions.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose__functions.h"

bool
jenga_interfaces__msg__JengaBlockState__init(jenga_interfaces__msg__JengaBlockState * msg)
{
  if (!msg) {
    return false;
  }
  // block_id
  // colour
  if (!rosidl_runtime_c__String__init(&msg->colour)) {
    jenga_interfaces__msg__JengaBlockState__fini(msg);
    return false;
  }
  // layer
  // layer_position
  // pose
  if (!geometry_msgs__msg__Pose__init(&msg->pose)) {
    jenga_interfaces__msg__JengaBlockState__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__msg__JengaBlockState__fini(jenga_interfaces__msg__JengaBlockState * msg)
{
  if (!msg) {
    return;
  }
  // block_id
  // colour
  rosidl_runtime_c__String__fini(&msg->colour);
  // layer
  // layer_position
  // pose
  geometry_msgs__msg__Pose__fini(&msg->pose);
}

bool
jenga_interfaces__msg__JengaBlockState__are_equal(const jenga_interfaces__msg__JengaBlockState * lhs, const jenga_interfaces__msg__JengaBlockState * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // block_id
  if (lhs->block_id != rhs->block_id) {
    return false;
  }
  // colour
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->colour), &(rhs->colour)))
  {
    return false;
  }
  // layer
  if (lhs->layer != rhs->layer) {
    return false;
  }
  // layer_position
  if (lhs->layer_position != rhs->layer_position) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__msg__JengaBlockState__copy(
  const jenga_interfaces__msg__JengaBlockState * input,
  jenga_interfaces__msg__JengaBlockState * output)
{
  if (!input || !output) {
    return false;
  }
  // block_id
  output->block_id = input->block_id;
  // colour
  if (!rosidl_runtime_c__String__copy(
      &(input->colour), &(output->colour)))
  {
    return false;
  }
  // layer
  output->layer = input->layer;
  // layer_position
  output->layer_position = input->layer_position;
  // pose
  if (!geometry_msgs__msg__Pose__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__msg__JengaBlockState *
jenga_interfaces__msg__JengaBlockState__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__msg__JengaBlockState * msg = (jenga_interfaces__msg__JengaBlockState *)allocator.allocate(sizeof(jenga_interfaces__msg__JengaBlockState), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__msg__JengaBlockState));
  bool success = jenga_interfaces__msg__JengaBlockState__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__msg__JengaBlockState__destroy(jenga_interfaces__msg__JengaBlockState * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__msg__JengaBlockState__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__msg__JengaBlockState__Sequence__init(jenga_interfaces__msg__JengaBlockState__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__msg__JengaBlockState * data = NULL;

  if (size) {
    data = (jenga_interfaces__msg__JengaBlockState *)allocator.zero_allocate(size, sizeof(jenga_interfaces__msg__JengaBlockState), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__msg__JengaBlockState__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__msg__JengaBlockState__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
jenga_interfaces__msg__JengaBlockState__Sequence__fini(jenga_interfaces__msg__JengaBlockState__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      jenga_interfaces__msg__JengaBlockState__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

jenga_interfaces__msg__JengaBlockState__Sequence *
jenga_interfaces__msg__JengaBlockState__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__msg__JengaBlockState__Sequence * array = (jenga_interfaces__msg__JengaBlockState__Sequence *)allocator.allocate(sizeof(jenga_interfaces__msg__JengaBlockState__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__msg__JengaBlockState__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__msg__JengaBlockState__Sequence__destroy(jenga_interfaces__msg__JengaBlockState__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__msg__JengaBlockState__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__msg__JengaBlockState__Sequence__are_equal(const jenga_interfaces__msg__JengaBlockState__Sequence * lhs, const jenga_interfaces__msg__JengaBlockState__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__msg__JengaBlockState__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__msg__JengaBlockState__Sequence__copy(
  const jenga_interfaces__msg__JengaBlockState__Sequence * input,
  jenga_interfaces__msg__JengaBlockState__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__msg__JengaBlockState);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__msg__JengaBlockState * data =
      (jenga_interfaces__msg__JengaBlockState *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__msg__JengaBlockState__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__msg__JengaBlockState__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__msg__JengaBlockState__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
