#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__msg__JengaBlockState() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__msg__JengaBlockState__init(msg: *mut JengaBlockState) -> bool;
    fn jenga_interfaces__msg__JengaBlockState__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaBlockState>, size: usize) -> bool;
    fn jenga_interfaces__msg__JengaBlockState__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaBlockState>);
    fn jenga_interfaces__msg__JengaBlockState__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaBlockState>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaBlockState>) -> bool;
}

// Corresponds to jenga_interfaces__msg__JengaBlockState
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaBlockState {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_id: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub colour: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub layer: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub layer_position: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::rmw::Pose,

}



impl Default for JengaBlockState {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__msg__JengaBlockState__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__msg__JengaBlockState__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaBlockState {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__msg__JengaBlockState__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__msg__JengaBlockState__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__msg__JengaBlockState__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaBlockState {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaBlockState where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/msg/JengaBlockState";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__msg__JengaBlockState() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__msg__JengaBlockStates() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__msg__JengaBlockStates__init(msg: *mut JengaBlockStates) -> bool;
    fn jenga_interfaces__msg__JengaBlockStates__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaBlockStates>, size: usize) -> bool;
    fn jenga_interfaces__msg__JengaBlockStates__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaBlockStates>);
    fn jenga_interfaces__msg__JengaBlockStates__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaBlockStates>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaBlockStates>) -> bool;
}

// Corresponds to jenga_interfaces__msg__JengaBlockStates
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaBlockStates {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub blocks: rosidl_runtime_rs::Sequence<super::super::msg::rmw::JengaBlockState>,

}



impl Default for JengaBlockStates {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__msg__JengaBlockStates__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__msg__JengaBlockStates__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaBlockStates {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__msg__JengaBlockStates__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__msg__JengaBlockStates__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__msg__JengaBlockStates__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaBlockStates {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaBlockStates where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/msg/JengaBlockStates";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__msg__JengaBlockStates() }
  }
}


