// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from jenga_interfaces:srv/ProtrudeJengaBlock.idl
// generated code does not contain a copyright notice
#include "jenga_interfaces/srv/detail/protrude_jenga_block__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `axis`
#include "rosidl_runtime_c/string_functions.h"

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Request__init(jenga_interfaces__srv__ProtrudeJengaBlock_Request * msg)
{
  if (!msg) {
    return false;
  }
  // block_index
  // distance_m
  // axis
  if (!rosidl_runtime_c__String__init(&msg->axis)) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Request__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__srv__ProtrudeJengaBlock_Request__fini(jenga_interfaces__srv__ProtrudeJengaBlock_Request * msg)
{
  if (!msg) {
    return;
  }
  // block_index
  // distance_m
  // axis
  rosidl_runtime_c__String__fini(&msg->axis);
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Request__are_equal(const jenga_interfaces__srv__ProtrudeJengaBlock_Request * lhs, const jenga_interfaces__srv__ProtrudeJengaBlock_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // block_index
  if (lhs->block_index != rhs->block_index) {
    return false;
  }
  // distance_m
  if (lhs->distance_m != rhs->distance_m) {
    return false;
  }
  // axis
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->axis), &(rhs->axis)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Request__copy(
  const jenga_interfaces__srv__ProtrudeJengaBlock_Request * input,
  jenga_interfaces__srv__ProtrudeJengaBlock_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // block_index
  output->block_index = input->block_index;
  // distance_m
  output->distance_m = input->distance_m;
  // axis
  if (!rosidl_runtime_c__String__copy(
      &(input->axis), &(output->axis)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__srv__ProtrudeJengaBlock_Request *
jenga_interfaces__srv__ProtrudeJengaBlock_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__srv__ProtrudeJengaBlock_Request * msg = (jenga_interfaces__srv__ProtrudeJengaBlock_Request *)allocator.allocate(sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Request));
  bool success = jenga_interfaces__srv__ProtrudeJengaBlock_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__srv__ProtrudeJengaBlock_Request__destroy(jenga_interfaces__srv__ProtrudeJengaBlock_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__init(jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__srv__ProtrudeJengaBlock_Request * data = NULL;

  if (size) {
    data = (jenga_interfaces__srv__ProtrudeJengaBlock_Request *)allocator.zero_allocate(size, sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__srv__ProtrudeJengaBlock_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__srv__ProtrudeJengaBlock_Request__fini(&data[i - 1]);
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
jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__fini(jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * array)
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
      jenga_interfaces__srv__ProtrudeJengaBlock_Request__fini(&array->data[i]);
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

jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence *
jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * array = (jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence *)allocator.allocate(sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__destroy(jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__are_equal(const jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * lhs, const jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__srv__ProtrudeJengaBlock_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__copy(
  const jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * input,
  jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__srv__ProtrudeJengaBlock_Request * data =
      (jenga_interfaces__srv__ProtrudeJengaBlock_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__srv__ProtrudeJengaBlock_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__srv__ProtrudeJengaBlock_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__srv__ProtrudeJengaBlock_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Response__init(jenga_interfaces__srv__ProtrudeJengaBlock_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Response__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__srv__ProtrudeJengaBlock_Response__fini(jenga_interfaces__srv__ProtrudeJengaBlock_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Response__are_equal(const jenga_interfaces__srv__ProtrudeJengaBlock_Response * lhs, const jenga_interfaces__srv__ProtrudeJengaBlock_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Response__copy(
  const jenga_interfaces__srv__ProtrudeJengaBlock_Response * input,
  jenga_interfaces__srv__ProtrudeJengaBlock_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__srv__ProtrudeJengaBlock_Response *
jenga_interfaces__srv__ProtrudeJengaBlock_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__srv__ProtrudeJengaBlock_Response * msg = (jenga_interfaces__srv__ProtrudeJengaBlock_Response *)allocator.allocate(sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Response));
  bool success = jenga_interfaces__srv__ProtrudeJengaBlock_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__srv__ProtrudeJengaBlock_Response__destroy(jenga_interfaces__srv__ProtrudeJengaBlock_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__init(jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__srv__ProtrudeJengaBlock_Response * data = NULL;

  if (size) {
    data = (jenga_interfaces__srv__ProtrudeJengaBlock_Response *)allocator.zero_allocate(size, sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__srv__ProtrudeJengaBlock_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__srv__ProtrudeJengaBlock_Response__fini(&data[i - 1]);
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
jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__fini(jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * array)
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
      jenga_interfaces__srv__ProtrudeJengaBlock_Response__fini(&array->data[i]);
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

jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence *
jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * array = (jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence *)allocator.allocate(sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__destroy(jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__are_equal(const jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * lhs, const jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__srv__ProtrudeJengaBlock_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__copy(
  const jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * input,
  jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__srv__ProtrudeJengaBlock_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__srv__ProtrudeJengaBlock_Response * data =
      (jenga_interfaces__srv__ProtrudeJengaBlock_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__srv__ProtrudeJengaBlock_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__srv__ProtrudeJengaBlock_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__srv__ProtrudeJengaBlock_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
