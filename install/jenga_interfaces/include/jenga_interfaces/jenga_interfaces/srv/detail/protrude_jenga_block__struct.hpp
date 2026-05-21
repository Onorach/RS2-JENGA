// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from jenga_interfaces:srv/ProtrudeJengaBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__STRUCT_HPP_
#define JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Request __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Request __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ProtrudeJengaBlock_Request_
{
  using Type = ProtrudeJengaBlock_Request_<ContainerAllocator>;

  explicit ProtrudeJengaBlock_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->block_index = 0ul;
      this->distance_m = 0.0;
      this->axis = "";
    }
  }

  explicit ProtrudeJengaBlock_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : axis(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->block_index = 0ul;
      this->distance_m = 0.0;
      this->axis = "";
    }
  }

  // field types and members
  using _block_index_type =
    uint32_t;
  _block_index_type block_index;
  using _distance_m_type =
    double;
  _distance_m_type distance_m;
  using _axis_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _axis_type axis;

  // setters for named parameter idiom
  Type & set__block_index(
    const uint32_t & _arg)
  {
    this->block_index = _arg;
    return *this;
  }
  Type & set__distance_m(
    const double & _arg)
  {
    this->distance_m = _arg;
    return *this;
  }
  Type & set__axis(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->axis = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Request
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Request
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ProtrudeJengaBlock_Request_ & other) const
  {
    if (this->block_index != other.block_index) {
      return false;
    }
    if (this->distance_m != other.distance_m) {
      return false;
    }
    if (this->axis != other.axis) {
      return false;
    }
    return true;
  }
  bool operator!=(const ProtrudeJengaBlock_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ProtrudeJengaBlock_Request_

// alias to use template instance with default allocator
using ProtrudeJengaBlock_Request =
  jenga_interfaces::srv::ProtrudeJengaBlock_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace jenga_interfaces


#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Response __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Response __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ProtrudeJengaBlock_Response_
{
  using Type = ProtrudeJengaBlock_Response_<ContainerAllocator>;

  explicit ProtrudeJengaBlock_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit ProtrudeJengaBlock_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Response
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__srv__ProtrudeJengaBlock_Response
    std::shared_ptr<jenga_interfaces::srv::ProtrudeJengaBlock_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ProtrudeJengaBlock_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const ProtrudeJengaBlock_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ProtrudeJengaBlock_Response_

// alias to use template instance with default allocator
using ProtrudeJengaBlock_Response =
  jenga_interfaces::srv::ProtrudeJengaBlock_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace jenga_interfaces

namespace jenga_interfaces
{

namespace srv
{

struct ProtrudeJengaBlock
{
  using Request = jenga_interfaces::srv::ProtrudeJengaBlock_Request;
  using Response = jenga_interfaces::srv::ProtrudeJengaBlock_Response;
};

}  // namespace srv

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__SRV__DETAIL__PROTRUDE_JENGA_BLOCK__STRUCT_HPP_
