use std::{
    collections::HashMap,
    fs::File,
    path::{Path, PathBuf},
    sync::Mutex,
};

use serde::Serialize;
use tauri::{AppHandle, State};
use tauri_plugin_dialog::DialogExt;
use uuid::Uuid;
use walkdir::WalkDir;

#[derive(Default)]
struct SelectedDirectoryState {
    files: Mutex<HashMap<String, PathBuf>>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct PesFileEntry {
    id: String,
    name: String,
    relative_path: String,
    size: u64,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct DirectorySelection {
    folder_name: String,
    files: Vec<PesFileEntry>,
    unreadable_entries: usize,
}

struct ScanResult {
    selection: DirectorySelection,
    paths: HashMap<String, PathBuf>,
}

fn is_pes(path: &Path) -> bool {
    path.extension()
        .and_then(|extension| extension.to_str())
        .is_some_and(|extension| extension.eq_ignore_ascii_case("pes"))
}

fn relative_path(root: &Path, path: &Path) -> Option<String> {
    path.strip_prefix(root)
        .ok()
        .map(|relative| relative.to_string_lossy().replace('\\', "/"))
}

fn scan_directory(root: &Path) -> Result<ScanResult, String> {
    let canonical_root = root
        .canonicalize()
        .map_err(|_| "Não foi possível acessar a pasta selecionada.".to_string())?;

    if !canonical_root.is_dir() {
        return Err("A seleção não corresponde a uma pasta válida.".to_string());
    }

    let mut files = Vec::new();
    let mut paths = HashMap::new();
    let mut unreadable_entries = 0;

    for entry in WalkDir::new(&canonical_root).follow_links(false) {
        let entry = match entry {
            Ok(entry) => entry,
            Err(_) => {
                unreadable_entries += 1;
                continue;
            }
        };

        if !entry.file_type().is_file() || !is_pes(entry.path()) {
            continue;
        }

        let path = match entry.path().canonicalize() {
            Ok(path) if path.starts_with(&canonical_root) => path,
            _ => {
                unreadable_entries += 1;
                continue;
            }
        };
        let Some(relative_path) = relative_path(&canonical_root, &path) else {
            unreadable_entries += 1;
            continue;
        };
        let metadata = match path.metadata() {
            Ok(metadata) => metadata,
            Err(_) => {
                unreadable_entries += 1;
                continue;
            }
        };

        // Confirma a permissão de leitura durante a varredura. Falhas são isoladas.
        if File::open(&path).is_err() {
            unreadable_entries += 1;
            continue;
        }

        let id = Uuid::new_v4().to_string();
        let name = path
            .file_name()
            .map(|name| name.to_string_lossy().into_owned())
            .unwrap_or_else(|| relative_path.clone());

        paths.insert(id.clone(), path);
        files.push(PesFileEntry {
            id,
            name,
            relative_path,
            size: metadata.len(),
        });
    }

    files.sort_by(|left, right| {
        left.relative_path
            .to_lowercase()
            .cmp(&right.relative_path.to_lowercase())
    });

    let folder_name = canonical_root
        .file_name()
        .map(|name| name.to_string_lossy().into_owned())
        .unwrap_or_else(|| "Pasta selecionada".to_string());

    Ok(ScanResult {
        selection: DirectorySelection {
            folder_name,
            files,
            unreadable_entries,
        },
        paths,
    })
}

#[tauri::command]
async fn select_pes_directory(
    app: AppHandle,
    state: State<'_, SelectedDirectoryState>,
) -> Result<Option<DirectorySelection>, String> {
    let selected = app.dialog().file().blocking_pick_folder();
    let Some(selected) = selected else {
        return Ok(None);
    };
    let root = selected
        .into_path()
        .map_err(|_| "A pasta selecionada não pode ser lida neste dispositivo.".to_string())?;

    let scan = tauri::async_runtime::spawn_blocking(move || scan_directory(&root))
        .await
        .map_err(|_| "Não foi possível concluir a leitura da pasta.".to_string())??;

    *state
        .files
        .lock()
        .map_err(|_| "O estado da seleção não está disponível.".to_string())? = scan.paths;

    Ok(Some(scan.selection))
}

#[tauri::command]
async fn read_selected_pes_file(
    id: String,
    state: State<'_, SelectedDirectoryState>,
) -> Result<Vec<u8>, String> {
    let path = state
        .files
        .lock()
        .map_err(|_| "O estado da seleção não está disponível.".to_string())?
        .get(&id)
        .cloned()
        .ok_or_else(|| "O arquivo não pertence à pasta selecionada.".to_string())?;

    if !is_pes(&path) {
        return Err("Somente arquivos .PES podem ser lidos.".to_string());
    }

    tauri::async_runtime::spawn_blocking(move || {
        std::fs::read(path)
            .map_err(|_| "Não foi possível ler um dos arquivos selecionados.".to_string())
    })
    .await
    .map_err(|_| "Não foi possível concluir a leitura do arquivo.".to_string())?
}

#[tauri::command]
fn clear_selected_directory(state: State<'_, SelectedDirectoryState>) -> Result<(), String> {
    state
        .files
        .lock()
        .map_err(|_| "O estado da seleção não está disponível.".to_string())?
        .clear();
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(SelectedDirectoryState::default())
        .invoke_handler(tauri::generate_handler![
            select_pes_directory,
            read_selected_pes_file,
            clear_selected_directory
        ])
        .run(tauri::generate_context!())
        .expect("erro ao executar o Catálogo de Bordados");
}

#[cfg(test)]
mod tests {
    use std::fs;

    use tempfile::tempdir;

    use super::{is_pes, scan_directory};

    #[test]
    fn accepts_pes_extension_without_case_sensitivity() {
        assert!(is_pes(std::path::Path::new("flor.PES")));
        assert!(is_pes(std::path::Path::new("flor.pes")));
        assert!(!is_pes(std::path::Path::new("flor.png")));
    }

    #[test]
    fn scans_pes_files_recursively_and_hides_absolute_paths() {
        let directory = tempdir().expect("temporary directory");
        let nested = directory.path().join("flores");
        fs::create_dir(&nested).expect("nested directory");
        fs::write(directory.path().join("raiz.PES"), b"pes").expect("root file");
        fs::write(nested.join("rosa.pes"), b"pes").expect("nested file");
        fs::write(nested.join("nota.txt"), b"text").expect("ignored file");

        let result = scan_directory(directory.path()).expect("directory scan");

        assert_eq!(result.selection.files.len(), 2);
        assert_eq!(result.selection.files[0].relative_path, "flores/rosa.pes");
        assert_eq!(result.selection.files[1].relative_path, "raiz.PES");
        assert!(result
            .selection
            .files
            .iter()
            .all(|file| !file.relative_path.contains(directory.path().to_string_lossy().as_ref())));
    }
}
