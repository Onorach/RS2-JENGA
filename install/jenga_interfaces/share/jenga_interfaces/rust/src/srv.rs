#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to jenga_interfaces__srv__ProtrudeJengaBlock_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ProtrudeJengaBlock_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub distance_m: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub axis: std::string::String,

}



impl Default for ProtrudeJengaBlock_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ProtrudeJengaBlock_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ProtrudeJengaBlock_Request {
  type RmwMsg = super::srv::rmw::ProtrudeJengaBlock_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_index: msg.block_index,
        distance_m: msg.distance_m,
        axis: msg.axis.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      block_index: msg.block_index,
      distance_m: msg.distance_m,
        axis: msg.axis.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      block_index: msg.block_index,
      distance_m: msg.distance_m,
      axis: msg.axis.to_string(),
    }
  }
}


// Corresponds to jenga_interfaces__srv__ProtrudeJengaBlock_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ProtrudeJengaBlock_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,

}



impl Default for ProtrudeJengaBlock_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ProtrudeJengaBlock_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ProtrudeJengaBlock_Response {
  type RmwMsg = super::srv::rmw::ProtrudeJengaBlock_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
    }
  }
}


// Corresponds to jenga_interfaces__srv__SetJengaBlocksLayout_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetJengaBlocksLayout_Request {
    /// empty = all blocks
    pub block_indices: Vec<u32>,

    /// "stock" | "tower"
    pub target_layout: std::string::String,

}



impl Default for SetJengaBlocksLayout_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::SetJengaBlocksLayout_Request::default())
  }
}

impl rosidl_runtime_rs::Message for SetJengaBlocksLayout_Request {
  type RmwMsg = super::srv::rmw::SetJengaBlocksLayout_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_indices: msg.block_indices.into(),
        target_layout: msg.target_layout.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        block_indices: msg.block_indices.as_slice().into(),
        target_layout: msg.target_layout.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      block_indices: msg.block_indices
          .into_iter()
          .collect(),
      target_layout: msg.target_layout.to_string(),
    }
  }
}


// Corresponds to jenga_interfaces__srv__SetJengaBlocksLayout_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetJengaBlocksLayout_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,

}



impl Default for SetJengaBlocksLayout_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::SetJengaBlocksLayout_Response::default())
  }
}

impl rosidl_runtime_rs::Message for SetJengaBlocksLayout_Response {
  type RmwMsg = super::srv::rmw::SetJengaBlocksLayout_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
    }
  }
}






#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__srv__ProtrudeJengaBlock() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__srv__ProtrudeJengaBlock
#[allow(missing_docs, non_camel_case_types)]
pub struct ProtrudeJengaBlock;

impl rosidl_runtime_rs::Service for ProtrudeJengaBlock {
    type Request = ProtrudeJengaBlock_Request;
    type Response = ProtrudeJengaBlock_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__srv__ProtrudeJengaBlock() }
    }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__srv__SetJengaBlocksLayout() -> *const std::ffi::c_void;
}

// Corresponds to jenga_interfaces__srv__SetJengaBlocksLayout
#[allow(missing_docs, non_camel_case_types)]
pub struct SetJengaBlocksLayout;

impl rosidl_runtime_rs::Service for SetJengaBlocksLayout {
    type Request = SetJengaBlocksLayout_Request;
    type Response = SetJengaBlocksLayout_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__jenga_interfaces__srv__SetJengaBlocksLayout() }
    }
}


