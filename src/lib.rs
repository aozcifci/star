use std::path::Path;

pub fn check_format_type(format_type: Option<&str>, path: &Path) -> Option<&'static str> {
    let t = format_type
        .or_else(|| Some(path.extension()?.to_str()?))?
        .to_lowercase();
    Some(match t.as_str() {
        "xz" => "xz",
        "gzip" | "gz" | "tgz" | "z" => "gzip",
        "tar" => "tar",
        "zst" | "zstd" => "zstd",
        _ => None?,
    })
}

pub fn target_is_dir(path: &Path) -> bool {
    let path = path.to_string_lossy().to_string();
    if path.len() == 0 {
        return true;
    }
    if path.ends_with('/') {
        return true;
    }
    if cfg!(windows) && path.ends_with('\\') {
        return true;
    }
    false
}

