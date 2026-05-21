// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from jenga_interfaces:msg/JengaBlockStates.idl
// generated code does not contain a copyright notice
#include "jenga_interfaces/msg/detail/jenga_block_states__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `blocks`
#include "jenga_interfaces/msg/detail/jenga_block_state__functions.h"

bool
jenga_interfaces__msg__JengaBlockStates__init(jenga_interfaces__msg__JengaBlockStates * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    jenga_interfaces__msg__JengaBlockStates__fini(msg);
    return false;
  }
  // blocks
  if (!jenga_interfaces__msg__JengaBlockState__Sequence__init(&msg->blocks, 0)) {
    jenga_interfaces__msg__JengaBlockStates__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__msg__JengaBlockStates__fini(jenga_interfaces__msg__JengaBlockStates * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // blocks
  jenga_interfaces__msg__JengaBlockState__Sequence__fini(&msg->blocks);
}

bool
jenga_interfaces__msg__JengaBlockStates__are_equal(const jenga_interfaces__msg__JengaBlockStates * lhs, const jenga_interfaces__msg__JengaBlockStates * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // blocks
  if (!jenga_interfaces__msg__JengaBlockState__Sequence__are_equal(
      &(lhs->blocks), &(rhs->blocks)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__msg__JengaBlockStates__copy(
  const jenga_interfaces__msg__JengaBlockStates * input,
  jenga_interfaces__msg__JengaBlockStates * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // blocks
  if (!jenga_interfaces__msg__JengaBlockState__Sequence__copy(
      &(input->blocks), &(output->blocks)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__msg__JengaBlockStates *
jenga_interfaces__msg__JengaBlockStates__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__msg__JengaBlockStates * msg = (jenga_interfaces__msg__JengaBlockStates *)allocator.allocate(sizeof(jenga_interfaces__msg__JengaBlockStates), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__msg__JengaBlockStates));
  bool success = jenga_interfaces__msg__JengaBlockStates__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__msg__JengaBlockStates__destroy(jenga_interfaces__msg__JengaBlockStates * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__msg__JengaBlockStates__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__msg__JengaBlockStates__Sequence__init(jenga_interfaces__msg__JengaBlockStates__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__msg__JengaBlockStates * data = NULL;

  if (size) {
    data = (jenga_interfaces__msg__JengaBlockStates *)allocator.zero_allocate(size, sizeof(jenga_interfaces__msg__JengaBlockStates), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__msg__JengaBlockStates__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__msg__JengaBlockStates__fini(&data[i - 1]);
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
jenga_interfaces__msg__JengaBlockStates__Sequence__fini(jenga_interfaces__msg__JengaBlockStates__Sequence * array)
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
      jenga_interfaces__msg__JengaBlockStates__fini(&array->data[i]);
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

jenga_interfaces__msg__JengaBlockStates__Sequence *
jenga_interfaces__msg__JengaBlockStates__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__msg__JengaBlockStates__Sequence * array = (jenga_interfaces__msg__JengaBlockStates__Sequence *)allocator.allocate(sizeof(jenga_interfaces__msg__JengaBlockStates__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__msg__JengaBlockStates__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__msg__JengaBlockStates__Sequence__destroy(jenga_interfaces__msg__JengaBlockStates__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__msg__JengaBlockStates__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__msg__JengaBlockStates__Sequence__are_equal(const jenga_interfaces__msg__JengaBlockStates__Sequence * lhs, const jenga_interfaces__msg__JengaBlockStates__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__msg__JengaBlockStates__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__msg__JengaBlockStates__Sequence__copy(
  const jenga_interfaces__msg__JengaBlockStates__Sequence * input,
  jenga_interfaces__msg__JengaBlockStates__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__msg__JengaBlockStates);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__msg__JengaBlockStates * data =
      (jenga_interfaces__msg__JengaBlockStates *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__msg__JengaBlockStates__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__msg__JengaBlockStates__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__msg__JengaBlockStates__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
