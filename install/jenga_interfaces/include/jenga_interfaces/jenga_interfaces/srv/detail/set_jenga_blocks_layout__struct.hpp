// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from jenga_interfaces:srv/SetJengaBlocksLayout.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__STRUCT_HPP_
#define JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Request __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Request __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetJengaBlocksLayout_Request_
{
  using Type = SetJengaBlocksLayout_Request_<ContainerAllocator>;

  explicit SetJengaBlocksLayout_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->target_layout = "";
    }
  }

  explicit SetJengaBlocksLayout_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : target_layout(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->target_layout = "";
    }
  }

  // field types and members
  using _block_indices_type =
    std::vector<uint32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint32_t>>;
  _block_indices_type block_indices;
  using _target_layout_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _target_layout_type target_layout;

  // setters for named parameter idiom
  Type & set__block_indices(
    const std::vector<uint32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint32_t>> & _arg)
  {
    this->block_indices = _arg;
    return *this;
  }
  Type & set__target_layout(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->target_layout = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Request
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Request
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetJengaBlocksLayout_Request_ & other) const
  {
    if (this->block_indices != other.block_indices) {
      return false;
    }
    if (this->target_layout != other.target_layout) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetJengaBlocksLayout_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetJengaBlocksLayout_Request_

// alias to use template instance with default allocator
using SetJengaBlocksLayout_Request =
  jenga_interfaces::srv::SetJengaBlocksLayout_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace jenga_interfaces


#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Response __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Response __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetJengaBlocksLayout_Response_
{
  using Type = SetJengaBlocksLayout_Response_<ContainerAllocator>;

  explicit SetJengaBlocksLayout_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit SetJengaBlocksLayout_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Response
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__srv__SetJengaBlocksLayout_Response
    std::shared_ptr<jenga_interfaces::srv::SetJengaBlocksLayout_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetJengaBlocksLayout_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetJengaBlocksLayout_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetJengaBlocksLayout_Response_

// alias to use template instance with default allocator
using SetJengaBlocksLayout_Response =
  jenga_interfaces::srv::SetJengaBlocksLayout_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace jenga_interfaces

namespace jenga_interfaces
{

namespace srv
{

struct SetJengaBlocksLayout
{
  using Request = jenga_interfaces::srv::SetJengaBlocksLayout_Request;
  using Response = jenga_interfaces::srv::SetJengaBlocksLayout_Response;
};

}  // namespace srv

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__SRV__DETAIL__SET_JENGA_BLOCKS_LAYOUT__STRUCT_HPP_
