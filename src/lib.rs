use pyo3::prelude::*;
use frost_core::{SigningPackage, Identifier};
use frost_core::keys::{generate_with_dealer, KeyPackage, PublicKeyPackage, IdentifierList, SigningShare, VerifyingShare};
use frost_core::round1;
use frost_core::round2;
use frost_secp256k1::Secp256K1Sha256;
use frost_core::{aggregate, VerifyingKey, Signature};
use rand::thread_rng;
use serde_json;
use base64::{engine::general_purpose, Engine};
use std::collections::BTreeMap;
use hex;
use std::num::NonZeroU16;

#[pyfunction]
fn generate_keys_py(n: u16, t: u16) -> PyResult<String> {
    let mut rng = thread_rng();
    let identifiers: Vec<Identifier<Secp256K1Sha256>> = (1..=n)
        .map(|i| Identifier::<Secp256K1Sha256>::try_from(i).unwrap())
        .collect();
    let identifier_list = IdentifierList::Custom(&identifiers);

    let (shares_map, pubkey_package) = generate_with_dealer(n.into(), t.into(), identifier_list, &mut rng)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Key generation failed: {e}")))?;

    let group_public_key_b64 = general_purpose::STANDARD.encode(
        pubkey_package.serialize()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {e}")))?
    );

    let group_verifying_key_b64 = general_purpose::STANDARD.encode(
        pubkey_package.verifying_key().serialize()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {e}")))?
    );

    let shares: Vec<serde_json::Value> = shares_map
        .into_iter()
        .enumerate()
        .map(|(index, (id, secret_share))| {
            let verifying_key_bytes = pubkey_package.verifying_key().serialize()
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {e}")));
            match verifying_key_bytes {
                Ok(bytes) => serde_json::json!({
                    "participant_id": index + 1,
                    "share": {
                        "header": {
                            "version": 0,
                            "ciphersuite": "FROST-secp256k1-SHA256-v1"
                        },
                        "identifier": hex::encode(id.serialize()),
                        "signing_share": hex::encode(secret_share.signing_share().serialize()),
                        "verifying_key": hex::encode(bytes),
                        "min_signers": t  // Already correct, included in JSON
                    }
                }),
                Err(e) => serde_json::json!({"error": e.to_string()}),
            }
        })
        .collect();

    let output_json = serde_json::json!({
        "shares": shares,
        "group_public_key": group_public_key_b64,
        "group_verifying_key": group_verifying_key_b64
    });

    serde_json::to_string_pretty(&output_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON formatting error: {e}")))
}

#[pyfunction]
fn sign_message_py(message: String, shares_json: String, threshold: u16, pubkey_package_json: String) -> PyResult<(String, String)> {
    let shares_data: Vec<serde_json::Value> = serde_json::from_str(&shares_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Share deserialization error: {e}")))?;
    let pubkey_package: PublicKeyPackage<Secp256K1Sha256> = {
        let bytes = general_purpose::STANDARD
            .decode(&pubkey_package_json)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Pubkey package decode error: {e}")))?;
        PublicKeyPackage::deserialize(&bytes)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Pubkey package deserialization error: {e}")))?
    };

    let shares: Vec<KeyPackage<Secp256K1Sha256>> = shares_data
        .iter()
        .map(|share_data| {
            let share = share_data.as_object()
                .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid share format"))?;
            let identifier = Identifier::<Secp256K1Sha256>::deserialize(
                &hex::decode(share["identifier"].as_str().unwrap())
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Hex decode error: {e}")))?
            ).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Identifier deserialize error: {e}")))?;
            let signing_share = SigningShare::<Secp256K1Sha256>::deserialize(
                &hex::decode(share["signing_share"].as_str().unwrap())
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Hex decode error: {e}")))?
            ).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Signing share deserialize error: {e}")))?;
            let verifying_key = VerifyingKey::<Secp256K1Sha256>::deserialize(
                &hex::decode(share["verifying_key"].as_str().unwrap())
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Hex decode error: {e}")))?
            ).map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Verifying key deserialize error: {e}")))?;
            let min_signers = NonZeroU16::new(
                share["min_signers"].as_u64().unwrap() as u16  // Use min_signers from JSON
            ).ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid min_signers"))?;

            let verifying_share = VerifyingShare::from(signing_share);

            Ok(KeyPackage::new(identifier, signing_share, verifying_share, verifying_key, min_signers.get()))
        })
        .collect::<Result<Vec<_>, PyErr>>()?;

    // Enforce original threshold from key packages
    let original_min_signers = shares[0].min_signers();
    if threshold < *original_min_signers {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Threshold too low: provided {}, required at least {} from key generation", threshold, original_min_signers)
        ));
    }

    if shares.len() < threshold as usize {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Insufficient shares: got {}, need at least {}", shares.len(), threshold)
        ));
    }

    let mut rng = thread_rng();
    let mut commitments_map = BTreeMap::new();
    let mut nonces_map = BTreeMap::new();

    for share in &shares {
        let (nonces, commitments) = round1::commit(share.signing_share(), &mut rng);
        commitments_map.insert(*share.identifier(), commitments);
        nonces_map.insert(*share.identifier(), nonces);
    }

    let signing_package = SigningPackage::new(commitments_map, message.as_bytes());

    let mut partial_signatures = BTreeMap::new();
    for share in &shares {
        let nonce = nonces_map.get(share.identifier()).unwrap();
        let signature = round2::sign(&signing_package, nonce, share)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Signing error: {e}")))?;
        partial_signatures.insert(*share.identifier(), signature);
    }

    let signature = aggregate(&signing_package, &partial_signatures, &pubkey_package)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Aggregation error: {e}")))?;

    let verifying_key = pubkey_package.verifying_key();
    if verifying_key.verify(message.as_bytes(), &signature).is_err() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Generated signature is invalid"));
    }

    let signature_bytes = signature.serialize()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Serialization error: {e}")))?;
    let signature_b64 = general_purpose::STANDARD.encode(signature_bytes);
    Ok((signature_b64, message))
}

#[pyfunction]
fn verify_signature_py(message: String, signature_b64: String, public_key_b64: String) -> PyResult<bool> {
    let signature_bytes = general_purpose::STANDARD
        .decode(signature_b64)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Signature decode error: {e}")))?;

    let public_key_bytes = general_purpose::STANDARD
        .decode(public_key_b64)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Public key decode error: {e}")))?;

    let signature = Signature::<Secp256K1Sha256>::deserialize(&signature_bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Signature parse error: {e}")))?;
    let public_key = VerifyingKey::<Secp256K1Sha256>::deserialize(&public_key_bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Public key parse error: {e}")))?;

    let is_valid = public_key.verify(message.as_bytes(), &signature).is_ok();
    Ok(is_valid)
}

// [Rest of the file unchanged]

#[pymodule]
fn frostpy(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_keys_py, m)?)?;
    m.add_function(wrap_pyfunction!(sign_message_py, m)?)?;
    m.add_function(wrap_pyfunction!(verify_signature_py, m)?)?;
    Ok(())
}