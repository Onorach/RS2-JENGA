// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from jenga_interfaces:srv/SetJengaBlocksLayout.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__FUNCTIONS_H_
#define JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "jenga_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "jenga_interfaces/srv/detail/set_jenga_blocks_layout__struct.h"

/// Initialize srv/SetJengaBlocksLayout message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request
 * )) before or use
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Request__init(jenga_interfaces__srv__SetJengaBlocksLayout_Request * msg);

/// Finalize srv/SetJengaBlocksLayout message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Request__fini(jenga_interfaces__srv__SetJengaBlocksLayout_Request * msg);

/// Create srv/SetJengaBlocksLayout message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
jenga_interfaces__srv__SetJengaBlocksLayout_Request *
jenga_interfaces__srv__SetJengaBlocksLayout_Request__create();

/// Destroy srv/SetJengaBlocksLayout message.
/**
 * It calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Request__destroy(jenga_interfaces__srv__SetJengaBlocksLayout_Request * msg);

/// Check for srv/SetJengaBlocksLayout message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Request__are_equal(const jenga_interfaces__srv__SetJengaBlocksLayout_Request * lhs, const jenga_interfaces__srv__SetJengaBlocksLayout_Request * rhs);

/// Copy a srv/SetJengaBlocksLayout message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Request__copy(
  const jenga_interfaces__srv__SetJengaBlocksLayout_Request * input,
  jenga_interfaces__srv__SetJengaBlocksLayout_Request * output);

/// Initialize array of srv/SetJengaBlocksLayout messages.
/**
 * It allocates the memory for the number of elements and calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__init(jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence * array, size_t size);

/// Finalize array of srv/SetJengaBlocksLayout messages.
/**
 * It calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__fini(jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence * array);

/// Create array of srv/SetJengaBlocksLayout messages.
/**
 * It allocates the memory for the array and calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence *
jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__create(size_t size);

/// Destroy array of srv/SetJengaBlocksLayout messages.
/**
 * It calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__destroy(jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence * array);

/// Check for srv/SetJengaBlocksLayout message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__are_equal(const jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence * lhs, const jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence * rhs);

/// Copy an array of srv/SetJengaBlocksLayout messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__copy(
  const jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence * input,
  jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence * output);

/// Initialize srv/SetJengaBlocksLayout message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response
 * )) before or use
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Response__init(jenga_interfaces__srv__SetJengaBlocksLayout_Response * msg);

/// Finalize srv/SetJengaBlocksLayout message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Response__fini(jenga_interfaces__srv__SetJengaBlocksLayout_Response * msg);

/// Create srv/SetJengaBlocksLayout message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
jenga_interfaces__srv__SetJengaBlocksLayout_Response *
jenga_interfaces__srv__SetJengaBlocksLayout_Response__create();

/// Destroy srv/SetJengaBlocksLayout message.
/**
 * It calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Response__destroy(jenga_interfaces__srv__SetJengaBlocksLayout_Response * msg);

/// Check for srv/SetJengaBlocksLayout message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Response__are_equal(const jenga_interfaces__srv__SetJengaBlocksLayout_Response * lhs, const jenga_interfaces__srv__SetJengaBlocksLayout_Response * rhs);

/// Copy a srv/SetJengaBlocksLayout message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Response__copy(
  const jenga_interfaces__srv__SetJengaBlocksLayout_Response * input,
  jenga_interfaces__srv__SetJengaBlocksLayout_Response * output);

/// Initialize array of srv/SetJengaBlocksLayout messages.
/**
 * It allocates the memory for the number of elements and calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__init(jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence * array, size_t size);

/// Finalize array of srv/SetJengaBlocksLayout messages.
/**
 * It calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__fini(jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence * array);

/// Create array of srv/SetJengaBlocksLayout messages.
/**
 * It allocates the memory for the array and calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence *
jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__create(size_t size);

/// Destroy array of srv/SetJengaBlocksLayout messages.
/**
 * It calls
 * jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
void
jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__destroy(jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence * array);

/// Check for srv/SetJengaBlocksLayout message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__are_equal(const jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence * lhs, const jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence * rhs);

/// Copy an array of srv/SetJengaBlocksLayout messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_jenga_interfaces
bool
jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__copy(
  const jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence * input,
  jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__FUNCTIONS_H_
