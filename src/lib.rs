use pyo3::prelude::*;
use frost_secp256k1::{keys};
use frost_secp256k1::rand_core::OsRng;
use serde::Serialize;
use base64::{engine::general_purpose, Engine};
use serde_json;

#[derive(Serialize)]
struct SerializableShare {
    participant_id: u16,
    share: String,
}

#[pyfunction]
fn generate_keys_py(n: u16, t: u16) -> PyResult<String> {
    // Generate the shares and group key
    let (shares_map, _group_key) = keys::generate_with_dealer(n, t, &mut OsRng)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Keygen failed: {e}")))?;

    // Serialize the shares for output
    let result: Vec<SerializableShare> = shares_map
    .into_iter()
    .enumerate() // Assign unique index to each participant
    .map(|(index, (identifier, share))| {
        let pid: u16 = index as u16 + 1; // Participant IDs start from 1
        let encoded = serde_json::to_string(&share) // Serialize `SecretShare` to JSON
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {e}")))
            .unwrap();
        SerializableShare {
            participant_id: pid,
            share: encoded,
        }
    })
    .collect();


    // Convert the result to JSON format
    let json = serde_json::to_string_pretty(&result)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {e}")))?;

    Ok(json)
}

#[pymodule]
fn frostpy(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_keys_py, m)?)?;
    Ok(())
}