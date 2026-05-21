// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from jenga_interfaces:action/JengaPickPlace.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_PICK_PLACE__STRUCT_HPP_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_PICK_PLACE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'pick_pose'
// Member 'place_pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_Goal __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_Goal __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_Goal_
{
  using Type = JengaPickPlace_Goal_<ContainerAllocator>;

  explicit JengaPickPlace_Goal_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pick_pose(_init),
    place_pose(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->block_index = 0ul;
    }
  }

  explicit JengaPickPlace_Goal_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pick_pose(_alloc, _init),
    place_pose(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->block_index = 0ul;
    }
  }

  // field types and members
  using _block_index_type =
    uint32_t;
  _block_index_type block_index;
  using _pick_pose_type =
    geometry_msgs::msg::PoseStamped_<ContainerAllocator>;
  _pick_pose_type pick_pose;
  using _place_pose_type =
    geometry_msgs::msg::PoseStamped_<ContainerAllocator>;
  _place_pose_type place_pose;

  // setters for named parameter idiom
  Type & set__block_index(
    const uint32_t & _arg)
  {
    this->block_index = _arg;
    return *this;
  }
  Type & set__pick_pose(
    const geometry_msgs::msg::PoseStamped_<ContainerAllocator> & _arg)
  {
    this->pick_pose = _arg;
    return *this;
  }
  Type & set__place_pose(
    const geometry_msgs::msg::PoseStamped_<ContainerAllocator> & _arg)
  {
    this->place_pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_Goal
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_Goal
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_Goal_ & other) const
  {
    if (this->block_index != other.block_index) {
      return false;
    }
    if (this->pick_pose != other.pick_pose) {
      return false;
    }
    if (this->place_pose != other.place_pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_Goal_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_Goal_

// alias to use template instance with default allocator
using JengaPickPlace_Goal =
  jenga_interfaces::action::JengaPickPlace_Goal_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces


#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_Result __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_Result __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_Result_
{
  using Type = JengaPickPlace_Result_<ContainerAllocator>;

  explicit JengaPickPlace_Result_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
      this->error_code = 0;
    }
  }

  explicit JengaPickPlace_Result_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
      this->error_code = 0;
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;
  using _error_code_type =
    uint8_t;
  _error_code_type error_code;

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
  Type & set__error_code(
    const uint8_t & _arg)
  {
    this->error_code = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_Result
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_Result
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_Result_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    if (this->error_code != other.error_code) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_Result_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_Result_

// alias to use template instance with default allocator
using JengaPickPlace_Result =
  jenga_interfaces::action::JengaPickPlace_Result_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces


#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_Feedback __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_Feedback __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_Feedback_
{
  using Type = JengaPickPlace_Feedback_<ContainerAllocator>;

  explicit JengaPickPlace_Feedback_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->current_stage = "";
      this->progress_pct = 0.0f;
    }
  }

  explicit JengaPickPlace_Feedback_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : current_stage(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->current_stage = "";
      this->progress_pct = 0.0f;
    }
  }

  // field types and members
  using _current_stage_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _current_stage_type current_stage;
  using _progress_pct_type =
    float;
  _progress_pct_type progress_pct;

  // setters for named parameter idiom
  Type & set__current_stage(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->current_stage = _arg;
    return *this;
  }
  Type & set__progress_pct(
    const float & _arg)
  {
    this->progress_pct = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_Feedback
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_Feedback
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_Feedback_ & other) const
  {
    if (this->current_stage != other.current_stage) {
      return false;
    }
    if (this->progress_pct != other.progress_pct) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_Feedback_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_Feedback_

// alias to use template instance with default allocator
using JengaPickPlace_Feedback =
  jenga_interfaces::action::JengaPickPlace_Feedback_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces


// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'goal'
#include "jenga_interfaces/action/detail/jenga_pick_place__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Request __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Request __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_SendGoal_Request_
{
  using Type = JengaPickPlace_SendGoal_Request_<ContainerAllocator>;

  explicit JengaPickPlace_SendGoal_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init),
    goal(_init)
  {
    (void)_init;
  }

  explicit JengaPickPlace_SendGoal_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init),
    goal(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;
  using _goal_type =
    jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator>;
  _goal_type goal;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }
  Type & set__goal(
    const jenga_interfaces::action::JengaPickPlace_Goal_<ContainerAllocator> & _arg)
  {
    this->goal = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Request
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Request
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_SendGoal_Request_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    if (this->goal != other.goal) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_SendGoal_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_SendGoal_Request_

// alias to use template instance with default allocator
using JengaPickPlace_SendGoal_Request =
  jenga_interfaces::action::JengaPickPlace_SendGoal_Request_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces


// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Response __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Response __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_SendGoal_Response_
{
  using Type = JengaPickPlace_SendGoal_Response_<ContainerAllocator>;

  explicit JengaPickPlace_SendGoal_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  explicit JengaPickPlace_SendGoal_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  // field types and members
  using _accepted_type =
    bool;
  _accepted_type accepted;
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;

  // setters for named parameter idiom
  Type & set__accepted(
    const bool & _arg)
  {
    this->accepted = _arg;
    return *this;
  }
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Response
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_SendGoal_Response
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_SendGoal_Response_ & other) const
  {
    if (this->accepted != other.accepted) {
      return false;
    }
    if (this->stamp != other.stamp) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_SendGoal_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_SendGoal_Response_

// alias to use template instance with default allocator
using JengaPickPlace_SendGoal_Response =
  jenga_interfaces::action::JengaPickPlace_SendGoal_Response_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces

namespace jenga_interfaces
{

namespace action
{

struct JengaPickPlace_SendGoal
{
  using Request = jenga_interfaces::action::JengaPickPlace_SendGoal_Request;
  using Response = jenga_interfaces::action::JengaPickPlace_SendGoal_Response;
};

}  // namespace action

}  // namespace jenga_interfaces


// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Request __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Request __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_GetResult_Request_
{
  using Type = JengaPickPlace_GetResult_Request_<ContainerAllocator>;

  explicit JengaPickPlace_GetResult_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init)
  {
    (void)_init;
  }

  explicit JengaPickPlace_GetResult_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Request
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Request
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_GetResult_Request_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_GetResult_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_GetResult_Request_

// alias to use template instance with default allocator
using JengaPickPlace_GetResult_Request =
  jenga_interfaces::action::JengaPickPlace_GetResult_Request_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces


// Include directives for member types
// Member 'result'
// already included above
// #include "jenga_interfaces/action/detail/jenga_pick_place__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Response __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Response __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_GetResult_Response_
{
  using Type = JengaPickPlace_GetResult_Response_<ContainerAllocator>;

  explicit JengaPickPlace_GetResult_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  explicit JengaPickPlace_GetResult_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  // field types and members
  using _status_type =
    int8_t;
  _status_type status;
  using _result_type =
    jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator>;
  _result_type result;

  // setters for named parameter idiom
  Type & set__status(
    const int8_t & _arg)
  {
    this->status = _arg;
    return *this;
  }
  Type & set__result(
    const jenga_interfaces::action::JengaPickPlace_Result_<ContainerAllocator> & _arg)
  {
    this->result = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Response
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_GetResult_Response
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_GetResult_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_GetResult_Response_ & other) const
  {
    if (this->status != other.status) {
      return false;
    }
    if (this->result != other.result) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_GetResult_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_GetResult_Response_

// alias to use template instance with default allocator
using JengaPickPlace_GetResult_Response =
  jenga_interfaces::action::JengaPickPlace_GetResult_Response_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces

namespace jenga_interfaces
{

namespace action
{

struct JengaPickPlace_GetResult
{
  using Request = jenga_interfaces::action::JengaPickPlace_GetResult_Request;
  using Response = jenga_interfaces::action::JengaPickPlace_GetResult_Response;
};

}  // namespace action

}  // namespace jenga_interfaces


// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'feedback'
// already included above
// #include "jenga_interfaces/action/detail/jenga_pick_place__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_FeedbackMessage __attribute__((deprecated))
#else
# define DEPRECATED__jenga_interfaces__action__JengaPickPlace_FeedbackMessage __declspec(deprecated)
#endif

namespace jenga_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct JengaPickPlace_FeedbackMessage_
{
  using Type = JengaPickPlace_FeedbackMessage_<ContainerAllocator>;

  explicit JengaPickPlace_FeedbackMessage_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init),
    feedback(_init)
  {
    (void)_init;
  }

  explicit JengaPickPlace_FeedbackMessage_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init),
    feedback(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;
  using _feedback_type =
    jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator>;
  _feedback_type feedback;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }
  Type & set__feedback(
    const jenga_interfaces::action::JengaPickPlace_Feedback_<ContainerAllocator> & _arg)
  {
    this->feedback = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator> *;
  using ConstRawPtr =
    const jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_FeedbackMessage
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__jenga_interfaces__action__JengaPickPlace_FeedbackMessage
    std::shared_ptr<jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const JengaPickPlace_FeedbackMessage_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    if (this->feedback != other.feedback) {
      return false;
    }
    return true;
  }
  bool operator!=(const JengaPickPlace_FeedbackMessage_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct JengaPickPlace_FeedbackMessage_

// alias to use template instance with default allocator
using JengaPickPlace_FeedbackMessage =
  jenga_interfaces::action::JengaPickPlace_FeedbackMessage_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace jenga_interfaces

#include "action_msgs/srv/cancel_goal.hpp"
#include "action_msgs/msg/goal_info.hpp"
#include "action_msgs/msg/goal_status_array.hpp"

namespace jenga_interfaces
{

namespace action
{

struct JengaPickPlace
{
  /// The goal message defined in the action definition.
  using Goal = jenga_interfaces::action::JengaPickPlace_Goal;
  /// The result message defined in the action definition.
  using Result = jenga_interfaces::action::JengaPickPlace_Result;
  /// The feedback message defined in the action definition.
  using Feedback = jenga_interfaces::action::JengaPickPlace_Feedback;

  struct Impl
  {
    /// The send_goal service using a wrapped version of the goal message as a request.
    using SendGoalService = jenga_interfaces::action::JengaPickPlace_SendGoal;
    /// The get_result service using a wrapped version of the result message as a response.
    using GetResultService = jenga_interfaces::action::JengaPickPlace_GetResult;
    /// The feedback message with generic fields which wraps the feedback message.
    using FeedbackMessage = jenga_interfaces::action::JengaPickPlace_FeedbackMessage;

    /// The generic service to cancel a goal.
    using CancelGoalService = action_msgs::srv::CancelGoal;
    /// The generic message for the status of a goal.
    using GoalStatusMessage = action_msgs::msg::GoalStatusArray;
  };
};

typedef struct JengaPickPlace JengaPickPlace;

}  // namespace action

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_PICK_PLACE__STRUCT_HPP_
