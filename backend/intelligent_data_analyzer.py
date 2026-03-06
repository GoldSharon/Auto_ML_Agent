import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from core.models import InputConfiguration, MLType, LearningType,DataAnalysisReport
from cognitive_engine import chat_llm


from prompts import (
    SUPERVISED_COLUMN_SELECTION_SYSTEM_PROMPT,
    CLUSTERING_COLUMN_SELECTION_SYSTEM_PROMPT,
    ASSOCIATION_COLUMN_SELECTION_SYSTEM_PROMPT,
    DATATYPE_SELECTION_SYSTEM_PROMPT
)


# Configure logging globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntelligentDataAnalyzer:
    """
    Intelligent data analyzer using CognitiveEngine (LLM)
    for automated preprocessing and feature engineering.

    Supports:
    - Supervised Learning: Classification, Regression
    - Unsupervised Learning: Clustering, Association Rules (Apriori)
    """


    def __init__(self, ipc: InputConfiguration ):
        """
        Initialize analyzer with dataframe and input configuration.

        Args:
            df: Input dataset
            ipc: InputConfiguration object
        """
        self.ml_type = ipc.ml_type
        self.learning_type = ipc.learning_type
        self.target_column = ipc.target_column
        self.index_column = ipc.index_column

    def analyze_dataframe(self, df: pd.DataFrame
                         ) -> Tuple[DataAnalysisReport, Dict[str, Any]]:
        """
        Perform comprehensive analysis and preprocessing recommendation.

        Args:
            df: Input DataFrame
            target_column: Override target column (optional)

        Returns:
            Tuple of (DataAnalysisReport, preprocessing_config)
        """
        if df.empty:
            raise ValueError("Input dataframe is empty")

        logger.info(f"Starting analysis for ML type: {self.ml_type}, learning_type: {self.learning_type}")

        # Droping index column
        logger.info("Step 1: Generating dataset summary...")
        summary = self.dataset_summary(df)

        logger.info("Step 2: Assigning appropriate data types...")
        df = self._data_type_assignment(df, summary)

        logger.info("Step 3: Preparing feature analysis...")

        # For supervised learning, exclude target from feature analysis

        if self.ml_type == MLType.SUPERVISED and self.target_column:
            if self.target_column not in df.columns:
                raise ValueError(f"Target column '{self.target_column}' not found in dataframe")
            feature_df = df.drop(columns=[self.target_column])
        else:
            feature_df = df

        logger.info("Step 4: Analyzing features...")
        report = self._build_report(feature_df, self.target_column)

        logger.info("Step 5: Getting preprocessing recommendations...")
        preprocessing_config = self._get_llm_preprocessing_suggestion(df, report)

        return report, preprocessing_config

    def dataset_summary(self, df: pd.DataFrame, sample_values: int = 5) -> Dict[str, Any]:
        """Generate dataset summary with column-level details."""
        stats_df = df.describe(include="all").transpose()
        stats = stats_df.fillna("").to_dict()

        columns_info = {}
        for col in df.columns:
            col_data = df[col]
            col_info: Dict[str, Any] = {
                "dtype": str(col_data.dtype),
                "missing_values": int(col_data.isnull().sum()),
                "missing_percentage": float((col_data.isnull().sum() / len(df)) * 100),
                "unique_values": int(col_data.nunique()),
                "sample_values": col_data.dropna().unique()[:sample_values].tolist()
            }

            if pd.api.types.is_numeric_dtype(col_data):
                col_info.update({
                    "min": float(col_data.min()) if not col_data.isnull().all() else None,
                    "max": float(col_data.max()) if not col_data.isnull().all() else None,
                    "mean": float(col_data.mean()) if not col_data.isnull().all() else None,
                    "std": float(col_data.std()) if not col_data.isnull().all() else None,
                    "median": float(col_data.median()) if not col_data.isnull().all() else None,
                    "variance": float(col_data.var()) if not col_data.isnull().all() else None,
                    "likely_categorical": col_data.nunique() < 20
                })

                # For association rules - calculate support
                if self.learning_type == "association":
                    col_info["support"] = float(col_data.notna().sum() / len(df))

            else:
                mode_val = col_data.mode().iloc[0] if not col_data.mode().empty else None
                col_info["most_frequent"] = str(mode_val) if mode_val else None
                col_info["value_counts"] = {
                    str(k): int(v) for k, v in col_data.value_counts().head(10).items()
                }

                # For association rules - calculate item support
                if self.learning_type == "association":
                    col_info["support"] = float(col_data.value_counts().iloc[0] / len(df)) if len(col_data.value_counts()) > 0 else 0.0

            columns_info[col] = col_info

        return {
            "stats": stats,
            "columns": columns_info,
            "rows": len(df),
            "columns_count": len(df.columns),
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024**2)
        }

    def _data_type_assignment(self, df: pd.DataFrame, summary: Dict[str, Any]) -> pd.DataFrame:
        """Use LLM to assign correct datatypes."""
        input_data = {
            "columns_list": df.columns.tolist(),
            "data_preview": df.head(10).to_dict(orient="records"),
            "summary_stats": summary["columns"]
        }
        result = chat_llm(DATATYPE_SELECTION_SYSTEM_PROMPT, json.dumps(input_data, indent=2))

        if not result or "column_dtypes" not in result:
            logger.warning("Datatype assignment failed, keeping original dtypes.")
            return df

        normalized_dtypes = self._normalize_column_mapping(df, result["column_dtypes"])
        return df.astype(normalized_dtypes, errors="ignore")

    def _normalize_column_mapping(self, df: pd.DataFrame, llm_dtypes: Dict[str, str]) -> Dict[str, str]:
        """Map LLM-suggested column names to actual df columns (handles typos)."""
        from difflib import get_close_matches
        normalized = {}
        actual_columns = df.columns.tolist()

        for llm_col, dtype in llm_dtypes.items():
            if llm_col in actual_columns:
                normalized[llm_col] = dtype
            else:
                matches = get_close_matches(llm_col, actual_columns, n=1, cutoff=0.6)
                if matches:
                    normalized[matches[0]] = dtype
                    logger.info(f"Mapped '{llm_col}' → '{matches[0]}'")
                else:
                    logger.warning(f"Column '{llm_col}' not found in dataframe.")
        return normalized

    def _build_report(self, feature_df: pd.DataFrame, target_column: Optional[str]) -> DataAnalysisReport:
        """Helper to compute metrics and return report object."""
        shape = feature_df.shape
        dtypes = {col: str(dtype) for col, dtype in feature_df.dtypes.items()}
        missing_values = feature_df.isnull().sum().to_dict()
        missing_percentage = {col: (val / len(feature_df)) * 100 for col, val in missing_values.items()}
        numerical_cols = feature_df.select_dtypes(include=[np.number]).columns.tolist()
        numerical_stats, categorical_stats, outliers_detected, correlations = {}, {}, {}, {}

        # Numerical statistics
        for col in numerical_cols:
            stats = feature_df[col].describe().to_dict()
            stats["outliers"] = self._detect_outliers(feature_df[col])
            stats["variance"] = float(feature_df[col].var()) if not feature_df[col].isnull().all() else 0.0

            # Coefficient of variation (useful for clustering)
            if self.learning_type == "clustering" and stats.get("mean", 0) != 0:
                stats["cv_coefficient"] = stats["std"] / stats["mean"]

            numerical_stats[col] = {k: float(v) if isinstance(v, (np.integer, np.floating)) else v for k, v in stats.items()}
            outliers_detected[col] = stats["outliers"]

        # Categorical statistics
        categorical_cols = feature_df.select_dtypes(include=["object", "category"]).columns.tolist()
        for col in categorical_cols:
            cat_stats = {
                "unique_values": int(feature_df[col].nunique()),
                "most_frequent": str(feature_df[col].mode().iloc[0]) if not feature_df[col].mode().empty else None,
                "value_counts": {str(k): int(v) for k, v in feature_df[col].value_counts().head(10).items()}
            }

            # For association rules - add support metrics
            if self.learning_type == "association":
                top_value_count = feature_df[col].value_counts().iloc[0] if len(feature_df[col].value_counts()) > 0 else 0
                cat_stats["support"] = float(top_value_count / len(feature_df))
                cat_stats["most_frequent_items"] = feature_df[col].value_counts().head(3).index.tolist()

            categorical_stats[col] = cat_stats

        # Correlations (less relevant for association rules)
        if self.learning_type != "association" and len(numerical_cols) > 1:
            corr_matrix = feature_df[numerical_cols].corr()
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    val = corr_matrix.iloc[i, j]
                    # For clustering, focus on high correlations
                    threshold = 0.9 if self.learning_type == "clustering" else 0.7
                    if abs(val) > threshold:
                        correlations[f"{corr_matrix.columns[i]}_vs_{corr_matrix.columns[j]}"] = float(val)

        quality_metrics = self._calculate_quality_metrics(feature_df, missing_percentage, outliers_detected)

        return DataAnalysisReport(
            shape=shape,
            dtypes=dtypes,
            missing_values=missing_values,
            missing_percentage=missing_percentage,
            numerical_stats=numerical_stats,
            categorical_stats=categorical_stats,
            outliers_detected=outliers_detected,
            correlations=correlations,
            data_quality_score=quality_metrics["overall_score"],
            target_column=target_column,
            data_quality_metrics=quality_metrics,
            ml_type=self.ml_type,
            learning_type=self.learning_type
        )

    def _detect_outliers(self, series: pd.Series, learning_type: str = "iqr") -> int:
        """Detect outliers using IQR learning_type."""
        if not pd.api.types.is_numeric_dtype(series) or series.isnull().all():
            return 0

        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        return int(outliers)

    def _calculate_quality_metrics(self, df: pd.DataFrame, missing_pct: Dict[str, float],
                                   outliers: Dict[str, int]) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        total_missing = sum(missing_pct.values()) / len(missing_pct) if missing_pct else 0
        total_outliers = sum(outliers.values())

        # Quality score calculation (0-100)
        completeness_score = max(0, 100 - total_missing)
        outlier_penalty = min(50, (total_outliers / len(df)) * 100)
        overall_score = max(0, min(100, completeness_score - outlier_penalty))

        return {
            "overall_score": round(overall_score, 2),
            "completeness_score": round(completeness_score, 2),
            "total_missing_percentage": round(total_missing, 2),
            "total_outliers": total_outliers,
            "outlier_percentage": round((total_outliers / len(df)) * 100, 2)
        }

    def _get_llm_preprocessing_suggestion(self, df: pd.DataFrame,
                                      report: DataAnalysisReport) -> Dict[str, Any]:

        if self.learning_type in (LearningType.REGRESSION, LearningType.CLASSIFICATION):
            system_prompt = SUPERVISED_COLUMN_SELECTION_SYSTEM_PROMPT

        elif self.learning_type == LearningType.CLUSTERING:
            system_prompt = CLUSTERING_COLUMN_SELECTION_SYSTEM_PROMPT

        elif self.learning_type == LearningType.APRIORI:
            system_prompt = ASSOCIATION_COLUMN_SELECTION_SYSTEM_PROMPT

        else:
            raise ValueError(f"Unknown learning_type: {self.learning_type}")
        # Exclude target column from features before passing to LLM
        feature_columns = {col: dtype for col, dtype in report.dtypes.items()
                           if col != report.target_column}

        feature_df = df.drop(columns=[report.target_column], errors="ignore") \
                      if report.target_column else df

        # Prepare input data
        input_data = {
            "ml_type": self.ml_type.value,
            "learning_type": self.learning_type.value,
            "features": feature_columns,
            "first_5_rows": feature_df.head(5).to_dict(orient="records"),
            "column_names": list(feature_df.columns),
            "shape": [feature_df.shape[0], feature_df.shape[1]],
            "missing_values": report.missing_values,
            "missing_percentage": report.missing_percentage,
            "outliers_detected": report.outliers_detected,
            "correlations": report.correlations,
            "numerical_stats": report.numerical_stats,
            "categorical_stats": report.categorical_stats,
            "target_column": report.target_column,  
            "data_quality_metrics": report.data_quality_metrics
        }

        logger.info(f"Requesting preprocessing suggestions for {self.ml_type.value}/{self.learning_type.value}...")
        result = chat_llm(system_prompt, json.dumps(input_data, indent=2))

        if not result:
            logger.warning("LLM preprocessing suggestion failed, returning empty config.")
            return self._get_default_preprocessing_config(report)

        # Safety: remove any accidental references to target column in LLM output
        if report.target_column:
            for section in ["columns_to_drop", "columns_to_keep"]:
                if section in result and "column_list" in result[section]:
                    result[section]["column_list"] = [
                        col for col in result[section]["column_list"]
                        if col != report.target_column
                    ]
        return result

    def _get_default_preprocessing_config(self, report: Optional[DataAnalysisReport] = None) -> Dict[str, Any]:
        """Return default preprocessing config as fallback."""
        return {
            "columns_to_drop": {"column_list": [], "reasons": {}},
            "columns_to_keep": {
                "column_list": list(report.dtypes.keys()) if report else [],
                "details": {}
            },
            "feature_engineering_suggestions": [],
            "pipeline_recommendation": {},
            "summary": {
                "original_features": len(report.dtypes) if report else 0,
                "recommended_features": len(report.dtypes) if report else 0,
                "features_dropped": 0,
                "new_features_created": 0,
                "expected_model_improvement": "Default configuration used due to LLM failure",
                "key_insights": []
            }
        }


    def get_preprocessing_report(self, report: DataAnalysisReport,
                                preprocessing_config: Dict[str, Any]) -> str:
        """Generate human-readable preprocessing report."""
        lines = [
            "="*80,
            f"DATA ANALYSIS REPORT - {self.ml_type.value} / {self.learning_type.value}",
            "="*80,
            f"\nDataset Shape: {report.shape[0]} rows × {report.shape[1]} columns",
            f"ML Task Type: {self.ml_type.value}",
            f"Method: {self.learning_type.value}",
            f"Target Column: {report.target_column if report.target_column else 'None (Unsupervised)'}",
            f"Data Quality Score: {report.data_quality_score}/100",
            f"\n{'='*80}",
            "\nCOLUMNS TO DROP:",
            "-"*80
        ]

        for col in preprocessing_config.get("columns_to_drop", {}).get("column_list", []):
            reasons = preprocessing_config["columns_to_drop"]["reasons"].get(col, [])
            lines.append(f"  • {col}")
            for reason in reasons:
                lines.append(f"      - {reason}")

        lines.extend([
            f"\n{'='*80}",
            "\nCOLUMNS TO KEEP (Top 5 by priority):",
            "-"*80
        ])

        keep_details = preprocessing_config.get("columns_to_keep", {}).get("details", {})
        sorted_cols = sorted(keep_details.items(),
                           key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x[1].get("priority", "low"), 0),
                           reverse=True)[:5]

        for col, details in sorted_cols:
            lines.append(f"  • {col} (Priority: {details.get('priority', 'N/A')}, Confidence: {details.get('confidence', 'N/A')})")
            lines.append(f"      Reason: {details.get('reason', 'N/A')}")
            lines.append(f"      Preprocessing: {', '.join(details.get('recommended_preprocessing', []))}")

        lines.extend([
            f"\n{'='*80}",
            "\nSUMMARY:",
            "-"*80,
            f"  Original Features: {preprocessing_config.get('summary', {}).get('original_features', 'N/A')}",
            f"  Recommended Features: {preprocessing_config.get('summary', {}).get('recommended_features', 'N/A')}",
            f"  Features Dropped: {preprocessing_config.get('summary', {}).get('features_dropped', 'N/A')}",
            f"  New Features Created: {preprocessing_config.get('summary', {}).get('new_features_created', 'N/A')}",
            f"\n  Expected Impact: {preprocessing_config.get('summary', {}).get('expected_model_improvement', 'N/A')}",
            f"\n{'='*80}\n"
        ])

        return "\n".join(lines)