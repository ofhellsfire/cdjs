use std::collections::HashMap;
use std::os::raw::c_char;

use pyo3::AsPyPointer;
use pyo3::{exceptions, wrap_pyfunction};
use pyo3::exceptions::PyValueError;
use pyo3::ffi::*;
use pyo3::prelude::*;
use pyo3::types::{PyDateTime, PyDateAccess, PyTimeAccess};

type Num = i32;

struct TzInfo {
    offset_day: Num,
    offset_second: Num,
}

impl TzInfo {
    fn empty() -> TzInfo {
        TzInfo {
            offset_day: 0,
            offset_second: 0,
        }
    }
    fn has_tz(&self) -> bool {
        self.offset_day != 0 || self.offset_second != 0
    }
}

fn get_tzinfo(date: &PyDateTime) -> PyResult<TzInfo> {
    let has_tz = unsafe { 
        (*(date.as_ptr() as *mut pyo3::ffi::PyDateTime_DateTime)).hastzinfo == 1
    };
    if !has_tz {
        return Ok(TzInfo::empty());
    }
    let offset_day: i32;
    let offset_second: i32;
    let tzinfo = ffi!(PyDateTime_DATE_GET_TZINFO(date.as_ptr()));
    if ffi!(PyObject_HasAttr(tzinfo, PyUnicode_InternFromString("convert\0".as_ptr() as *const c_char))) == 1 {
        // pendulum
        let offset = call_method!(date.as_ptr(), PyUnicode_InternFromString("utcoffset\0".as_ptr() as *const c_char));
        offset_second = ffi!(PyDateTime_DELTA_GET_SECONDS(offset)) as i32;
        offset_day = ffi!(PyDateTime_DELTA_GET_DAYS(offset));
    } else if ffi!(PyObject_HasAttr(tzinfo, PyUnicode_InternFromString("normalize\0".as_ptr() as *const c_char))) == 1 {
        // pytz
        let method_ptr = call_method!(tzinfo, PyUnicode_InternFromString("normalize\0".as_ptr() as *const c_char), date.as_ptr());
        let offset = call_method!(method_ptr, PyUnicode_InternFromString("utcoffset\0".as_ptr() as *const c_char));
        offset_second = ffi!(PyDateTime_DELTA_GET_SECONDS(offset)) as i32;
        offset_day = ffi!(PyDateTime_DELTA_GET_DAYS(offset));
    } else if ffi!(PyObject_HasAttr(tzinfo, PyUnicode_InternFromString("dst\0".as_ptr() as *const c_char))) == 1 {
        // dateutil/arrow, datetime.timezone.utc
        let offset = call_method!(tzinfo, PyUnicode_InternFromString("utcoffset\0".as_ptr() as *const c_char), date.as_ptr());
        offset_second = ffi!(PyDateTime_DELTA_GET_SECONDS(offset)) as i32;
        offset_day = ffi!(PyDateTime_DELTA_GET_DAYS(offset));
    } else {
        return Err(PyErr::new::<exceptions::PyTypeError, _>("Unsupported Library"));
    }
    Ok(TzInfo {
        offset_day: offset_day,
        offset_second: offset_second,
    })
}

fn update_ms_tail(tail: &mut String, us: Num, has_tz: bool, is_epoch_aware: bool) {
    let ms = us / 1000;
    if ms != 0 || !is_epoch_aware {
        let s = format!(".{:03}", ms);
        tail.push_str(&s);
    }
    if !has_tz {
        tail.push_str("Z");
    }
}

fn update_tz_tail(tail: &mut String, tzinfo: &TzInfo) {
    let mut offset_minute = tzinfo.offset_second / 60;
    let mut offset_hour = offset_minute / 60;
    if tzinfo.offset_day >= 0 {
        tail.push_str("+");
    } else {
        offset_minute = (86400 - tzinfo.offset_second) / 60;
        offset_hour = offset_minute / 60;
        tail.push_str("-");
    }
    let s = format!("{:02}{:02}", offset_hour, offset_minute % 60);
    tail.push_str(&s);
}

#[pyfunction]
fn serialize_date(date_obj: &PyDateTime) -> PyResult<HashMap<String, String>> {
    let is_epoch_aware = date_obj.get_year() >= 1970;
    let tzinfo = get_tzinfo(&date_obj)?;
    if  !is_epoch_aware && tzinfo.has_tz() {
        return Err(PyValueError::new_err(
            "Module does not support year less than 1970 with tzinfo"
        ));
    }
    let us = date_obj.get_microsecond();
    let mut tail = String::new();
    update_ms_tail(&mut tail, us as Num, tzinfo.has_tz(), is_epoch_aware);
    if tzinfo.has_tz() {
        update_tz_tail(&mut tail, &tzinfo);
    }
    let mut result: HashMap<_, _> = HashMap::new();
    result.insert(
        "$date".to_string(),
        format!("{}-{:02}-{:02}T{:02}:{:02}:{:02}{}",
                date_obj.get_year(),
                date_obj.get_month(),
                date_obj.get_day(),
                date_obj.get_hour(),
                date_obj.get_minute(),
                date_obj.get_second(),
                tail)
    );

    Ok(result)
}

#[pyfunction]
fn do_nothing(_date_obj: &PyDateTime) -> PyResult<String> {
    Ok(String::from("{}"))
}

#[pymodule]
fn cdjs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(serialize_date, m)?)?;
    m.add_function(wrap_pyfunction!(do_nothing, m)?)?;

    Ok(())
}

#[macro_export]
macro_rules! ffi {
    ($fn:ident()) => {
        unsafe { pyo3::ffi::$fn() }
    };

    ($fn:ident($obj1:expr)) => {
        unsafe { pyo3::ffi::$fn($obj1) }
    };

    ($fn:ident($obj1:expr, $obj2:expr)) => {
        unsafe { pyo3::ffi::$fn($obj1, $obj2) }
    };

    ($fn:ident($obj1:expr, $obj2:expr, $obj3:expr)) => {
        unsafe { pyo3::ffi::$fn($obj1, $obj2, $obj3) }
    };

    ($fn:ident($obj1:expr, $obj2:expr, $obj3:expr, $obj4:expr)) => {
        unsafe { pyo3::ffi::$fn($obj1, $obj2, $obj3, $obj4) }
    };
}

#[macro_export]
macro_rules! call_method {
    ($obj1:expr, $obj2:expr) => {
        unsafe {
            pyo3::ffi::PyObject_CallMethodObjArgs(
                $obj1,
                $obj2,
                std::ptr::null_mut() as *mut pyo3::ffi::PyObject,
            )
        }
    };
    ($obj1:expr, $obj2:expr, $obj3:expr) => {
        unsafe {
            pyo3::ffi::PyObject_CallMethodObjArgs(
                $obj1,
                $obj2,
                $obj3,
                std::ptr::null_mut() as *mut pyo3::ffi::PyObject,
            )
        }
    };
}
