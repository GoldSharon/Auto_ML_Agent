import re
import pandas as pd
import csv
import json
import xml.etree.ElementTree as ET
import chardet
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ── Encoding / delimiter detection ────────────────────────────────────────────

def detect_encoding(file_path):
    try:
        with open(file_path, "rb") as fp:
            raw_data = fp.read(100000)
            result = chardet.detect(raw_data)
            encoding = result["encoding"]
            confidence = result["confidence"]

            if encoding == "ascii":
                logger.warning(f"ASCII detected with {confidence:.2%} confidence")
                logger.info("Upgrading to Latin1 (safer for compatibility)")
                return "latin1"

            logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")
            return encoding

    except Exception as e:
        logger.warning(f"Error detecting encoding {e}. Using utf-8")
        return "utf-8"


def find_delimiter(file_path):
    logger.info(f"Detecting delimiter for file: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
        sample = fp.read(2048)
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
            logger.info("Delimiter detected successfully")
        except Exception:
            delimiter = ","
            logger.warning("Error finding delimiter — defaulting to ','")

        logger.info(f"Using delimiter: {delimiter!r}")

    return delimiter


# ── Format-specific readers ───────────────────────────────────────────────────

def read_json(file_path):
    try:
        with open(file_path, "r") as fp:
            data = json.load(fp)

        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            logger.error("Unexpected JSON structure")
            return None

        return df

    except Exception:
        logger.error("Error reading JSON file")
        return None


def read_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        data = []
        for child in root:
            row = {}
            for elem in child:
                row[elem.tag] = elem.text
            data.append(row)

        return pd.DataFrame(data)

    except Exception:
        logger.error("Error reading XML file")
        return None


# ── DataFrame cleaning ────────────────────────────────────────────────────────

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Drop all-NaN columns and fix unnamed-column headers."""
    df = df.dropna(axis=1, how="all")

    unnamed_cols = [col for col in df.columns if str(col).startswith("Unnamed")]
    for col in unnamed_cols:
        if df[col].isna().all() or (df[col] == "").all():
            df = df.drop(columns=[col])

    total_cols = len(df.columns)
    unnamed_count = df.columns.str.contains("Unnamed").sum()

    if unnamed_count == total_cols and total_cols > 0:
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        logger.info("All columns were unnamed — promoted first row to column headers")
    elif unnamed_count > 0:
        logger.info(
            f"Found {unnamed_count} unnamed column(s) out of {total_cols} — keeping as data columns"
        )

    df.columns = df.columns.str.strip()
    return df


def canonicalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Canonicalize column names and clean categorical values.
    Removes special characters that cause issues with XGBoost / feature
    name validation.

    Returns:
        (cleaned DataFrame, column mapping dict {original -> canonical})
    """
    mapping: dict[str, str] = {}
    new_cols: list[str] = []

    for col in df.columns:
        clean = str(col).lower().strip()
        clean = re.sub(r"\s+", "_", clean)
        clean = re.sub(r"[^a-z0-9_]", "", clean)
        mapping[col] = clean
        new_cols.append(clean)

    df.columns = new_cols

    # Sanitize categorical / object values (prevents broken one-hot names)
    for col in df.select_dtypes(include=["object", "category"]).columns:
        df[col] = df[col].astype(str).apply(
            lambda x: re.sub(r"[^a-z0-9_]", "_", x.lower().strip())
        )

    logger.info(f"Canonicalized {len(mapping)} column(s)")
    return df, mapping


# ── Public entry point ────────────────────────────────────────────────────────

def open_file(file_path: str) -> tuple[pd.DataFrame | None, dict]:
    """
    Load any supported file, clean it, and canonicalize column names.

    Supported formats: CSV/TSV/delimited, Excel (.xls/.xlsx),
    Parquet, JSON, XML.

    Returns:
        (DataFrame, column_mapping)   on success
        (None,      {})               on failure
    """
    normalized = str(file_path).lower()
    encoding = detect_encoding(file_path)
    logger.info(f"Opening file: {file_path}  (encoding={encoding})")

    try:
        if normalized.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        elif normalized.endswith(".parquet"):
            df = pd.read_parquet(file_path)
        elif normalized.endswith(".json"):
            df = read_json(file_path)
        elif normalized.endswith(".xml"):
            df = read_xml_file(file_path)
        else:
            delimiter = find_delimiter(file_path)
            df = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding=encoding,
                skip_blank_lines=True,
            )

        if df is None:
            logger.error(f"Failed to parse file: {file_path}")
            return None, {}

        df = clean_dataframe(df)
        df, col_mapping = canonicalize_columns(df)

        logger.info(f"File loaded successfully — shape: {df.shape}")
        return df, col_mapping

    except Exception as e:
        logger.error(f"Error opening file {file_path}: {e}")
        return None, {}