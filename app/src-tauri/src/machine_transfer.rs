use std::{
    collections::HashMap,
    fs::{self, OpenOptions},
    io::Write,
    path::{Component, Path, PathBuf},
    sync::Mutex,
};

use serde::{Deserialize, Serialize};
use tauri::State;
use uuid::Uuid;

#[cfg(windows)]
const DRIVE_REMOVABLE: u32 = 2;

#[derive(Debug, Clone)]
struct DriveRecord {
    root: PathBuf,
    volume_serial: u32,
    info: RemovableDrive,
}

#[derive(Default)]
pub(crate) struct RemovableDriveState {
    drives: Mutex<HashMap<String, DriveRecord>>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct RemovableDrive {
    id: String,
    letter: String,
    volume_name: Option<String>,
    total_bytes: u64,
    free_bytes: u64,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct WritePesRequest {
    drive_id: String,
    relative_directory: String,
    filename: String,
    bytes: Vec<u8>,
    conflict_strategy: ConflictStrategy,
}

#[derive(Debug, Clone, Copy, Deserialize)]
#[serde(rename_all = "snake_case")]
enum ConflictStrategy {
    Ask,
    Replace,
    Rename,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct WritePesResult {
    status: WriteStatus,
    final_path: Option<String>,
    filename: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "snake_case")]
enum WriteStatus {
    Written,
    Conflict,
}

fn invalid_windows_name(value: &str) -> bool {
    if value.is_empty()
        || value.ends_with('.')
        || value.ends_with(' ')
        || value.chars().any(|character| {
            character.is_control() || matches!(character, '<' | '>' | ':' | '"' | '|' | '?' | '*')
        })
    {
        return true;
    }

    let base = value.split('.').next().unwrap_or_default();
    let upper = base.to_ascii_uppercase();
    matches!(upper.as_str(), "CON" | "PRN" | "AUX" | "NUL")
        || (upper.len() == 4
            && (upper.starts_with("COM") || upper.starts_with("LPT"))
            && upper[3..]
                .parse::<u8>()
                .is_ok_and(|number| (1..=9).contains(&number)))
}

fn validate_filename(filename: &str) -> Result<(), String> {
    if filename.len() > 255
        || filename.contains('/')
        || filename.contains('\\')
        || invalid_windows_name(filename)
    {
        return Err("O nome do arquivo retornado pela API não é válido no Windows.".to_string());
    }
    if !Path::new(filename)
        .extension()
        .and_then(|extension| extension.to_str())
        .is_some_and(|extension| extension.eq_ignore_ascii_case("pes"))
    {
        return Err("Somente arquivos .PES podem ser enviados para a máquina.".to_string());
    }
    Ok(())
}

fn validate_relative_directory(value: &str) -> Result<PathBuf, String> {
    let normalized = value.trim().replace('\\', "/");
    if normalized.is_empty() {
        return Ok(PathBuf::new());
    }
    if normalized.starts_with('/')
        || normalized
            .as_bytes()
            .get(1)
            .is_some_and(|character| *character == b':')
    {
        return Err("Informe uma pasta relativa dentro da unidade.".to_string());
    }

    let path = Path::new(&normalized);
    let mut validated = PathBuf::new();
    for component in path.components() {
        let Component::Normal(segment) = component else {
            return Err("A pasta informada contém um caminho inválido.".to_string());
        };
        let segment = segment
            .to_str()
            .ok_or_else(|| "A pasta informada possui caracteres inválidos.".to_string())?;
        if invalid_windows_name(segment) {
            return Err(format!(
                "O nome de pasta “{segment}” não é válido no Windows."
            ));
        }
        validated.push(segment);
    }
    Ok(validated)
}

fn alternative_path(destination: &Path, filename: &str) -> Result<PathBuf, String> {
    let path = Path::new(filename);
    let stem = path
        .file_stem()
        .and_then(|value| value.to_str())
        .ok_or_else(|| "O nome do arquivo não é válido.".to_string())?;
    let extension = path
        .extension()
        .and_then(|value| value.to_str())
        .unwrap_or("PES");

    for sequence in 1..=9_999 {
        let candidate = destination.join(format!("{stem} ({sequence}).{extension}"));
        if !candidate.exists() {
            return Ok(candidate);
        }
    }
    Err("Não foi possível gerar um nome alternativo para o arquivo.".to_string())
}

fn replace_file_safely(temporary: &Path, destination: &Path) -> Result<(), String> {
    if !destination.exists() {
        return fs::rename(temporary, destination)
            .map_err(|_| "Não foi possível finalizar a cópia na unidade.".to_string());
    }

    let backup = destination.with_extension(format!("pes.{}.backup", Uuid::new_v4()));
    fs::rename(destination, &backup)
        .map_err(|_| "O arquivo existente não pôde ser preparado para substituição.".to_string())?;

    match fs::rename(temporary, destination) {
        Ok(()) => {
            let _ = fs::remove_file(backup);
            Ok(())
        }
        Err(_) => {
            let _ = fs::rename(backup, destination);
            Err("A substituição falhou e o arquivo anterior foi preservado.".to_string())
        }
    }
}

fn write_file(record: DriveRecord, request: WritePesRequest) -> Result<WritePesResult, String> {
    validate_filename(&request.filename)?;
    if request.bytes.is_empty() {
        return Err("O arquivo baixado está vazio e não pode ser enviado.".to_string());
    }
    ensure_same_removable_drive(&record.root, record.volume_serial)?;

    let relative_directory = validate_relative_directory(&request.relative_directory)?;
    let canonical_root = record
        .root
        .canonicalize()
        .map_err(|_| "A unidade selecionada não está mais disponível.".to_string())?;
    let directory = canonical_root.join(relative_directory);
    fs::create_dir_all(&directory)
        .map_err(|_| "Não foi possível criar a pasta de destino na unidade.".to_string())?;
    let canonical_directory = directory
        .canonicalize()
        .map_err(|_| "Não foi possível acessar a pasta de destino.".to_string())?;
    if !canonical_directory.starts_with(&canonical_root) {
        return Err("A pasta de destino está fora da unidade selecionada.".to_string());
    }

    let free_bytes = drive_space(&record.root)?.1;
    if request.bytes.len() as u64 > free_bytes {
        return Err("A unidade selecionada não possui espaço livre suficiente.".to_string());
    }

    let original_destination = canonical_directory.join(&request.filename);
    if original_destination.exists() && matches!(request.conflict_strategy, ConflictStrategy::Ask) {
        return Ok(WritePesResult {
            status: WriteStatus::Conflict,
            final_path: None,
            filename: request.filename,
        });
    }

    let destination = if original_destination.exists()
        && matches!(request.conflict_strategy, ConflictStrategy::Rename)
    {
        alternative_path(&canonical_directory, &request.filename)?
    } else {
        original_destination
    };
    let final_filename = destination
        .file_name()
        .and_then(|value| value.to_str())
        .unwrap_or(&request.filename)
        .to_string();
    let temporary =
        canonical_directory.join(format!(".{}.{}.tmp", request.filename, Uuid::new_v4()));

    let write_result = (|| -> Result<(), String> {
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temporary)
            .map_err(|_| "Não foi possível iniciar a escrita na unidade.".to_string())?;
        file.write_all(&request.bytes).map_err(|_| {
            "A unidade foi removida ou ocorreu uma falha durante a escrita.".to_string()
        })?;
        file.sync_all().map_err(|_| {
            "Não foi possível confirmar a gravação do arquivo na unidade.".to_string()
        })?;
        drop(file);

        if matches!(request.conflict_strategy, ConflictStrategy::Replace) {
            replace_file_safely(&temporary, &destination)
        } else {
            fs::rename(&temporary, &destination)
                .map_err(|_| "Não foi possível finalizar a cópia na unidade.".to_string())
        }
    })();

    if write_result.is_err() {
        let _ = fs::remove_file(&temporary);
    }
    write_result?;

    Ok(WritePesResult {
        status: WriteStatus::Written,
        final_path: Some(destination.to_string_lossy().into_owned()),
        filename: final_filename,
    })
}

#[cfg(windows)]
fn wide(value: &str) -> Vec<u16> {
    use std::os::windows::ffi::OsStrExt;
    std::ffi::OsStr::new(value)
        .encode_wide()
        .chain(std::iter::once(0))
        .collect()
}

#[cfg(windows)]
fn ensure_removable_drive(root: &Path) -> Result<(), String> {
    use windows_sys::Win32::Storage::FileSystem::GetDriveTypeW;

    let root = wide(&root.to_string_lossy());
    let drive_type = unsafe { GetDriveTypeW(root.as_ptr()) };
    if drive_type != DRIVE_REMOVABLE {
        return Err(
            "O destino selecionado não está mais disponível como unidade removível.".to_string(),
        );
    }
    Ok(())
}

#[cfg(windows)]
fn volume_information(root: &Path) -> Result<(Option<String>, u32), String> {
    use windows_sys::Win32::Storage::FileSystem::GetVolumeInformationW;

    let root = wide(&root.to_string_lossy());
    let mut volume_buffer = [0_u16; 261];
    let mut volume_serial = 0_u32;
    let success = unsafe {
        GetVolumeInformationW(
            root.as_ptr(),
            volume_buffer.as_mut_ptr(),
            volume_buffer.len() as u32,
            &mut volume_serial,
            std::ptr::null_mut(),
            std::ptr::null_mut(),
            std::ptr::null_mut(),
            0,
        )
    };
    if success == 0 {
        return Err("Não foi possível identificar a unidade removível.".to_string());
    }

    let length = volume_buffer
        .iter()
        .position(|character| *character == 0)
        .unwrap_or(volume_buffer.len());
    let value = String::from_utf16_lossy(&volume_buffer[..length]);
    let volume_name = (!value.trim().is_empty()).then_some(value);
    Ok((volume_name, volume_serial))
}

#[cfg(windows)]
fn ensure_same_removable_drive(root: &Path, expected_serial: u32) -> Result<(), String> {
    ensure_removable_drive(root)?;
    let (_, current_serial) = volume_information(root)?;
    if current_serial != expected_serial {
        return Err(
            "A unidade conectada mudou. Atualize a lista e confirme novamente o destino."
                .to_string(),
        );
    }
    Ok(())
}

#[cfg(not(windows))]
fn ensure_removable_drive(_root: &Path) -> Result<(), String> {
    Err("O envio para máquina está disponível somente no Windows.".to_string())
}

#[cfg(not(windows))]
fn ensure_same_removable_drive(_root: &Path, _expected_serial: u32) -> Result<(), String> {
    Err("O envio para máquina está disponível somente no Windows.".to_string())
}

#[cfg(windows)]
fn drive_space(root: &Path) -> Result<(u64, u64), String> {
    use windows_sys::Win32::Storage::FileSystem::GetDiskFreeSpaceExW;

    let root = wide(&root.to_string_lossy());
    let mut available = 0_u64;
    let mut total = 0_u64;
    let mut total_free = 0_u64;
    let success =
        unsafe { GetDiskFreeSpaceExW(root.as_ptr(), &mut available, &mut total, &mut total_free) };
    if success == 0 {
        return Err("Não foi possível consultar o espaço livre da unidade.".to_string());
    }
    Ok((total, available))
}

#[cfg(not(windows))]
fn drive_space(_root: &Path) -> Result<(u64, u64), String> {
    Err("O envio para máquina está disponível somente no Windows.".to_string())
}

#[cfg(windows)]
fn scan_removable_drives() -> Result<Vec<DriveRecord>, String> {
    use windows_sys::Win32::Storage::FileSystem::{GetDriveTypeW, GetLogicalDrives};

    let mask = unsafe { GetLogicalDrives() };
    if mask == 0 {
        return Err("Não foi possível consultar as unidades conectadas.".to_string());
    }

    let mut drives = Vec::new();
    for index in 0..26_u32 {
        if mask & (1 << index) == 0 {
            continue;
        }
        let letter = (b'A' + index as u8) as char;
        let root_text = format!("{letter}:\\");
        let root_wide = wide(&root_text);
        if unsafe { GetDriveTypeW(root_wide.as_ptr()) } != DRIVE_REMOVABLE {
            continue;
        }

        let Ok((volume_name, volume_serial)) = volume_information(Path::new(&root_text)) else {
            continue;
        };
        let Ok((total_bytes, free_bytes)) = drive_space(Path::new(&root_text)) else {
            continue;
        };
        let id = Uuid::new_v4().to_string();
        let info = RemovableDrive {
            id,
            letter: format!("{letter}:"),
            volume_name,
            total_bytes,
            free_bytes,
        };
        drives.push(DriveRecord {
            root: PathBuf::from(root_text),
            volume_serial,
            info,
        });
    }
    Ok(drives)
}

#[cfg(not(windows))]
fn scan_removable_drives() -> Result<Vec<DriveRecord>, String> {
    Err("O envio para máquina está disponível somente no Windows.".to_string())
}

#[tauri::command]
pub(crate) async fn list_removable_drives(
    state: State<'_, RemovableDriveState>,
) -> Result<Vec<RemovableDrive>, String> {
    let records = tauri::async_runtime::spawn_blocking(scan_removable_drives)
        .await
        .map_err(|_| "Não foi possível concluir a busca por unidades.".to_string())??;
    let response = records.iter().map(|record| record.info.clone()).collect();
    let mapped = records
        .into_iter()
        .map(|record| (record.info.id.clone(), record))
        .collect();
    *state
        .drives
        .lock()
        .map_err(|_| "A lista de unidades não está disponível.".to_string())? = mapped;
    Ok(response)
}

#[tauri::command]
pub(crate) async fn write_pes_to_removable_drive(
    request: WritePesRequest,
    state: State<'_, RemovableDriveState>,
) -> Result<WritePesResult, String> {
    let record = state
        .drives
        .lock()
        .map_err(|_| "A lista de unidades não está disponível.".to_string())?
        .get(&request.drive_id)
        .cloned()
        .ok_or_else(|| {
            "Atualize a lista e selecione novamente a unidade de destino.".to_string()
        })?;

    tauri::async_runtime::spawn_blocking(move || write_file(record, request))
        .await
        .map_err(|_| "Não foi possível concluir o envio para a máquina.".to_string())?
}

#[cfg(test)]
mod tests {
    use super::{
        alternative_path, invalid_windows_name, validate_filename, validate_relative_directory,
    };

    #[test]
    fn validates_windows_paths_and_pes_filename() {
        assert!(validate_relative_directory("").is_ok());
        assert!(validate_relative_directory("Brother/Desenhos").is_ok());
        assert!(validate_relative_directory("../fora").is_err());
        assert!(validate_relative_directory("E:/fora").is_err());
        assert!(invalid_windows_name("CON"));
        assert!(invalid_windows_name("pasta."));
        assert!(validate_filename("flor.PES").is_ok());
        assert!(validate_filename("../flor.PES").is_err());
        assert!(validate_filename("flor.dst").is_err());
    }

    #[test]
    fn generates_an_alternative_filename() {
        let directory = tempfile::tempdir().expect("temporary directory");
        std::fs::write(directory.path().join("flor.PES"), b"pes").expect("existing file");
        let result = alternative_path(directory.path(), "flor.PES").expect("alternative path");
        assert_eq!(
            result.file_name().and_then(|value| value.to_str()),
            Some("flor (1).PES")
        );
    }
}
