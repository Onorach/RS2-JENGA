#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to jenga_interfaces__msg__JengaBlockState

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaBlockState {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_id: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub colour: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub layer: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub layer_position: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::Pose,

}



impl Default for JengaBlockState {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::JengaBlockState::default())
  }
}

impl rosidl_runtime_rs::Message for JengaBlockState {
  type RmwMsg = super::msg::rmw::JengaBlockState;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_id: msg.block_id,
        colour: msg.colour.as_str().into(),
        layer: msg.layer,
        layer_position: msg.layer_position,
        pose: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Owned(msg.pose)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      block_id: msg.block_id,
        colour: msg.colour.as_str().into(),
      layer: msg.layer,
      layer_position: msg.layer_position,
        pose: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Borrowed(&msg.pose)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      block_id: msg.block_id,
      colour: msg.colour.to_string(),
      layer: msg.layer,
      layer_position: msg.layer_position,
      pose: geometry_msgs::msg::Pose::from_rmw_message(msg.pose),
    }
  }
}


// Corresponds to jenga_interfaces__msg__JengaBlockStates

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaBlockStates {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub blocks: Vec<super::msg::JengaBlockState>,

}



impl Default for JengaBlockStates {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::JengaBlockStates::default())
  }
}

impl rosidl_runtime_rs::Message for JengaBlockStates {
  type RmwMsg = super::msg::rmw::JengaBlockStates;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        blocks: msg.blocks
          .into_iter()
          .map(|elem| super::msg::JengaBlockState::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        blocks: msg.blocks
          .iter()
          .map(|elem| super::msg::JengaBlockState::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      blocks: msg.blocks
          .into_iter()
          .map(super::msg::JengaBlockState::from_rmw_message)
          .collect(),
    }
  }
}


