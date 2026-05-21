#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__ProtrudeJengaBlock_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Request__init(msg: *mut ProtrudeJengaBlock_Request) -> bool;
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Request>, size: usize) -> bool;
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Request>);
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Request>) -> bool;
}

// Corresponds to jenga_interfaces__srv__ProtrudeJengaBlock_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
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
    pub axis: rosidl_runtime_rs::String,

}



impl Default for ProtrudeJengaBlock_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__srv__ProtrudeJengaBlock_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__srv__ProtrudeJengaBlock_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ProtrudeJengaBlock_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__ProtrudeJengaBlock_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ProtrudeJengaBlock_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ProtrudeJengaBlock_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/srv/ProtrudeJengaBlock_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__ProtrudeJengaBlock_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__ProtrudeJengaBlock_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Response__init(msg: *mut ProtrudeJengaBlock_Response) -> bool;
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Response>, size: usize) -> bool;
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Response>);
    fn jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ProtrudeJengaBlock_Response>) -> bool;
}

// Corresponds to jenga_interfaces__srv__ProtrudeJengaBlock_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ProtrudeJengaBlock_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

}



impl Default for ProtrudeJengaBlock_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__srv__ProtrudeJengaBlock_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__srv__ProtrudeJengaBlock_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ProtrudeJengaBlock_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__ProtrudeJengaBlock_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ProtrudeJengaBlock_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ProtrudeJengaBlock_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/srv/ProtrudeJengaBlock_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__ProtrudeJengaBlock_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__SetJengaBlocksLayout_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Request__init(msg: *mut SetJengaBlocksLayout_Request) -> bool;
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Request>, size: usize) -> bool;
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Request>);
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Request>) -> bool;
}

// Corresponds to jenga_interfaces__srv__SetJengaBlocksLayout_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetJengaBlocksLayout_Request {
    /// empty = all blocks
    pub block_indices: rosidl_runtime_rs::Sequence<u32>,

    /// "stock" | "tower"
    pub target_layout: rosidl_runtime_rs::String,

}



impl Default for SetJengaBlocksLayout_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__srv__SetJengaBlocksLayout_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__srv__SetJengaBlocksLayout_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SetJengaBlocksLayout_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__SetJengaBlocksLayout_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SetJengaBlocksLayout_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SetJengaBlocksLayout_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/srv/SetJengaBlocksLayout_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__SetJengaBlocksLayout_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__SetJengaBlocksLayout_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Response__init(msg: *mut SetJengaBlocksLayout_Response) -> bool;
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Response>, size: usize) -> bool;
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Response>);
    fn jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<SetJengaBlocksLayout_Response>) -> bool;
}

// Corresponds to jenga_interfaces__srv__SetJengaBlocksLayout_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetJengaBlocksLayout_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

}



impl Default for SetJengaBlocksLayout_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__srv__SetJengaBlocksLayout_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__srv__SetJengaBlocksLayout_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SetJengaBlocksLayout_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__srv__SetJengaBlocksLayout_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SetJengaBlocksLayout_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SetJengaBlocksLayout_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/srv/SetJengaBlocksLayout_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__srv__SetJengaBlocksLayout_Response() }
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


