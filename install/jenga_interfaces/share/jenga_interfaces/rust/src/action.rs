
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to jenga_interfaces__action__JengaPickPlace_Goal

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pick_pose: geometry_msgs::msg::PoseStamped,


    // This member is not documented.
    #[allow(missing_docs)]
    pub place_pose: geometry_msgs::msg::PoseStamped,

}



impl Default for JengaPickPlace_Goal {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_Goal::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_Goal {
  type RmwMsg = super::action::rmw::JengaPickPlace_Goal;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_index: msg.block_index,
        pick_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(msg.pick_pose)).into_owned(),
        place_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(msg.place_pose)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      block_index: msg.block_index,
        pick_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.pick_pose)).into_owned(),
        place_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.place_pose)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      block_index: msg.block_index,
      pick_pose: geometry_msgs::msg::PoseStamped::from_rmw_message(msg.pick_pose),
      place_pose: geometry_msgs::msg::PoseStamped::from_rmw_message(msg.place_pose),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaPickPlace_Result

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaPickPlace_Result {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_Result::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_Result {
  type RmwMsg = super::action::rmw::JengaPickPlace_Result;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
        error_code: msg.error_code,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      error_code: msg.error_code,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
      error_code: msg.error_code,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaPickPlace_Feedback

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaPickPlace_Feedback {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_Feedback::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_Feedback {
  type RmwMsg = super::action::rmw::JengaPickPlace_Feedback;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
        progress_pct: msg.progress_pct,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
      progress_pct: msg.progress_pct,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      current_stage: msg.current_stage.to_string(),
      progress_pct: msg.progress_pct,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaPickPlace_FeedbackMessage

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::action::JengaPickPlace_Feedback,

}



impl Default for JengaPickPlace_FeedbackMessage {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_FeedbackMessage::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_FeedbackMessage {
  type RmwMsg = super::action::rmw::JengaPickPlace_FeedbackMessage;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        feedback: super::action::JengaPickPlace_Feedback::into_rmw_message(std::borrow::Cow::Owned(msg.feedback)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        feedback: super::action::JengaPickPlace_Feedback::into_rmw_message(std::borrow::Cow::Borrowed(&msg.feedback)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      feedback: super::action::JengaPickPlace_Feedback::from_rmw_message(msg.feedback),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_Goal

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub target_state: std::string::String,

}



impl Default for JengaArmReady_Goal {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_Goal::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_Goal {
  type RmwMsg = super::action::rmw::JengaArmReady_Goal;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        target_state: msg.target_state.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        target_state: msg.target_state.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      target_state: msg.target_state.to_string(),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_Result

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaArmReady_Result {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_Result::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_Result {
  type RmwMsg = super::action::rmw::JengaArmReady_Result;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
        error_code: msg.error_code,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      error_code: msg.error_code,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
      error_code: msg.error_code,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_Feedback

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaArmReady_Feedback {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_Feedback::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_Feedback {
  type RmwMsg = super::action::rmw::JengaArmReady_Feedback;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
        progress_pct: msg.progress_pct,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
      progress_pct: msg.progress_pct,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      current_stage: msg.current_stage.to_string(),
      progress_pct: msg.progress_pct,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_FeedbackMessage

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::action::JengaArmReady_Feedback,

}



impl Default for JengaArmReady_FeedbackMessage {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_FeedbackMessage::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_FeedbackMessage {
  type RmwMsg = super::action::rmw::JengaArmReady_FeedbackMessage;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        feedback: super::action::JengaArmReady_Feedback::into_rmw_message(std::borrow::Cow::Owned(msg.feedback)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        feedback: super::action::JengaArmReady_Feedback::into_rmw_message(std::borrow::Cow::Borrowed(&msg.feedback)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      feedback: super::action::JengaArmReady_Feedback::from_rmw_message(msg.feedback),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_Goal

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub block_pose: geometry_msgs::msg::PoseStamped,


    // This member is not documented.
    #[allow(missing_docs)]
    pub place_pose: geometry_msgs::msg::PoseStamped,

}



impl Default for JengaExtractSideBlock_Goal {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_Goal::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_Goal {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_Goal;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_index: msg.block_index,
        block_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(msg.block_pose)).into_owned(),
        place_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(msg.place_pose)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      block_index: msg.block_index,
        block_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.block_pose)).into_owned(),
        place_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.place_pose)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      block_index: msg.block_index,
      block_pose: geometry_msgs::msg::PoseStamped::from_rmw_message(msg.block_pose),
      place_pose: geometry_msgs::msg::PoseStamped::from_rmw_message(msg.place_pose),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_Result

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaExtractSideBlock_Result {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_Result::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_Result {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_Result;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
        error_code: msg.error_code,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      error_code: msg.error_code,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
      error_code: msg.error_code,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_Feedback

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaExtractSideBlock_Feedback {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_Feedback::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_Feedback {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_Feedback;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
        progress_pct: msg.progress_pct,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
      progress_pct: msg.progress_pct,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      current_stage: msg.current_stage.to_string(),
      progress_pct: msg.progress_pct,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::action::JengaExtractSideBlock_Feedback,

}



impl Default for JengaExtractSideBlock_FeedbackMessage {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_FeedbackMessage::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_FeedbackMessage {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_FeedbackMessage;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        feedback: super::action::JengaExtractSideBlock_Feedback::into_rmw_message(std::borrow::Cow::Owned(msg.feedback)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        feedback: super::action::JengaExtractSideBlock_Feedback::into_rmw_message(std::borrow::Cow::Borrowed(&msg.feedback)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      feedback: super::action::JengaExtractSideBlock_Feedback::from_rmw_message(msg.feedback),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_Goal

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub block_pose: geometry_msgs::msg::PoseStamped,


    // This member is not documented.
    #[allow(missing_docs)]
    pub place_pose: geometry_msgs::msg::PoseStamped,

    /// e.g. "x", "-x". Empty string → auto-detect from planning scene; explicit string → override.
    pub extract_axis: std::string::String,

}



impl Default for JengaExtractMiddleBlock_Goal {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_Goal::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_Goal {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_Goal;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_index: msg.block_index,
        block_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(msg.block_pose)).into_owned(),
        place_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(msg.place_pose)).into_owned(),
        extract_axis: msg.extract_axis.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      block_index: msg.block_index,
        block_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.block_pose)).into_owned(),
        place_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.place_pose)).into_owned(),
        extract_axis: msg.extract_axis.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      block_index: msg.block_index,
      block_pose: geometry_msgs::msg::PoseStamped::from_rmw_message(msg.block_pose),
      place_pose: geometry_msgs::msg::PoseStamped::from_rmw_message(msg.place_pose),
      extract_axis: msg.extract_axis.to_string(),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_Result

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaExtractMiddleBlock_Result {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_Result::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_Result {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_Result;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
        error_code: msg.error_code,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      error_code: msg.error_code,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
      error_code: msg.error_code,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_Feedback

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaExtractMiddleBlock_Feedback {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_Feedback::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_Feedback {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_Feedback;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
        progress_pct: msg.progress_pct,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
      progress_pct: msg.progress_pct,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      current_stage: msg.current_stage.to_string(),
      progress_pct: msg.progress_pct,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::action::JengaExtractMiddleBlock_Feedback,

}



impl Default for JengaExtractMiddleBlock_FeedbackMessage {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_FeedbackMessage::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_FeedbackMessage {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_FeedbackMessage;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        feedback: super::action::JengaExtractMiddleBlock_Feedback::into_rmw_message(std::borrow::Cow::Owned(msg.feedback)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        feedback: super::action::JengaExtractMiddleBlock_Feedback::into_rmw_message(std::borrow::Cow::Borrowed(&msg.feedback)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      feedback: super::action::JengaExtractMiddleBlock_Feedback::from_rmw_message(msg.feedback),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_Goal

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub block_pose: geometry_msgs::msg::PoseStamped,

}



impl Default for JengaProbeBlock_Goal {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_Goal::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_Goal {
  type RmwMsg = super::action::rmw::JengaProbeBlock_Goal;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_index: msg.block_index,
        block_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Owned(msg.block_pose)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      block_index: msg.block_index,
        block_pose: geometry_msgs::msg::PoseStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.block_pose)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      block_index: msg.block_index,
      block_pose: geometry_msgs::msg::PoseStamped::from_rmw_message(msg.block_pose),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_Result

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub score: f32,

    /// 0=UNKNOWN, 1=LOOSE, 2=STUCK, 3=ERROR
    pub probe_outcome: u8,

    /// actual distance pushed along probe axis
    pub displacement_m: f32,

    /// peak contact force observed during push
    pub max_force_n: f32,

}



impl Default for JengaProbeBlock_Result {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_Result::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_Result {
  type RmwMsg = super::action::rmw::JengaProbeBlock_Result;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
        error_code: msg.error_code,
        score: msg.score,
        probe_outcome: msg.probe_outcome,
        displacement_m: msg.displacement_m,
        max_force_n: msg.max_force_n,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      error_code: msg.error_code,
      score: msg.score,
      probe_outcome: msg.probe_outcome,
      displacement_m: msg.displacement_m,
      max_force_n: msg.max_force_n,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
      error_code: msg.error_code,
      score: msg.score,
      probe_outcome: msg.probe_outcome,
      displacement_m: msg.displacement_m,
      max_force_n: msg.max_force_n,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_Feedback

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaProbeBlock_Feedback {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_Feedback::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_Feedback {
  type RmwMsg = super::action::rmw::JengaProbeBlock_Feedback;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
        progress_pct: msg.progress_pct,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        current_stage: msg.current_stage.as_str().into(),
      progress_pct: msg.progress_pct,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      current_stage: msg.current_stage.to_string(),
      progress_pct: msg.progress_pct,
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_FeedbackMessage

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::action::JengaProbeBlock_Feedback,

}



impl Default for JengaProbeBlock_FeedbackMessage {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_FeedbackMessage::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_FeedbackMessage {
  type RmwMsg = super::action::rmw::JengaProbeBlock_FeedbackMessage;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        feedback: super::action::JengaProbeBlock_Feedback::into_rmw_message(std::borrow::Cow::Owned(msg.feedback)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        feedback: super::action::JengaProbeBlock_Feedback::into_rmw_message(std::borrow::Cow::Borrowed(&msg.feedback)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      feedback: super::action::JengaProbeBlock_Feedback::from_rmw_message(msg.feedback),
    }
  }
}






// Corresponds to jenga_interfaces__action__JengaPickPlace_SendGoal_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::action::JengaPickPlace_Goal,

}



impl Default for JengaPickPlace_SendGoal_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_SendGoal_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_SendGoal_Request {
  type RmwMsg = super::action::rmw::JengaPickPlace_SendGoal_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        goal: super::action::JengaPickPlace_Goal::into_rmw_message(std::borrow::Cow::Owned(msg.goal)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        goal: super::action::JengaPickPlace_Goal::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      goal: super::action::JengaPickPlace_Goal::from_rmw_message(msg.goal),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaPickPlace_SendGoal_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,

}



impl Default for JengaPickPlace_SendGoal_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_SendGoal_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_SendGoal_Response {
  type RmwMsg = super::action::rmw::JengaPickPlace_SendGoal_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      accepted: msg.accepted,
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaPickPlace_GetResult_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,

}



impl Default for JengaPickPlace_GetResult_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_GetResult_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_GetResult_Request {
  type RmwMsg = super::action::rmw::JengaPickPlace_GetResult_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaPickPlace_GetResult_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::action::JengaPickPlace_Result,

}



impl Default for JengaPickPlace_GetResult_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaPickPlace_GetResult_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_GetResult_Response {
  type RmwMsg = super::action::rmw::JengaPickPlace_GetResult_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status,
        result: super::action::JengaPickPlace_Result::into_rmw_message(std::borrow::Cow::Owned(msg.result)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      status: msg.status,
        result: super::action::JengaPickPlace_Result::into_rmw_message(std::borrow::Cow::Borrowed(&msg.result)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status,
      result: super::action::JengaPickPlace_Result::from_rmw_message(msg.result),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_SendGoal_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::action::JengaArmReady_Goal,

}



impl Default for JengaArmReady_SendGoal_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_SendGoal_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_SendGoal_Request {
  type RmwMsg = super::action::rmw::JengaArmReady_SendGoal_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        goal: super::action::JengaArmReady_Goal::into_rmw_message(std::borrow::Cow::Owned(msg.goal)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        goal: super::action::JengaArmReady_Goal::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      goal: super::action::JengaArmReady_Goal::from_rmw_message(msg.goal),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_SendGoal_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,

}



impl Default for JengaArmReady_SendGoal_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_SendGoal_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_SendGoal_Response {
  type RmwMsg = super::action::rmw::JengaArmReady_SendGoal_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      accepted: msg.accepted,
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_GetResult_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,

}



impl Default for JengaArmReady_GetResult_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_GetResult_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_GetResult_Request {
  type RmwMsg = super::action::rmw::JengaArmReady_GetResult_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaArmReady_GetResult_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::action::JengaArmReady_Result,

}



impl Default for JengaArmReady_GetResult_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaArmReady_GetResult_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_GetResult_Response {
  type RmwMsg = super::action::rmw::JengaArmReady_GetResult_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status,
        result: super::action::JengaArmReady_Result::into_rmw_message(std::borrow::Cow::Owned(msg.result)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      status: msg.status,
        result: super::action::JengaArmReady_Result::into_rmw_message(std::borrow::Cow::Borrowed(&msg.result)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status,
      result: super::action::JengaArmReady_Result::from_rmw_message(msg.result),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::action::JengaExtractSideBlock_Goal,

}



impl Default for JengaExtractSideBlock_SendGoal_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_SendGoal_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_SendGoal_Request {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_SendGoal_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        goal: super::action::JengaExtractSideBlock_Goal::into_rmw_message(std::borrow::Cow::Owned(msg.goal)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        goal: super::action::JengaExtractSideBlock_Goal::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      goal: super::action::JengaExtractSideBlock_Goal::from_rmw_message(msg.goal),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,

}



impl Default for JengaExtractSideBlock_SendGoal_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_SendGoal_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_SendGoal_Response {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_SendGoal_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      accepted: msg.accepted,
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,

}



impl Default for JengaExtractSideBlock_GetResult_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_GetResult_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_GetResult_Request {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_GetResult_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::action::JengaExtractSideBlock_Result,

}



impl Default for JengaExtractSideBlock_GetResult_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractSideBlock_GetResult_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_GetResult_Response {
  type RmwMsg = super::action::rmw::JengaExtractSideBlock_GetResult_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status,
        result: super::action::JengaExtractSideBlock_Result::into_rmw_message(std::borrow::Cow::Owned(msg.result)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      status: msg.status,
        result: super::action::JengaExtractSideBlock_Result::into_rmw_message(std::borrow::Cow::Borrowed(&msg.result)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status,
      result: super::action::JengaExtractSideBlock_Result::from_rmw_message(msg.result),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::action::JengaExtractMiddleBlock_Goal,

}



impl Default for JengaExtractMiddleBlock_SendGoal_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_SendGoal_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_SendGoal_Request {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_SendGoal_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        goal: super::action::JengaExtractMiddleBlock_Goal::into_rmw_message(std::borrow::Cow::Owned(msg.goal)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        goal: super::action::JengaExtractMiddleBlock_Goal::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      goal: super::action::JengaExtractMiddleBlock_Goal::from_rmw_message(msg.goal),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,

}



impl Default for JengaExtractMiddleBlock_SendGoal_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_SendGoal_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_SendGoal_Response {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_SendGoal_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      accepted: msg.accepted,
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,

}



impl Default for JengaExtractMiddleBlock_GetResult_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_GetResult_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_GetResult_Request {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_GetResult_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::action::JengaExtractMiddleBlock_Result,

}



impl Default for JengaExtractMiddleBlock_GetResult_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaExtractMiddleBlock_GetResult_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_GetResult_Response {
  type RmwMsg = super::action::rmw::JengaExtractMiddleBlock_GetResult_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status,
        result: super::action::JengaExtractMiddleBlock_Result::into_rmw_message(std::borrow::Cow::Owned(msg.result)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      status: msg.status,
        result: super::action::JengaExtractMiddleBlock_Result::into_rmw_message(std::borrow::Cow::Borrowed(&msg.result)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status,
      result: super::action::JengaExtractMiddleBlock_Result::from_rmw_message(msg.result),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_SendGoal_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::action::JengaProbeBlock_Goal,

}



impl Default for JengaProbeBlock_SendGoal_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_SendGoal_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_SendGoal_Request {
  type RmwMsg = super::action::rmw::JengaProbeBlock_SendGoal_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        goal: super::action::JengaProbeBlock_Goal::into_rmw_message(std::borrow::Cow::Owned(msg.goal)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
        goal: super::action::JengaProbeBlock_Goal::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
      goal: super::action::JengaProbeBlock_Goal::from_rmw_message(msg.goal),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_SendGoal_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::Time,

}



impl Default for JengaProbeBlock_SendGoal_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_SendGoal_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_SendGoal_Response {
  type RmwMsg = super::action::rmw::JengaProbeBlock_SendGoal_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      accepted: msg.accepted,
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      accepted: msg.accepted,
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_GetResult_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::UUID,

}



impl Default for JengaProbeBlock_GetResult_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_GetResult_Request::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_GetResult_Request {
  type RmwMsg = super::action::rmw::JengaProbeBlock_GetResult_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: unique_identifier_msgs::msg::UUID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: unique_identifier_msgs::msg::UUID::from_rmw_message(msg.goal_id),
    }
  }
}


// Corresponds to jenga_interfaces__action__JengaProbeBlock_GetResult_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::action::JengaProbeBlock_Result,

}



impl Default for JengaProbeBlock_GetResult_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::action::rmw::JengaProbeBlock_GetResult_Response::default())
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_GetResult_Response {
  type RmwMsg = super::action::rmw::JengaProbeBlock_GetResult_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status,
        result: super::action::JengaProbeBlock_Result::into_rmw_message(std::borrow::Cow::Owned(msg.result)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      status: msg.status,
        result: super::action::JengaProbeBlock_Result::into_rmw_message(std::borrow::Cow::Borrowed(&msg.result)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status,
      result: super::action::JengaProbeBlock_Result::from_rmw_message(msg.result),
    }
  }
}






#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaPickPlace_SendGoal() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_SendGoal
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaPickPlace_SendGoal;

impl rosidl_runtime_rs::Service for JengaPickPlace_SendGoal {
    type Request = JengaPickPlace_SendGoal_Request;
    type Response = JengaPickPlace_SendGoal_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaPickPlace_SendGoal() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaPickPlace_GetResult() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_GetResult
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaPickPlace_GetResult;

impl rosidl_runtime_rs::Service for JengaPickPlace_GetResult {
    type Request = JengaPickPlace_GetResult_Request;
    type Response = JengaPickPlace_GetResult_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaPickPlace_GetResult() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaArmReady_SendGoal() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_SendGoal
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaArmReady_SendGoal;

impl rosidl_runtime_rs::Service for JengaArmReady_SendGoal {
    type Request = JengaArmReady_SendGoal_Request;
    type Response = JengaArmReady_SendGoal_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaArmReady_SendGoal() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaArmReady_GetResult() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_GetResult
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaArmReady_GetResult;

impl rosidl_runtime_rs::Service for JengaArmReady_GetResult {
    type Request = JengaArmReady_GetResult_Request;
    type Response = JengaArmReady_GetResult_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaArmReady_GetResult() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_SendGoal() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_SendGoal
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaExtractSideBlock_SendGoal;

impl rosidl_runtime_rs::Service for JengaExtractSideBlock_SendGoal {
    type Request = JengaExtractSideBlock_SendGoal_Request;
    type Response = JengaExtractSideBlock_SendGoal_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_SendGoal() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_GetResult() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_GetResult
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaExtractSideBlock_GetResult;

impl rosidl_runtime_rs::Service for JengaExtractSideBlock_GetResult {
    type Request = JengaExtractSideBlock_GetResult_Request;
    type Response = JengaExtractSideBlock_GetResult_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_GetResult() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaExtractMiddleBlock_SendGoal;

impl rosidl_runtime_rs::Service for JengaExtractMiddleBlock_SendGoal {
    type Request = JengaExtractMiddleBlock_SendGoal_Request;
    type Response = JengaExtractMiddleBlock_SendGoal_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_GetResult() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_GetResult
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaExtractMiddleBlock_GetResult;

impl rosidl_runtime_rs::Service for JengaExtractMiddleBlock_GetResult {
    type Request = JengaExtractMiddleBlock_GetResult_Request;
    type Response = JengaExtractMiddleBlock_GetResult_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_GetResult() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaProbeBlock_SendGoal() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_SendGoal
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaProbeBlock_SendGoal;

impl rosidl_runtime_rs::Service for JengaProbeBlock_SendGoal {
    type Request = JengaProbeBlock_SendGoal_Request;
    type Response = JengaProbeBlock_SendGoal_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaProbeBlock_SendGoal() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaProbeBlock_GetResult() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_GetResult
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaProbeBlock_GetResult;

impl rosidl_runtime_rs::Service for JengaProbeBlock_GetResult {
    type Request = JengaProbeBlock_GetResult_Request;
    type Response = JengaProbeBlock_GetResult_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__action__JengaProbeBlock_GetResult() }
    }
}






#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaPickPlace() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaPickPlace;

impl rosidl_runtime_rs::Action for JengaPickPlace {
  // --- Associated types for client library users ---
  /// The goal message defined in the action definition.
  type Goal = JengaPickPlace_Goal;

  /// The result message defined in the action definition.
  type Result = JengaPickPlace_Result;

  /// The feedback message defined in the action definition.
  type Feedback = JengaPickPlace_Feedback;

  // --- Associated types for client library implementation ---
  /// The feedback message with generic fields which wraps the feedback message.
  type FeedbackMessage = super::action::JengaPickPlace_FeedbackMessage;

  /// The send_goal service using a wrapped version of the goal message as a request.
  type SendGoalService = super::action::JengaPickPlace_SendGoal;

  /// The generic service to cancel a goal.
  type CancelGoalService = action_msgs::srv::rmw::CancelGoal;

  /// The get_result service using a wrapped version of the result message as a response.
  type GetResultService = super::action::JengaPickPlace_GetResult;

  // --- Methods for client library implementation ---
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaPickPlace() }
  }

  fn create_goal_request(
    goal_id: &[u8; 16],
    goal: super::action::rmw::JengaPickPlace_Goal,
  ) -> super::action::rmw::JengaPickPlace_SendGoal_Request {
   super::action::rmw::JengaPickPlace_SendGoal_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
      goal,
    }
  }

  fn split_goal_request(
    request: super::action::rmw::JengaPickPlace_SendGoal_Request,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaPickPlace_Goal,
  ) {
    (request.goal_id.uuid, request.goal)
  }

  fn create_goal_response(
    accepted: bool,
    stamp: (i32, u32),
  ) -> super::action::rmw::JengaPickPlace_SendGoal_Response {
   super::action::rmw::JengaPickPlace_SendGoal_Response {
      accepted,
      stamp: builtin_interfaces::msg::rmw::Time {
        sec: stamp.0,
        nanosec: stamp.1,
      },
    }
  }

  fn get_goal_response_accepted(
    response: &super::action::rmw::JengaPickPlace_SendGoal_Response,
  ) -> bool {
    response.accepted
  }

  fn get_goal_response_stamp(
    response: &super::action::rmw::JengaPickPlace_SendGoal_Response,
  ) -> (i32, u32) {
    (response.stamp.sec, response.stamp.nanosec)
  }

  fn create_feedback_message(
    goal_id: &[u8; 16],
    feedback: super::action::rmw::JengaPickPlace_Feedback,
  ) -> super::action::rmw::JengaPickPlace_FeedbackMessage {
    let mut message = super::action::rmw::JengaPickPlace_FeedbackMessage::default();
    message.goal_id.uuid = *goal_id;
    message.feedback = feedback;
    message
  }

  fn split_feedback_message(
    feedback: super::action::rmw::JengaPickPlace_FeedbackMessage,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaPickPlace_Feedback,
  ) {
    (feedback.goal_id.uuid, feedback.feedback)
  }

  fn create_result_request(
    goal_id: &[u8; 16],
  ) -> super::action::rmw::JengaPickPlace_GetResult_Request {
   super::action::rmw::JengaPickPlace_GetResult_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
    }
  }

  fn get_result_request_uuid(
    request: &super::action::rmw::JengaPickPlace_GetResult_Request,
  ) -> &[u8; 16] {
    &request.goal_id.uuid
  }

  fn create_result_response(
    status: i8,
    result: super::action::rmw::JengaPickPlace_Result,
  ) -> super::action::rmw::JengaPickPlace_GetResult_Response {
   super::action::rmw::JengaPickPlace_GetResult_Response {
      status,
      result,
    }
  }

  fn split_result_response(
    response: super::action::rmw::JengaPickPlace_GetResult_Response
  ) -> (
    i8,
   super::action::rmw::JengaPickPlace_Result,
  ) {
    (response.status, response.result)
  }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaArmReady() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaArmReady
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaArmReady;

impl rosidl_runtime_rs::Action for JengaArmReady {
  // --- Associated types for client library users ---
  /// The goal message defined in the action definition.
  type Goal = JengaArmReady_Goal;

  /// The result message defined in the action definition.
  type Result = JengaArmReady_Result;

  /// The feedback message defined in the action definition.
  type Feedback = JengaArmReady_Feedback;

  // --- Associated types for client library implementation ---
  /// The feedback message with generic fields which wraps the feedback message.
  type FeedbackMessage = super::action::JengaArmReady_FeedbackMessage;

  /// The send_goal service using a wrapped version of the goal message as a request.
  type SendGoalService = super::action::JengaArmReady_SendGoal;

  /// The generic service to cancel a goal.
  type CancelGoalService = action_msgs::srv::rmw::CancelGoal;

  /// The get_result service using a wrapped version of the result message as a response.
  type GetResultService = super::action::JengaArmReady_GetResult;

  // --- Methods for client library implementation ---
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaArmReady() }
  }

  fn create_goal_request(
    goal_id: &[u8; 16],
    goal: super::action::rmw::JengaArmReady_Goal,
  ) -> super::action::rmw::JengaArmReady_SendGoal_Request {
   super::action::rmw::JengaArmReady_SendGoal_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
      goal,
    }
  }

  fn split_goal_request(
    request: super::action::rmw::JengaArmReady_SendGoal_Request,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaArmReady_Goal,
  ) {
    (request.goal_id.uuid, request.goal)
  }

  fn create_goal_response(
    accepted: bool,
    stamp: (i32, u32),
  ) -> super::action::rmw::JengaArmReady_SendGoal_Response {
   super::action::rmw::JengaArmReady_SendGoal_Response {
      accepted,
      stamp: builtin_interfaces::msg::rmw::Time {
        sec: stamp.0,
        nanosec: stamp.1,
      },
    }
  }

  fn get_goal_response_accepted(
    response: &super::action::rmw::JengaArmReady_SendGoal_Response,
  ) -> bool {
    response.accepted
  }

  fn get_goal_response_stamp(
    response: &super::action::rmw::JengaArmReady_SendGoal_Response,
  ) -> (i32, u32) {
    (response.stamp.sec, response.stamp.nanosec)
  }

  fn create_feedback_message(
    goal_id: &[u8; 16],
    feedback: super::action::rmw::JengaArmReady_Feedback,
  ) -> super::action::rmw::JengaArmReady_FeedbackMessage {
    let mut message = super::action::rmw::JengaArmReady_FeedbackMessage::default();
    message.goal_id.uuid = *goal_id;
    message.feedback = feedback;
    message
  }

  fn split_feedback_message(
    feedback: super::action::rmw::JengaArmReady_FeedbackMessage,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaArmReady_Feedback,
  ) {
    (feedback.goal_id.uuid, feedback.feedback)
  }

  fn create_result_request(
    goal_id: &[u8; 16],
  ) -> super::action::rmw::JengaArmReady_GetResult_Request {
   super::action::rmw::JengaArmReady_GetResult_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
    }
  }

  fn get_result_request_uuid(
    request: &super::action::rmw::JengaArmReady_GetResult_Request,
  ) -> &[u8; 16] {
    &request.goal_id.uuid
  }

  fn create_result_response(
    status: i8,
    result: super::action::rmw::JengaArmReady_Result,
  ) -> super::action::rmw::JengaArmReady_GetResult_Response {
   super::action::rmw::JengaArmReady_GetResult_Response {
      status,
      result,
    }
  }

  fn split_result_response(
    response: super::action::rmw::JengaArmReady_GetResult_Response
  ) -> (
    i8,
   super::action::rmw::JengaArmReady_Result,
  ) {
    (response.status, response.result)
  }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaExtractSideBlock;

impl rosidl_runtime_rs::Action for JengaExtractSideBlock {
  // --- Associated types for client library users ---
  /// The goal message defined in the action definition.
  type Goal = JengaExtractSideBlock_Goal;

  /// The result message defined in the action definition.
  type Result = JengaExtractSideBlock_Result;

  /// The feedback message defined in the action definition.
  type Feedback = JengaExtractSideBlock_Feedback;

  // --- Associated types for client library implementation ---
  /// The feedback message with generic fields which wraps the feedback message.
  type FeedbackMessage = super::action::JengaExtractSideBlock_FeedbackMessage;

  /// The send_goal service using a wrapped version of the goal message as a request.
  type SendGoalService = super::action::JengaExtractSideBlock_SendGoal;

  /// The generic service to cancel a goal.
  type CancelGoalService = action_msgs::srv::rmw::CancelGoal;

  /// The get_result service using a wrapped version of the result message as a response.
  type GetResultService = super::action::JengaExtractSideBlock_GetResult;

  // --- Methods for client library implementation ---
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock() }
  }

  fn create_goal_request(
    goal_id: &[u8; 16],
    goal: super::action::rmw::JengaExtractSideBlock_Goal,
  ) -> super::action::rmw::JengaExtractSideBlock_SendGoal_Request {
   super::action::rmw::JengaExtractSideBlock_SendGoal_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
      goal,
    }
  }

  fn split_goal_request(
    request: super::action::rmw::JengaExtractSideBlock_SendGoal_Request,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaExtractSideBlock_Goal,
  ) {
    (request.goal_id.uuid, request.goal)
  }

  fn create_goal_response(
    accepted: bool,
    stamp: (i32, u32),
  ) -> super::action::rmw::JengaExtractSideBlock_SendGoal_Response {
   super::action::rmw::JengaExtractSideBlock_SendGoal_Response {
      accepted,
      stamp: builtin_interfaces::msg::rmw::Time {
        sec: stamp.0,
        nanosec: stamp.1,
      },
    }
  }

  fn get_goal_response_accepted(
    response: &super::action::rmw::JengaExtractSideBlock_SendGoal_Response,
  ) -> bool {
    response.accepted
  }

  fn get_goal_response_stamp(
    response: &super::action::rmw::JengaExtractSideBlock_SendGoal_Response,
  ) -> (i32, u32) {
    (response.stamp.sec, response.stamp.nanosec)
  }

  fn create_feedback_message(
    goal_id: &[u8; 16],
    feedback: super::action::rmw::JengaExtractSideBlock_Feedback,
  ) -> super::action::rmw::JengaExtractSideBlock_FeedbackMessage {
    let mut message = super::action::rmw::JengaExtractSideBlock_FeedbackMessage::default();
    message.goal_id.uuid = *goal_id;
    message.feedback = feedback;
    message
  }

  fn split_feedback_message(
    feedback: super::action::rmw::JengaExtractSideBlock_FeedbackMessage,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaExtractSideBlock_Feedback,
  ) {
    (feedback.goal_id.uuid, feedback.feedback)
  }

  fn create_result_request(
    goal_id: &[u8; 16],
  ) -> super::action::rmw::JengaExtractSideBlock_GetResult_Request {
   super::action::rmw::JengaExtractSideBlock_GetResult_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
    }
  }

  fn get_result_request_uuid(
    request: &super::action::rmw::JengaExtractSideBlock_GetResult_Request,
  ) -> &[u8; 16] {
    &request.goal_id.uuid
  }

  fn create_result_response(
    status: i8,
    result: super::action::rmw::JengaExtractSideBlock_Result,
  ) -> super::action::rmw::JengaExtractSideBlock_GetResult_Response {
   super::action::rmw::JengaExtractSideBlock_GetResult_Response {
      status,
      result,
    }
  }

  fn split_result_response(
    response: super::action::rmw::JengaExtractSideBlock_GetResult_Response
  ) -> (
    i8,
   super::action::rmw::JengaExtractSideBlock_Result,
  ) {
    (response.status, response.result)
  }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaExtractMiddleBlock;

impl rosidl_runtime_rs::Action for JengaExtractMiddleBlock {
  // --- Associated types for client library users ---
  /// The goal message defined in the action definition.
  type Goal = JengaExtractMiddleBlock_Goal;

  /// The result message defined in the action definition.
  type Result = JengaExtractMiddleBlock_Result;

  /// The feedback message defined in the action definition.
  type Feedback = JengaExtractMiddleBlock_Feedback;

  // --- Associated types for client library implementation ---
  /// The feedback message with generic fields which wraps the feedback message.
  type FeedbackMessage = super::action::JengaExtractMiddleBlock_FeedbackMessage;

  /// The send_goal service using a wrapped version of the goal message as a request.
  type SendGoalService = super::action::JengaExtractMiddleBlock_SendGoal;

  /// The generic service to cancel a goal.
  type CancelGoalService = action_msgs::srv::rmw::CancelGoal;

  /// The get_result service using a wrapped version of the result message as a response.
  type GetResultService = super::action::JengaExtractMiddleBlock_GetResult;

  // --- Methods for client library implementation ---
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock() }
  }

  fn create_goal_request(
    goal_id: &[u8; 16],
    goal: super::action::rmw::JengaExtractMiddleBlock_Goal,
  ) -> super::action::rmw::JengaExtractMiddleBlock_SendGoal_Request {
   super::action::rmw::JengaExtractMiddleBlock_SendGoal_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
      goal,
    }
  }

  fn split_goal_request(
    request: super::action::rmw::JengaExtractMiddleBlock_SendGoal_Request,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaExtractMiddleBlock_Goal,
  ) {
    (request.goal_id.uuid, request.goal)
  }

  fn create_goal_response(
    accepted: bool,
    stamp: (i32, u32),
  ) -> super::action::rmw::JengaExtractMiddleBlock_SendGoal_Response {
   super::action::rmw::JengaExtractMiddleBlock_SendGoal_Response {
      accepted,
      stamp: builtin_interfaces::msg::rmw::Time {
        sec: stamp.0,
        nanosec: stamp.1,
      },
    }
  }

  fn get_goal_response_accepted(
    response: &super::action::rmw::JengaExtractMiddleBlock_SendGoal_Response,
  ) -> bool {
    response.accepted
  }

  fn get_goal_response_stamp(
    response: &super::action::rmw::JengaExtractMiddleBlock_SendGoal_Response,
  ) -> (i32, u32) {
    (response.stamp.sec, response.stamp.nanosec)
  }

  fn create_feedback_message(
    goal_id: &[u8; 16],
    feedback: super::action::rmw::JengaExtractMiddleBlock_Feedback,
  ) -> super::action::rmw::JengaExtractMiddleBlock_FeedbackMessage {
    let mut message = super::action::rmw::JengaExtractMiddleBlock_FeedbackMessage::default();
    message.goal_id.uuid = *goal_id;
    message.feedback = feedback;
    message
  }

  fn split_feedback_message(
    feedback: super::action::rmw::JengaExtractMiddleBlock_FeedbackMessage,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaExtractMiddleBlock_Feedback,
  ) {
    (feedback.goal_id.uuid, feedback.feedback)
  }

  fn create_result_request(
    goal_id: &[u8; 16],
  ) -> super::action::rmw::JengaExtractMiddleBlock_GetResult_Request {
   super::action::rmw::JengaExtractMiddleBlock_GetResult_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
    }
  }

  fn get_result_request_uuid(
    request: &super::action::rmw::JengaExtractMiddleBlock_GetResult_Request,
  ) -> &[u8; 16] {
    &request.goal_id.uuid
  }

  fn create_result_response(
    status: i8,
    result: super::action::rmw::JengaExtractMiddleBlock_Result,
  ) -> super::action::rmw::JengaExtractMiddleBlock_GetResult_Response {
   super::action::rmw::JengaExtractMiddleBlock_GetResult_Response {
      status,
      result,
    }
  }

  fn split_result_response(
    response: super::action::rmw::JengaExtractMiddleBlock_GetResult_Response
  ) -> (
    i8,
   super::action::rmw::JengaExtractMiddleBlock_Result,
  ) {
    (response.status, response.result)
  }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaProbeBlock() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock
#[allow(missing_docs, non_camel_case_types)]
pub struct JengaProbeBlock;

impl rosidl_runtime_rs::Action for JengaProbeBlock {
  // --- Associated types for client library users ---
  /// The goal message defined in the action definition.
  type Goal = JengaProbeBlock_Goal;

  /// The result message defined in the action definition.
  type Result = JengaProbeBlock_Result;

  /// The feedback message defined in the action definition.
  type Feedback = JengaProbeBlock_Feedback;

  // --- Associated types for client library implementation ---
  /// The feedback message with generic fields which wraps the feedback message.
  type FeedbackMessage = super::action::JengaProbeBlock_FeedbackMessage;

  /// The send_goal service using a wrapped version of the goal message as a request.
  type SendGoalService = super::action::JengaProbeBlock_SendGoal;

  /// The generic service to cancel a goal.
  type CancelGoalService = action_msgs::srv::rmw::CancelGoal;

  /// The get_result service using a wrapped version of the result message as a response.
  type GetResultService = super::action::JengaProbeBlock_GetResult;

  // --- Methods for client library implementation ---
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_action_type_support_handle__jenga_interfaces__action__JengaProbeBlock() }
  }

  fn create_goal_request(
    goal_id: &[u8; 16],
    goal: super::action::rmw::JengaProbeBlock_Goal,
  ) -> super::action::rmw::JengaProbeBlock_SendGoal_Request {
   super::action::rmw::JengaProbeBlock_SendGoal_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
      goal,
    }
  }

  fn split_goal_request(
    request: super::action::rmw::JengaProbeBlock_SendGoal_Request,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaProbeBlock_Goal,
  ) {
    (request.goal_id.uuid, request.goal)
  }

  fn create_goal_response(
    accepted: bool,
    stamp: (i32, u32),
  ) -> super::action::rmw::JengaProbeBlock_SendGoal_Response {
   super::action::rmw::JengaProbeBlock_SendGoal_Response {
      accepted,
      stamp: builtin_interfaces::msg::rmw::Time {
        sec: stamp.0,
        nanosec: stamp.1,
      },
    }
  }

  fn get_goal_response_accepted(
    response: &super::action::rmw::JengaProbeBlock_SendGoal_Response,
  ) -> bool {
    response.accepted
  }

  fn get_goal_response_stamp(
    response: &super::action::rmw::JengaProbeBlock_SendGoal_Response,
  ) -> (i32, u32) {
    (response.stamp.sec, response.stamp.nanosec)
  }

  fn create_feedback_message(
    goal_id: &[u8; 16],
    feedback: super::action::rmw::JengaProbeBlock_Feedback,
  ) -> super::action::rmw::JengaProbeBlock_FeedbackMessage {
    let mut message = super::action::rmw::JengaProbeBlock_FeedbackMessage::default();
    message.goal_id.uuid = *goal_id;
    message.feedback = feedback;
    message
  }

  fn split_feedback_message(
    feedback: super::action::rmw::JengaProbeBlock_FeedbackMessage,
  ) -> (
    [u8; 16],
   super::action::rmw::JengaProbeBlock_Feedback,
  ) {
    (feedback.goal_id.uuid, feedback.feedback)
  }

  fn create_result_request(
    goal_id: &[u8; 16],
  ) -> super::action::rmw::JengaProbeBlock_GetResult_Request {
   super::action::rmw::JengaProbeBlock_GetResult_Request {
      goal_id: unique_identifier_msgs::msg::rmw::UUID { uuid: *goal_id },
    }
  }

  fn get_result_request_uuid(
    request: &super::action::rmw::JengaProbeBlock_GetResult_Request,
  ) -> &[u8; 16] {
    &request.goal_id.uuid
  }

  fn create_result_response(
    status: i8,
    result: super::action::rmw::JengaProbeBlock_Result,
  ) -> super::action::rmw::JengaProbeBlock_GetResult_Response {
   super::action::rmw::JengaProbeBlock_GetResult_Response {
      status,
      result,
    }
  }

  fn split_result_response(
    response: super::action::rmw::JengaProbeBlock_GetResult_Response
  ) -> (
    i8,
   super::action::rmw::JengaProbeBlock_Result,
  ) {
    (response.status, response.result)
  }
}


