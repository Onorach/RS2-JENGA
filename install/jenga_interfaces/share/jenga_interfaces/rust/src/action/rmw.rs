
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_Goal() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_Goal__init(msg: *mut JengaPickPlace_Goal) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_Goal__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Goal>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_Goal__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Goal>);
    fn jenga_interfaces__action__JengaPickPlace_Goal__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_Goal>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Goal>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_Goal
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pick_pose: geometry_msgs::msg::rmw::PoseStamped,


    // This member is not documented.
    #[allow(missing_docs)]
    pub place_pose: geometry_msgs::msg::rmw::PoseStamped,

}



impl Default for JengaPickPlace_Goal {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_Goal__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_Goal__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_Goal {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Goal__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Goal__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Goal__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_Goal {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_Goal where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_Goal";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_Goal() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_Result() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_Result__init(msg: *mut JengaPickPlace_Result) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_Result__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Result>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_Result__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Result>);
    fn jenga_interfaces__action__JengaPickPlace_Result__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_Result>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Result>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_Result
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaPickPlace_Result {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_Result__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_Result__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_Result {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Result__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Result__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Result__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_Result {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_Result where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_Result";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_Result() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_Feedback() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_Feedback__init(msg: *mut JengaPickPlace_Feedback) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_Feedback__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Feedback>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_Feedback__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Feedback>);
    fn jenga_interfaces__action__JengaPickPlace_Feedback__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_Feedback>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_Feedback>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_Feedback
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaPickPlace_Feedback {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_Feedback__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_Feedback__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_Feedback {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Feedback__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Feedback__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_Feedback__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_Feedback {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_Feedback where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_Feedback";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_Feedback() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_FeedbackMessage() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_FeedbackMessage__init(msg: *mut JengaPickPlace_FeedbackMessage) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_FeedbackMessage>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_FeedbackMessage>);
    fn jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_FeedbackMessage>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_FeedbackMessage>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_FeedbackMessage
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::super::action::rmw::JengaPickPlace_Feedback,

}



impl Default for JengaPickPlace_FeedbackMessage {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_FeedbackMessage__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_FeedbackMessage__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_FeedbackMessage {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_FeedbackMessage__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_FeedbackMessage {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_FeedbackMessage where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_FeedbackMessage";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_FeedbackMessage() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_Goal() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_Goal__init(msg: *mut JengaArmReady_Goal) -> bool;
    fn jenga_interfaces__action__JengaArmReady_Goal__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Goal>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_Goal__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Goal>);
    fn jenga_interfaces__action__JengaArmReady_Goal__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_Goal>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Goal>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_Goal
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub target_state: rosidl_runtime_rs::String,

}



impl Default for JengaArmReady_Goal {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_Goal__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_Goal__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_Goal {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Goal__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Goal__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Goal__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_Goal {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_Goal where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_Goal";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_Goal() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_Result() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_Result__init(msg: *mut JengaArmReady_Result) -> bool;
    fn jenga_interfaces__action__JengaArmReady_Result__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Result>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_Result__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Result>);
    fn jenga_interfaces__action__JengaArmReady_Result__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_Result>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Result>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_Result
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaArmReady_Result {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_Result__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_Result__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_Result {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Result__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Result__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Result__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_Result {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_Result where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_Result";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_Result() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_Feedback() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_Feedback__init(msg: *mut JengaArmReady_Feedback) -> bool;
    fn jenga_interfaces__action__JengaArmReady_Feedback__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Feedback>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_Feedback__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Feedback>);
    fn jenga_interfaces__action__JengaArmReady_Feedback__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_Feedback>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_Feedback>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_Feedback
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaArmReady_Feedback {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_Feedback__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_Feedback__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_Feedback {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Feedback__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Feedback__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_Feedback__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_Feedback {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_Feedback where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_Feedback";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_Feedback() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_FeedbackMessage() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_FeedbackMessage__init(msg: *mut JengaArmReady_FeedbackMessage) -> bool;
    fn jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_FeedbackMessage>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_FeedbackMessage>);
    fn jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_FeedbackMessage>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_FeedbackMessage>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_FeedbackMessage
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::super::action::rmw::JengaArmReady_Feedback,

}



impl Default for JengaArmReady_FeedbackMessage {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_FeedbackMessage__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_FeedbackMessage__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_FeedbackMessage {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_FeedbackMessage__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_FeedbackMessage {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_FeedbackMessage where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_FeedbackMessage";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_FeedbackMessage() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_Goal() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_Goal__init(msg: *mut JengaExtractSideBlock_Goal) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Goal>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Goal>);
    fn jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Goal>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Goal>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_Goal
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub block_pose: geometry_msgs::msg::rmw::PoseStamped,


    // This member is not documented.
    #[allow(missing_docs)]
    pub place_pose: geometry_msgs::msg::rmw::PoseStamped,

}



impl Default for JengaExtractSideBlock_Goal {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_Goal__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_Goal__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_Goal {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Goal__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_Goal {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_Goal where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_Goal";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_Goal() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_Result() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_Result__init(msg: *mut JengaExtractSideBlock_Result) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Result>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Result>);
    fn jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Result>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Result>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_Result
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaExtractSideBlock_Result {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_Result__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_Result__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_Result {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Result__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_Result {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_Result where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_Result";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_Result() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_Feedback() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_Feedback__init(msg: *mut JengaExtractSideBlock_Feedback) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Feedback>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Feedback>);
    fn jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Feedback>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_Feedback>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_Feedback
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaExtractSideBlock_Feedback {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_Feedback__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_Feedback__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_Feedback {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_Feedback__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_Feedback {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_Feedback where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_Feedback";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_Feedback() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__init(msg: *mut JengaExtractSideBlock_FeedbackMessage) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_FeedbackMessage>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_FeedbackMessage>);
    fn jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_FeedbackMessage>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_FeedbackMessage>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::super::action::rmw::JengaExtractSideBlock_Feedback,

}



impl Default for JengaExtractSideBlock_FeedbackMessage {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_FeedbackMessage {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_FeedbackMessage {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_FeedbackMessage where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_FeedbackMessage";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_FeedbackMessage() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_Goal() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Goal__init(msg: *mut JengaExtractMiddleBlock_Goal) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Goal>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Goal>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Goal>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Goal>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_Goal
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub block_pose: geometry_msgs::msg::rmw::PoseStamped,


    // This member is not documented.
    #[allow(missing_docs)]
    pub place_pose: geometry_msgs::msg::rmw::PoseStamped,

    /// e.g. "x", "-x". Empty string → auto-detect from planning scene; explicit string → override.
    pub extract_axis: rosidl_runtime_rs::String,

}



impl Default for JengaExtractMiddleBlock_Goal {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_Goal__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_Goal__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_Goal {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Goal__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_Goal {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_Goal where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_Goal";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_Goal() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_Result() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Result__init(msg: *mut JengaExtractMiddleBlock_Result) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Result>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Result>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Result>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Result>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_Result
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_code: u8,

}



impl Default for JengaExtractMiddleBlock_Result {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_Result__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_Result__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_Result {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Result__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_Result {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_Result where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_Result";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_Result() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_Feedback() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__init(msg: *mut JengaExtractMiddleBlock_Feedback) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Feedback>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Feedback>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Feedback>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_Feedback>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_Feedback
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaExtractMiddleBlock_Feedback {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_Feedback {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_Feedback__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_Feedback {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_Feedback where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_Feedback";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_Feedback() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__init(msg: *mut JengaExtractMiddleBlock_FeedbackMessage) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_FeedbackMessage>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_FeedbackMessage>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_FeedbackMessage>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_FeedbackMessage>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::super::action::rmw::JengaExtractMiddleBlock_Feedback,

}



impl Default for JengaExtractMiddleBlock_FeedbackMessage {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_FeedbackMessage {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_FeedbackMessage {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_FeedbackMessage where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_FeedbackMessage";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_FeedbackMessage() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_Goal() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_Goal__init(msg: *mut JengaProbeBlock_Goal) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_Goal__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Goal>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_Goal__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Goal>);
    fn jenga_interfaces__action__JengaProbeBlock_Goal__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_Goal>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Goal>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_Goal
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub block_index: u32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub block_pose: geometry_msgs::msg::rmw::PoseStamped,

}



impl Default for JengaProbeBlock_Goal {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_Goal__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_Goal__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_Goal {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Goal__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Goal__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Goal__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_Goal {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_Goal where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_Goal";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_Goal() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_Result() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_Result__init(msg: *mut JengaProbeBlock_Result) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_Result__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Result>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_Result__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Result>);
    fn jenga_interfaces__action__JengaProbeBlock_Result__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_Result>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Result>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_Result
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,


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
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_Result__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_Result__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_Result {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Result__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Result__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Result__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_Result {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_Result where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_Result";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_Result() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_Feedback() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_Feedback__init(msg: *mut JengaProbeBlock_Feedback) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Feedback>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Feedback>);
    fn jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_Feedback>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_Feedback>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_Feedback
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub current_stage: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress_pct: f32,

}



impl Default for JengaProbeBlock_Feedback {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_Feedback__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_Feedback__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_Feedback {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_Feedback__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_Feedback {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_Feedback where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_Feedback";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_Feedback() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_FeedbackMessage() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__init(msg: *mut JengaProbeBlock_FeedbackMessage) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_FeedbackMessage>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_FeedbackMessage>);
    fn jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_FeedbackMessage>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_FeedbackMessage>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_FeedbackMessage
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::super::action::rmw::JengaProbeBlock_Feedback,

}



impl Default for JengaProbeBlock_FeedbackMessage {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_FeedbackMessage {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_FeedbackMessage__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_FeedbackMessage {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_FeedbackMessage where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_FeedbackMessage";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_FeedbackMessage() }
  }
}




#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_SendGoal_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Request__init(msg: *mut JengaPickPlace_SendGoal_Request) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Request>);
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_SendGoal_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::super::action::rmw::JengaPickPlace_Goal,

}



impl Default for JengaPickPlace_SendGoal_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_SendGoal_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_SendGoal_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_SendGoal_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_SendGoal_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_SendGoal_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_SendGoal_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_SendGoal_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_SendGoal_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_SendGoal_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Response__init(msg: *mut JengaPickPlace_SendGoal_Response) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Response>);
    fn jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_SendGoal_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_SendGoal_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,

}



impl Default for JengaPickPlace_SendGoal_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_SendGoal_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_SendGoal_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_SendGoal_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_SendGoal_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_SendGoal_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_SendGoal_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_SendGoal_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_SendGoal_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_GetResult_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Request__init(msg: *mut JengaPickPlace_GetResult_Request) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Request>);
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_GetResult_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,

}



impl Default for JengaPickPlace_GetResult_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_GetResult_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_GetResult_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_GetResult_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_GetResult_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_GetResult_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_GetResult_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_GetResult_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_GetResult_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_GetResult_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Response__init(msg: *mut JengaPickPlace_GetResult_Response) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Response>);
    fn jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaPickPlace_GetResult_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaPickPlace_GetResult_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaPickPlace_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::action::rmw::JengaPickPlace_Result,

}



impl Default for JengaPickPlace_GetResult_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaPickPlace_GetResult_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaPickPlace_GetResult_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaPickPlace_GetResult_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaPickPlace_GetResult_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaPickPlace_GetResult_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaPickPlace_GetResult_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaPickPlace_GetResult_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaPickPlace_GetResult_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_SendGoal_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Request__init(msg: *mut JengaArmReady_SendGoal_Request) -> bool;
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Request>);
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_SendGoal_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::super::action::rmw::JengaArmReady_Goal,

}



impl Default for JengaArmReady_SendGoal_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_SendGoal_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_SendGoal_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_SendGoal_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_SendGoal_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_SendGoal_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_SendGoal_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_SendGoal_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_SendGoal_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_SendGoal_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Response__init(msg: *mut JengaArmReady_SendGoal_Response) -> bool;
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Response>);
    fn jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_SendGoal_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_SendGoal_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,

}



impl Default for JengaArmReady_SendGoal_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_SendGoal_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_SendGoal_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_SendGoal_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_SendGoal_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_SendGoal_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_SendGoal_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_SendGoal_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_SendGoal_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_GetResult_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_GetResult_Request__init(msg: *mut JengaArmReady_GetResult_Request) -> bool;
    fn jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Request>);
    fn jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_GetResult_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,

}



impl Default for JengaArmReady_GetResult_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_GetResult_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_GetResult_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_GetResult_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_GetResult_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_GetResult_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_GetResult_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_GetResult_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_GetResult_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_GetResult_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaArmReady_GetResult_Response__init(msg: *mut JengaArmReady_GetResult_Response) -> bool;
    fn jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Response>);
    fn jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaArmReady_GetResult_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaArmReady_GetResult_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaArmReady_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::action::rmw::JengaArmReady_Result,

}



impl Default for JengaArmReady_GetResult_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaArmReady_GetResult_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaArmReady_GetResult_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaArmReady_GetResult_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaArmReady_GetResult_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaArmReady_GetResult_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaArmReady_GetResult_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaArmReady_GetResult_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaArmReady_GetResult_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__init(msg: *mut JengaExtractSideBlock_SendGoal_Request) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Request>);
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::super::action::rmw::JengaExtractSideBlock_Goal,

}



impl Default for JengaExtractSideBlock_SendGoal_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_SendGoal_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_SendGoal_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_SendGoal_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_SendGoal_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__init(msg: *mut JengaExtractSideBlock_SendGoal_Response) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Response>);
    fn jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_SendGoal_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,

}



impl Default for JengaExtractSideBlock_SendGoal_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_SendGoal_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_SendGoal_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_SendGoal_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_SendGoal_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_SendGoal_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__init(msg: *mut JengaExtractSideBlock_GetResult_Request) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Request>);
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,

}



impl Default for JengaExtractSideBlock_GetResult_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_GetResult_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_GetResult_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_GetResult_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_GetResult_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_GetResult_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__init(msg: *mut JengaExtractSideBlock_GetResult_Response) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Response>);
    fn jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractSideBlock_GetResult_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractSideBlock_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::action::rmw::JengaExtractSideBlock_Result,

}



impl Default for JengaExtractSideBlock_GetResult_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractSideBlock_GetResult_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractSideBlock_GetResult_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractSideBlock_GetResult_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractSideBlock_GetResult_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractSideBlock_GetResult_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__init(msg: *mut JengaExtractMiddleBlock_SendGoal_Request) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Request>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::super::action::rmw::JengaExtractMiddleBlock_Goal,

}



impl Default for JengaExtractMiddleBlock_SendGoal_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_SendGoal_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_SendGoal_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_SendGoal_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_SendGoal_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__init(msg: *mut JengaExtractMiddleBlock_SendGoal_Response) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Response>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_SendGoal_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,

}



impl Default for JengaExtractMiddleBlock_SendGoal_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_SendGoal_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_SendGoal_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_SendGoal_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_SendGoal_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_SendGoal_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__init(msg: *mut JengaExtractMiddleBlock_GetResult_Request) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Request>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,

}



impl Default for JengaExtractMiddleBlock_GetResult_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_GetResult_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_GetResult_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_GetResult_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_GetResult_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__init(msg: *mut JengaExtractMiddleBlock_GetResult_Response) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Response>);
    fn jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaExtractMiddleBlock_GetResult_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaExtractMiddleBlock_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::action::rmw::JengaExtractMiddleBlock_Result,

}



impl Default for JengaExtractMiddleBlock_GetResult_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaExtractMiddleBlock_GetResult_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaExtractMiddleBlock_GetResult_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaExtractMiddleBlock_GetResult_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaExtractMiddleBlock_GetResult_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaExtractMiddleBlock_GetResult_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_SendGoal_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__init(msg: *mut JengaProbeBlock_SendGoal_Request) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Request>);
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_SendGoal_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::super::action::rmw::JengaProbeBlock_Goal,

}



impl Default for JengaProbeBlock_SendGoal_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_SendGoal_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_SendGoal_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_SendGoal_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_SendGoal_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_SendGoal_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_SendGoal_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_SendGoal_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__init(msg: *mut JengaProbeBlock_SendGoal_Response) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Response>);
    fn jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_SendGoal_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_SendGoal_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,

}



impl Default for JengaProbeBlock_SendGoal_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_SendGoal_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_SendGoal_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_SendGoal_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_SendGoal_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_SendGoal_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_SendGoal_Response() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_GetResult_Request() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Request__init(msg: *mut JengaProbeBlock_GetResult_Request) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Request>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Request>);
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Request>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_GetResult_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,

}



impl Default for JengaProbeBlock_GetResult_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_GetResult_Request__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_GetResult_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_GetResult_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_GetResult_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_GetResult_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_GetResult_Request where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_GetResult_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_GetResult_Request() }
  }
}


#[link(name = "jenga_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_GetResult_Response() -> *const std::ffi::c_void;
}

#[link(name = "jenga_interfaces__rosidl_generator_c")]
extern "C" {
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Response__init(msg: *mut JengaProbeBlock_GetResult_Response) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Response>, size: usize) -> bool;
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Response>);
    fn jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<JengaProbeBlock_GetResult_Response>) -> bool;
}

// Corresponds to jenga_interfaces__action__JengaProbeBlock_GetResult_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct JengaProbeBlock_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::action::rmw::JengaProbeBlock_Result,

}



impl Default for JengaProbeBlock_GetResult_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !jenga_interfaces__action__JengaProbeBlock_GetResult_Response__init(&mut msg as *mut _) {
        panic!("Call to jenga_interfaces__action__JengaProbeBlock_GetResult_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for JengaProbeBlock_GetResult_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { jenga_interfaces__action__JengaProbeBlock_GetResult_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for JengaProbeBlock_GetResult_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for JengaProbeBlock_GetResult_Response where Self: Sized {
  const TYPE_NAME: &'static str = "jenga_interfaces/action/JengaProbeBlock_GetResult_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__jenga_interfaces__action__JengaProbeBlock_GetResult_Response() }
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


