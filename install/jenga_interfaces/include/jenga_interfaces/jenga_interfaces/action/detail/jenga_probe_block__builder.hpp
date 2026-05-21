// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from jenga_interfaces:action/JengaProbeBlock.idl
// generated code does not contain a copyright notice

#ifndef JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__BUILDER_HPP_
#define JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "jenga_interfaces/action/detail/jenga_probe_block__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_Goal_block_pose
{
public:
  explicit Init_JengaProbeBlock_Goal_block_pose(::jenga_interfaces::action::JengaProbeBlock_Goal & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_Goal block_pose(::jenga_interfaces::action::JengaProbeBlock_Goal::_block_pose_type arg)
  {
    msg_.block_pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Goal msg_;
};

class Init_JengaProbeBlock_Goal_block_index
{
public:
  Init_JengaProbeBlock_Goal_block_index()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaProbeBlock_Goal_block_pose block_index(::jenga_interfaces::action::JengaProbeBlock_Goal::_block_index_type arg)
  {
    msg_.block_index = std::move(arg);
    return Init_JengaProbeBlock_Goal_block_pose(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_Goal>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_Goal_block_index();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_Result_max_force_n
{
public:
  explicit Init_JengaProbeBlock_Result_max_force_n(::jenga_interfaces::action::JengaProbeBlock_Result & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_Result max_force_n(::jenga_interfaces::action::JengaProbeBlock_Result::_max_force_n_type arg)
  {
    msg_.max_force_n = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Result msg_;
};

class Init_JengaProbeBlock_Result_displacement_m
{
public:
  explicit Init_JengaProbeBlock_Result_displacement_m(::jenga_interfaces::action::JengaProbeBlock_Result & msg)
  : msg_(msg)
  {}
  Init_JengaProbeBlock_Result_max_force_n displacement_m(::jenga_interfaces::action::JengaProbeBlock_Result::_displacement_m_type arg)
  {
    msg_.displacement_m = std::move(arg);
    return Init_JengaProbeBlock_Result_max_force_n(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Result msg_;
};

class Init_JengaProbeBlock_Result_probe_outcome
{
public:
  explicit Init_JengaProbeBlock_Result_probe_outcome(::jenga_interfaces::action::JengaProbeBlock_Result & msg)
  : msg_(msg)
  {}
  Init_JengaProbeBlock_Result_displacement_m probe_outcome(::jenga_interfaces::action::JengaProbeBlock_Result::_probe_outcome_type arg)
  {
    msg_.probe_outcome = std::move(arg);
    return Init_JengaProbeBlock_Result_displacement_m(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Result msg_;
};

class Init_JengaProbeBlock_Result_score
{
public:
  explicit Init_JengaProbeBlock_Result_score(::jenga_interfaces::action::JengaProbeBlock_Result & msg)
  : msg_(msg)
  {}
  Init_JengaProbeBlock_Result_probe_outcome score(::jenga_interfaces::action::JengaProbeBlock_Result::_score_type arg)
  {
    msg_.score = std::move(arg);
    return Init_JengaProbeBlock_Result_probe_outcome(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Result msg_;
};

class Init_JengaProbeBlock_Result_error_code
{
public:
  explicit Init_JengaProbeBlock_Result_error_code(::jenga_interfaces::action::JengaProbeBlock_Result & msg)
  : msg_(msg)
  {}
  Init_JengaProbeBlock_Result_score error_code(::jenga_interfaces::action::JengaProbeBlock_Result::_error_code_type arg)
  {
    msg_.error_code = std::move(arg);
    return Init_JengaProbeBlock_Result_score(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Result msg_;
};

class Init_JengaProbeBlock_Result_message
{
public:
  explicit Init_JengaProbeBlock_Result_message(::jenga_interfaces::action::JengaProbeBlock_Result & msg)
  : msg_(msg)
  {}
  Init_JengaProbeBlock_Result_error_code message(::jenga_interfaces::action::JengaProbeBlock_Result::_message_type arg)
  {
    msg_.message = std::move(arg);
    return Init_JengaProbeBlock_Result_error_code(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Result msg_;
};

class Init_JengaProbeBlock_Result_success
{
public:
  Init_JengaProbeBlock_Result_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaProbeBlock_Result_message success(::jenga_interfaces::action::JengaProbeBlock_Result::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_JengaProbeBlock_Result_message(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_Result>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_Result_success();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_Feedback_progress_pct
{
public:
  explicit Init_JengaProbeBlock_Feedback_progress_pct(::jenga_interfaces::action::JengaProbeBlock_Feedback & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_Feedback progress_pct(::jenga_interfaces::action::JengaProbeBlock_Feedback::_progress_pct_type arg)
  {
    msg_.progress_pct = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Feedback msg_;
};

class Init_JengaProbeBlock_Feedback_current_stage
{
public:
  Init_JengaProbeBlock_Feedback_current_stage()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaProbeBlock_Feedback_progress_pct current_stage(::jenga_interfaces::action::JengaProbeBlock_Feedback::_current_stage_type arg)
  {
    msg_.current_stage = std::move(arg);
    return Init_JengaProbeBlock_Feedback_progress_pct(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_Feedback>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_Feedback_current_stage();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_SendGoal_Request_goal
{
public:
  explicit Init_JengaProbeBlock_SendGoal_Request_goal(::jenga_interfaces::action::JengaProbeBlock_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_SendGoal_Request goal(::jenga_interfaces::action::JengaProbeBlock_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_SendGoal_Request msg_;
};

class Init_JengaProbeBlock_SendGoal_Request_goal_id
{
public:
  Init_JengaProbeBlock_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaProbeBlock_SendGoal_Request_goal goal_id(::jenga_interfaces::action::JengaProbeBlock_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_JengaProbeBlock_SendGoal_Request_goal(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_SendGoal_Request>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_SendGoal_Request_goal_id();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_SendGoal_Response_stamp
{
public:
  explicit Init_JengaProbeBlock_SendGoal_Response_stamp(::jenga_interfaces::action::JengaProbeBlock_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_SendGoal_Response stamp(::jenga_interfaces::action::JengaProbeBlock_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_SendGoal_Response msg_;
};

class Init_JengaProbeBlock_SendGoal_Response_accepted
{
public:
  Init_JengaProbeBlock_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaProbeBlock_SendGoal_Response_stamp accepted(::jenga_interfaces::action::JengaProbeBlock_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_JengaProbeBlock_SendGoal_Response_stamp(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_SendGoal_Response>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_SendGoal_Response_accepted();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_GetResult_Request_goal_id
{
public:
  Init_JengaProbeBlock_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_GetResult_Request goal_id(::jenga_interfaces::action::JengaProbeBlock_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_GetResult_Request>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_GetResult_Request_goal_id();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_GetResult_Response_result
{
public:
  explicit Init_JengaProbeBlock_GetResult_Response_result(::jenga_interfaces::action::JengaProbeBlock_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_GetResult_Response result(::jenga_interfaces::action::JengaProbeBlock_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_GetResult_Response msg_;
};

class Init_JengaProbeBlock_GetResult_Response_status
{
public:
  Init_JengaProbeBlock_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaProbeBlock_GetResult_Response_result status(::jenga_interfaces::action::JengaProbeBlock_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_JengaProbeBlock_GetResult_Response_result(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_GetResult_Response>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_GetResult_Response_status();
}

}  // namespace jenga_interfaces


namespace jenga_interfaces
{

namespace action
{

namespace builder
{

class Init_JengaProbeBlock_FeedbackMessage_feedback
{
public:
  explicit Init_JengaProbeBlock_FeedbackMessage_feedback(::jenga_interfaces::action::JengaProbeBlock_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::jenga_interfaces::action::JengaProbeBlock_FeedbackMessage feedback(::jenga_interfaces::action::JengaProbeBlock_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_FeedbackMessage msg_;
};

class Init_JengaProbeBlock_FeedbackMessage_goal_id
{
public:
  Init_JengaProbeBlock_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_JengaProbeBlock_FeedbackMessage_feedback goal_id(::jenga_interfaces::action::JengaProbeBlock_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_JengaProbeBlock_FeedbackMessage_feedback(msg_);
  }

private:
  ::jenga_interfaces::action::JengaProbeBlock_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::jenga_interfaces::action::JengaProbeBlock_FeedbackMessage>()
{
  return jenga_interfaces::action::builder::Init_JengaProbeBlock_FeedbackMessage_goal_id();
}

}  // namespace jenga_interfaces

#endif  // JENGA_INTERFACES__ACTION__DETAIL__JENGA_PROBE_BLOCK__BUILDER_HPP_
