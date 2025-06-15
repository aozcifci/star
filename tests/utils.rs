use std::path::Path;
use star::{check_format_type, target_is_dir};

#[test]
fn test_check_format_type_extensions() {
    assert_eq!(check_format_type(None, Path::new("foo.xz")), Some("xz"));
    assert_eq!(check_format_type(None, Path::new("foo.gz")), Some("gzip"));
    assert_eq!(check_format_type(None, Path::new("foo.tgz")), Some("gzip"));
    assert_eq!(check_format_type(None, Path::new("foo.z")), Some("gzip"));
    assert_eq!(check_format_type(None, Path::new("foo.zst")), Some("zstd"));
    assert_eq!(check_format_type(None, Path::new("foo.tar")), Some("tar"));
    assert_eq!(check_format_type(Some("xz"), Path::new("foo.tar")), Some("xz"));
    assert_eq!(check_format_type(Some("gz"), Path::new("foo.tar")), Some("gzip"));
    assert_eq!(check_format_type(Some("zst"), Path::new("foo.tar")), Some("zstd"));
    assert_eq!(check_format_type(Some("unknown"), Path::new("foo.bar")), None);
}

#[test]
fn test_target_is_dir_variations() {
    assert!(target_is_dir(Path::new("")));
    assert!(target_is_dir(Path::new("dir/")));
    if cfg!(windows) {
        assert!(target_is_dir(Path::new("dir\\")));
    } else {
        assert!(!target_is_dir(Path::new("dir\\")));
    }
    assert!(!target_is_dir(Path::new("dir")));
}
