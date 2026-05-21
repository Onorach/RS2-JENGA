// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from jenga_interfaces:msg/JengaBlockState.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__STRUCT_HPP_
#define JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__msg__JengaBlockState __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__msg__JengaBlockState __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct JengaBlockState_
{
  using Type = JengaBlockState_<ContainerAllocator>;

  explicit JengaBlockState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->block_id = 0ul;
      this->colour = "";
      this->layer = 0ul;
      this->layer_position = 0;
    }
  }

  explicit JengaBlockState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : colour(_alloc),
    pose(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->block_id = 0ul;
      this->colour = "";
      this->layer = 0ul;
      this->layer_position = 0;
    }
  }

  // field types and members
  using _block_id_type =
    uint32_t;
  _block_id_type block_id;
  using _colour_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _colour_type colour;
  using _layer_type =
    uint32_t;
  _layer_type layer;
  using _layer_position_type =
    uint8_t;
  _layer_position_type layer_position;
  using _pose_type =
    geometry_msgs::msg::Pose_<ContainerAllocator>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__block_id(
    const uint32_t & _arg)
  {
    this->block_id = _arg;
    return *this;
  }
  Type & set__colour(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->colour = _arg;
    return *this;
  }
  Type & set__layer(
    const uint32_t & _arg)
  {
    this->layer = _arg;
    return *this;
  }
  Type & set__layer_position(
    const uint8_t & _arg)
  {
    this->layer_position = _arg;
    return *this;
  }
  Type & set__pose(
    const geometry_msgs::msg::Pose_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::msg::JengaBlockState_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::msg::JengaBlockState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::msg::JengaBlockState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::msg::JengaBlockState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__msg__JengaBlockState
    std::shared_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__msg__JengaBlockState
    std::shared_ptr<jenga_interfaces::msg::JengaBlockState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaBlockState_ & other) const
  {
    if (this->block_id != other.block_id) {
      return false;
    }
    if (this->colour != other.colour) {
      return false;
    }
    if (this->layer != other.layer) {
      return false;
    }
    if (this->layer_position != other.layer_position) {
      return false;
    }
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaBlockState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaBlockState_

// alias to use template instance with default allocator
using JengaBlockState =
  jenga_interfaces::msg::JengaBlockState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__MSG__DETAIL__JENGA_BLOCK_STATE__STRUCT_HPP_
