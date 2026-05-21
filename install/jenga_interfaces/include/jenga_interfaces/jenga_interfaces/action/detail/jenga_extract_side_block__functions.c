// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from jenga_interfaces:action/JengaExtractSideBlock.idl
// generated code does not contain a copyright notice
#include "jenga_interfaces/action/detail/jenga_extract_side_block__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `block_pose`
// Member `place_pose`
#include "geometry_msgs/msg/detail/pose_stamped__functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_Goal__init(jenga_interfaces__action__JengaExtractSideBlock_Goal * msg)
{
  if (!msg) {
    return false;
  }
  // block_index
  // block_pose
  if (!geometry_msgs__msg__PoseStamped__init(&msg->block_pose)) {
    jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(msg);
    return false;
  }
  // place_pose
  if (!geometry_msgs__msg__PoseStamped__init(&msg->place_pose)) {
    jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(jenga_interfaces__action__JengaExtractSideBlock_Goal * msg)
{
  if (!msg) {
    return;
  }
  // block_index
  // block_pose
  geometry_msgs__msg__PoseStamped__fini(&msg->block_pose);
  // place_pose
  geometry_msgs__msg__PoseStamped__fini(&msg->place_pose);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Goal__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_Goal * lhs, const jenga_interfaces__action__JengaExtractSideBlock_Goal * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // block_index
  if (lhs->block_index != rhs->block_index) {
    return false;
  }
  // block_pose
  if (!geometry_msgs__msg__PoseStamped__are_equal(
      &(lhs->block_pose), &(rhs->block_pose)))
  {
    return false;
  }
  // place_pose
  if (!geometry_msgs__msg__PoseStamped__are_equal(
      &(lhs->place_pose), &(rhs->place_pose)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Goal__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_Goal * input,
  jenga_interfaces__action__JengaExtractSideBlock_Goal * output)
{
  if (!input || !output) {
    return false;
  }
  // block_index
  output->block_index = input->block_index;
  // block_pose
  if (!geometry_msgs__msg__PoseStamped__copy(
      &(input->block_pose), &(output->block_pose)))
  {
    return false;
  }
  // place_pose
  if (!geometry_msgs__msg__PoseStamped__copy(
      &(input->place_pose), &(output->place_pose)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_Goal *
jenga_interfaces__action__JengaExtractSideBlock_Goal__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Goal * msg = (jenga_interfaces__action__JengaExtractSideBlock_Goal *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_Goal), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_Goal));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_Goal__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Goal__destroy(jenga_interfaces__action__JengaExtractSideBlock_Goal * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Goal * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_Goal *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_Goal), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_Goal__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_Goal__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_Goal);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_Goal * data =
      (jenga_interfaces__action__JengaExtractSideBlock_Goal *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_Goal__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_Goal__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_Result__init(jenga_interfaces__action__JengaExtractSideBlock_Result * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    jenga_interfaces__action__JengaExtractSideBlock_Result__fini(msg);
    return false;
  }
  // error_code
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Result__fini(jenga_interfaces__action__JengaExtractSideBlock_Result * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
  // error_code
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Result__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_Result * lhs, const jenga_interfaces__action__JengaExtractSideBlock_Result * rhs)
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
  // error_code
  if (lhs->error_code != rhs->error_code) {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Result__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_Result * input,
  jenga_interfaces__action__JengaExtractSideBlock_Result * output)
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
  // error_code
  output->error_code = input->error_code;
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_Result *
jenga_interfaces__action__JengaExtractSideBlock_Result__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Result * msg = (jenga_interfaces__action__JengaExtractSideBlock_Result *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_Result), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_Result));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_Result__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Result__destroy(jenga_interfaces__action__JengaExtractSideBlock_Result * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_Result__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Result * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_Result *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_Result), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_Result__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_Result__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_Result__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_Result__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_Result);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_Result * data =
      (jenga_interfaces__action__JengaExtractSideBlock_Result *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_Result__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_Result__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_Result__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `current_stage`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_Feedback__init(jenga_interfaces__action__JengaExtractSideBlock_Feedback * msg)
{
  if (!msg) {
    return false;
  }
  // current_stage
  if (!rosidl_runtime_c__String__init(&msg->current_stage)) {
    jenga_interfaces__action__JengaExtractSideBlock_Feedback__fini(msg);
    return false;
  }
  // progress_pct
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Feedback__fini(jenga_interfaces__action__JengaExtractSideBlock_Feedback * msg)
{
  if (!msg) {
    return;
  }
  // current_stage
  rosidl_runtime_c__String__fini(&msg->current_stage);
  // progress_pct
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Feedback__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_Feedback * lhs, const jenga_interfaces__action__JengaExtractSideBlock_Feedback * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // current_stage
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->current_stage), &(rhs->current_stage)))
  {
    return false;
  }
  // progress_pct
  if (lhs->progress_pct != rhs->progress_pct) {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Feedback__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_Feedback * input,
  jenga_interfaces__action__JengaExtractSideBlock_Feedback * output)
{
  if (!input || !output) {
    return false;
  }
  // current_stage
  if (!rosidl_runtime_c__String__copy(
      &(input->current_stage), &(output->current_stage)))
  {
    return false;
  }
  // progress_pct
  output->progress_pct = input->progress_pct;
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_Feedback *
jenga_interfaces__action__JengaExtractSideBlock_Feedback__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Feedback * msg = (jenga_interfaces__action__JengaExtractSideBlock_Feedback *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_Feedback), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_Feedback));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_Feedback__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Feedback__destroy(jenga_interfaces__action__JengaExtractSideBlock_Feedback * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_Feedback__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Feedback * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_Feedback *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_Feedback), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_Feedback__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_Feedback__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_Feedback__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_Feedback__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_Feedback);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_Feedback * data =
      (jenga_interfaces__action__JengaExtractSideBlock_Feedback *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_Feedback__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_Feedback__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_Feedback__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `goal`
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_side_block__functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__init(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__fini(msg);
    return false;
  }
  // goal
  if (!jenga_interfaces__action__JengaExtractSideBlock_Goal__init(&msg->goal)) {
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__fini(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // goal
  jenga_interfaces__action__JengaExtractSideBlock_Goal__fini(&msg->goal);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * lhs, const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // goal
  if (!jenga_interfaces__action__JengaExtractSideBlock_Goal__are_equal(
      &(lhs->goal), &(rhs->goal)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * input,
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // goal
  if (!jenga_interfaces__action__JengaExtractSideBlock_Goal__copy(
      &(input->goal), &(output->goal)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request *
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * msg = (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__destroy(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request * data =
      (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__init(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * msg)
{
  if (!msg) {
    return false;
  }
  // accepted
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__fini(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * msg)
{
  if (!msg) {
    return;
  }
  // accepted
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * lhs, const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * input,
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // accepted
  output->accepted = input->accepted;
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response *
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * msg = (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__destroy(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response * data =
      (jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__init(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__fini(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * lhs, const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * input,
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request *
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * msg = (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__destroy(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request * data =
      (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `result`
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_side_block__functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__init(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * msg)
{
  if (!msg) {
    return false;
  }
  // status
  // result
  if (!jenga_interfaces__action__JengaExtractSideBlock_Result__init(&msg->result)) {
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__fini(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * msg)
{
  if (!msg) {
    return;
  }
  // status
  // result
  jenga_interfaces__action__JengaExtractSideBlock_Result__fini(&msg->result);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * lhs, const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // status
  if (lhs->status != rhs->status) {
    return false;
  }
  // result
  if (!jenga_interfaces__action__JengaExtractSideBlock_Result__are_equal(
      &(lhs->result), &(rhs->result)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * input,
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // status
  output->status = input->status;
  // result
  if (!jenga_interfaces__action__JengaExtractSideBlock_Result__copy(
      &(input->result), &(output->result)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response *
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * msg = (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__destroy(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response * data =
      (jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `feedback`
// already included above
// #include "jenga_interfaces/action/detail/jenga_extract_side_block__functions.h"

bool
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__init(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__fini(msg);
    return false;
  }
  // feedback
  if (!jenga_interfaces__action__JengaExtractSideBlock_Feedback__init(&msg->feedback)) {
    jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__fini(msg);
    return false;
  }
  return true;
}

void
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__fini(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // feedback
  jenga_interfaces__action__JengaExtractSideBlock_Feedback__fini(&msg->feedback);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * lhs, const jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // feedback
  if (!jenga_interfaces__action__JengaExtractSideBlock_Feedback__are_equal(
      &(lhs->feedback), &(rhs->feedback)))
  {
    return false;
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * input,
  jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // feedback
  if (!jenga_interfaces__action__JengaExtractSideBlock_Feedback__copy(
      &(input->feedback), &(output->feedback)))
  {
    return false;
  }
  return true;
}

jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage *
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * msg = (jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage));
  bool success = jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__destroy(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__init(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * data = NULL;

  if (size) {
    data = (jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage *)allocator.zero_allocate(size, sizeof(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__fini(&data[i - 1]);
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
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__fini(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * array)
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
      jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__fini(&array->data[i]);
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

jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence *
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * array = (jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence *)allocator.allocate(sizeof(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__destroy(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__are_equal(const jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * lhs, const jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__copy(
  const jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * input,
  jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage * data =
      (jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
