from pathlib import Path


def get_file_extension(file_path: str) -> str | None:
    """
    Detect file extension based on magic bytes (file signature).
    Returns the appropriate extension or None if unknown.
    """
    magic_bytes_map = {
        b"\x89PNG\r\n\x1a\n": ".png",
        b"\xff\xd8\xff": ".jpg",
        b"GIF87a": ".gif",
        b"GIF89a": ".gif",
        b"BM": ".bmp",
        b"%PDF": ".pdf",
        b"PK\x03\x04": [".zip", ".docx", ".xlsx"],  # Need further detection
        b"\x1f\x8b\x08": ".gz",
        b"BZh": ".bz2",
        b"\x7fELF": ".elf",
        b"MZ": ".exe",
        b"\xca\xfe\xba\xbe": ".class",
        b"\xff\xfe\x00\x00": ".exe",
        b"PLP\x6e\x53\x74": ".pls",
        b"ID3": ".mp3",
        b"\xff\xfb": ".mp3",
        b"ftyp": ".mp4",
        b"\x00\x00\x00\x20\x66\x74\x79\x70": ".mp4",
        b"RIFF": ".wav",
        b"\x42\x49\x47\x46": ".bmp",
    }

    try:
        with open(file_path, "rb") as f:
            file_signature = f.read(32)

        # Check magic bytes
        for signature, extension in magic_bytes_map.items():
            if file_signature.startswith(signature):
                if isinstance(extension, list):
                    # Further detection for ambiguous types
                    if signature == b"PK\x03\x04":
                        if b"xl/" in file_signature or b"worksheet" in file_signature:
                            return ".xlsx"
                        elif b"word/" in file_signature:
                            return ".docx"
                        else:
                            return ".zip"
                return extension

        # Check for text-based file types
        try:
            text_content = file_signature.decode("utf-8", errors="ignore")[:200]

            # Check XML-based
            if text_content.startswith("<?xml"):
                return ".xml"
            if '"version"' in text_content and '"encoding"' in text_content:
                return ".json"

            # Check JSON
            if text_content.strip().startswith(('{', '[')):
                return ".json"

            # Check HTML
            if any(
                tag in text_content.lower()
                for tag in ["<html", "<!doctype", "<head", "<body"]
            ):
                return ".html"

            # Check CSS
            if any(
                pattern in text_content.lower() for pattern in ["{", "css", "@media"]
            ):
                return ".css"

            # Check JavaScript
            if any(
                pattern in text_content.lower()
                for pattern in ["function", "const ", "let ", "var ", "=>"]
            ):
                return ".js"

            # Check Python
            if any(
                pattern in text_content
                for pattern in ["import ", "from ", "def ", "class ", "#!"]
            ):
                return ".py"

            # Check Bash
            if text_content.startswith("#!") and "bash" in text_content:
                return ".sh"

        except Exception:
            pass

        return None

    except (IOError, OSError):
        return None


def process_files_in_folder(folder_path: str = ".") -> None:
    """
    Process all files without extension in the given folder.
    Detects and adds appropriate extensions, or keeps files as is.
    """
    folder = Path(folder_path)

    if not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return

    files_processed = 0
    files_renamed = 0
    files_skipped = 0

    for item in folder.iterdir():
        if item.is_file() and item.suffix == "":
            files_processed += 1
            extension = get_file_extension(str(item))

            if extension:
                new_name = item.with_suffix(extension)
                try:
                    item.rename(new_name)
                    print(f"✓ Renamed: {item.name} → {new_name.name}")
                    files_renamed += 1
                except OSError as e:
                    print(f"✗ Failed to rename {item.name}: {e}")
            else:
                print(f"- Skipped: {item.name} (no extension detected)")
                files_skipped += 1

    print(
        f"\nSummary: Processed {files_processed} files, "
        f"Renamed {files_renamed}, Skipped {files_skipped}"
    )


if __name__ == "__main__":
    folder_path = input("Enter the folder path to process: ").strip()
    process_files_in_folder(folder_path)

