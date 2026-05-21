// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from jenga_interfaces:action/JengaExtractMiddleBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_MIDDLE_BLOCK__BUILDER_HPP_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_MIDDLE_BLOCK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "jenga_interfaces/action/detail/jenga_extract_middle_block__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_Goal_extract_axis
{
public:
  explicit Init_JengaExtractMiddleBlock_Goal_extract_axis(::jenga_interfaces::action::JengaExtractMiddleBlock_Goal & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Goal extract_axis(::jenga_interfaces::action::JengaExtractMiddleBlock_Goal::_extract_axis_type arg)
  {
    msg_.extract_axis = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Goal msg_;
};

class Init_JengaExtractMiddleBlock_Goal_place_pose
{
public:
  explicit Init_JengaExtractMiddleBlock_Goal_place_pose(::jenga_interfaces::action::JengaExtractMiddleBlock_Goal & msg)
  : msg_(msg)
  {}
  Init_JengaExtractMiddleBlock_Goal_extract_axis place_pose(::jenga_interfaces::action::JengaExtractMiddleBlock_Goal::_place_pose_type arg)
  {
    msg_.place_pose = std::move(arg);
    return Init_JengaExtractMiddleBlock_Goal_extract_axis(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Goal msg_;
};

class Init_JengaExtractMiddleBlock_Goal_block_pose
{
public:
  explicit Init_JengaExtractMiddleBlock_Goal_block_pose(::jenga_interfaces::action::JengaExtractMiddleBlock_Goal & msg)
  : msg_(msg)
  {}
  Init_JengaExtractMiddleBlock_Goal_place_pose block_pose(::jenga_interfaces::action::JengaExtractMiddleBlock_Goal::_block_pose_type arg)
  {
    msg_.block_pose = std::move(arg);
    return Init_JengaExtractMiddleBlock_Goal_place_pose(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Goal msg_;
};

class Init_JengaExtractMiddleBlock_Goal_block_index
{
public:
  Init_JengaExtractMiddleBlock_Goal_block_index()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaExtractMiddleBlock_Goal_block_pose block_index(::jenga_interfaces::action::JengaExtractMiddleBlock_Goal::_block_index_type arg)
  {
    msg_.block_index = std::move(arg);
    return Init_JengaExtractMiddleBlock_Goal_block_pose(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_Goal>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_Goal_block_index();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_Result_error_code
{
public:
  explicit Init_JengaExtractMiddleBlock_Result_error_code(::jenga_interfaces::action::JengaExtractMiddleBlock_Result & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Result error_code(::jenga_interfaces::action::JengaExtractMiddleBlock_Result::_error_code_type arg)
  {
    msg_.error_code = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Result msg_;
};

class Init_JengaExtractMiddleBlock_Result_message
{
public:
  explicit Init_JengaExtractMiddleBlock_Result_message(::jenga_interfaces::action::JengaExtractMiddleBlock_Result & msg)
  : msg_(msg)
  {}
  Init_JengaExtractMiddleBlock_Result_error_code message(::jenga_interfaces::action::JengaExtractMiddleBlock_Result::_message_type arg)
  {
    msg_.message = std::move(arg);
    return Init_JengaExtractMiddleBlock_Result_error_code(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Result msg_;
};

class Init_JengaExtractMiddleBlock_Result_success
{
public:
  Init_JengaExtractMiddleBlock_Result_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaExtractMiddleBlock_Result_message success(::jenga_interfaces::action::JengaExtractMiddleBlock_Result::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_JengaExtractMiddleBlock_Result_message(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_Result>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_Result_success();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_Feedback_progress_pct
{
public:
  explicit Init_JengaExtractMiddleBlock_Feedback_progress_pct(::jenga_interfaces::action::JengaExtractMiddleBlock_Feedback & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Feedback progress_pct(::jenga_interfaces::action::JengaExtractMiddleBlock_Feedback::_progress_pct_type arg)
  {
    msg_.progress_pct = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Feedback msg_;
};

class Init_JengaExtractMiddleBlock_Feedback_current_stage
{
public:
  Init_JengaExtractMiddleBlock_Feedback_current_stage()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaExtractMiddleBlock_Feedback_progress_pct current_stage(::jenga_interfaces::action::JengaExtractMiddleBlock_Feedback::_current_stage_type arg)
  {
    msg_.current_stage = std::move(arg);
    return Init_JengaExtractMiddleBlock_Feedback_progress_pct(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_Feedback>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_Feedback_current_stage();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_SendGoal_Request_goal
{
public:
  explicit Init_JengaExtractMiddleBlock_SendGoal_Request_goal(::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request goal(::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request msg_;
};

class Init_JengaExtractMiddleBlock_SendGoal_Request_goal_id
{
public:
  Init_JengaExtractMiddleBlock_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaExtractMiddleBlock_SendGoal_Request_goal goal_id(::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_JengaExtractMiddleBlock_SendGoal_Request_goal(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Request>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_SendGoal_Request_goal_id();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_SendGoal_Response_stamp
{
public:
  explicit Init_JengaExtractMiddleBlock_SendGoal_Response_stamp(::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response stamp(::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response msg_;
};

class Init_JengaExtractMiddleBlock_SendGoal_Response_accepted
{
public:
  Init_JengaExtractMiddleBlock_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaExtractMiddleBlock_SendGoal_Response_stamp accepted(::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_JengaExtractMiddleBlock_SendGoal_Response_stamp(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_SendGoal_Response>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_SendGoal_Response_accepted();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_GetResult_Request_goal_id
{
public:
  Init_JengaExtractMiddleBlock_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request goal_id(::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Request>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_GetResult_Request_goal_id();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_GetResult_Response_result
{
public:
  explicit Init_JengaExtractMiddleBlock_GetResult_Response_result(::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response result(::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response msg_;
};

class Init_JengaExtractMiddleBlock_GetResult_Response_status
{
public:
  Init_JengaExtractMiddleBlock_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaExtractMiddleBlock_GetResult_Response_result status(::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_JengaExtractMiddleBlock_GetResult_Response_result(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_GetResult_Response>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_GetResult_Response_status();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaExtractMiddleBlock_FeedbackMessage_feedback
{
public:
  explicit Init_JengaExtractMiddleBlock_FeedbackMessage_feedback(::jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage feedback(::jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage msg_;
};

class Init_JengaExtractMiddleBlock_FeedbackMessage_goal_id
{
public:
  Init_JengaExtractMiddleBlock_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaExtractMiddleBlock_FeedbackMessage_feedback goal_id(::jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_JengaExtractMiddleBlock_FeedbackMessage_feedback(msg_);
  }

private:
  ::jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaExtractMiddleBlock_FeedbackMessage>()
{
  return jenga_interfaces::action::builder::Init_JengaExtractMiddleBlock_FeedbackMessage_goal_id();
}

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_EXTRACT_MIDDLE_BLOCK__BUILDER_HPP_
