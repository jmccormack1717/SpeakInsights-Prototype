"""Tests for analysis playbooks"""
import pytest
import pandas as pd
import numpy as np
from app.services import playbooks


class TestOverviewPlaybook:
    """Tests for overview_playbook"""

    def test_overview_playbook_basic(self, sample_dataframe):
        """Test overview playbook with valid data"""
        result = playbooks.overview_playbook(sample_dataframe)
        
        assert "visualization" in result
        assert "analysis_context" in result
        assert result["visualization"]["type"] == "table"
        assert "data" in result["visualization"]
        assert "columns" in result["visualization"]["data"]
        assert result["analysis_context"]["kind"] == "overview"
        assert result["analysis_context"]["row_count"] == 100

    def test_overview_playbook_empty(self, empty_dataframe):
        """Test overview playbook with empty DataFrame"""
        result = playbooks.overview_playbook(empty_dataframe)
        
        assert result["analysis_context"]["row_count"] == 0
        assert result["visualization"]["type"] == "table"


class TestCorrelationPlaybook:
    """Tests for correlation_playbook"""

    def test_correlation_playbook_basic(self, sample_dataframe):
        """Test correlation playbook with valid data"""
        result = playbooks.correlation_playbook(
            sample_dataframe,
            outcome="outcome",
            top_n=3
        )
        
        assert "visualization" in result
        assert "analysis_context" in result
        assert result["analysis_context"]["kind"] == "correlation"
        assert result["visualization"]["type"] == "bar"
        assert "labels" in result["visualization"]["data"]
        assert len(result["visualization"]["data"]["labels"]) <= 3

    def test_correlation_playbook_insufficient_data(self, minimal_dataframe):
        """Test correlation playbook with insufficient data"""
        result = playbooks.correlation_playbook(
            minimal_dataframe,
            outcome="value",
            top_n=5
        )
        
        assert result["analysis_context"]["kind"] == "correlation"
        assert result["analysis_context"]["reason"] == "insufficient_data"

    def test_correlation_playbook_missing_outcome(self, sample_dataframe):
        """Test correlation playbook with missing outcome column"""
        result = playbooks.correlation_playbook(
            sample_dataframe,
            outcome="nonexistent",
            top_n=5
        )
        
        assert result["analysis_context"]["reason"] == "insufficient_data"


class TestDistributionPlaybook:
    """Tests for distribution_playbook"""

    def test_distribution_playbook_basic(self, sample_dataframe):
        """Test distribution playbook with valid data"""
        result = playbooks.distribution_playbook(
            sample_dataframe,
            feature="age",
            bins=10
        )
        
        assert "visualization" in result
        assert result["visualization"]["type"] == "histogram"
        assert result["analysis_context"]["kind"] == "distribution"
        assert result["analysis_context"]["feature"] == "age"
        assert "labels" in result["visualization"]["data"]
        assert len(result["visualization"]["data"]["labels"]) == 10

    def test_distribution_playbook_auto_feature(self, sample_dataframe):
        """Test distribution playbook with auto-selected feature"""
        result = playbooks.distribution_playbook(
            sample_dataframe,
            feature=None,
            bins=5
        )
        
        assert result["visualization"]["type"] == "histogram"
        assert result["analysis_context"]["kind"] == "distribution"
        assert "feature" in result["analysis_context"]

    def test_distribution_playbook_no_numeric(self, empty_dataframe):
        """Test distribution playbook with no numeric columns"""
        df = pd.DataFrame({'text': ['a', 'b', 'c']})
        result = playbooks.distribution_playbook(df, feature=None)
        
        assert result["analysis_context"]["reason"] == "no_numeric_columns"


class TestOutcomeBreakdownPlaybook:
    """Tests for outcome_breakdown_playbook"""

    def test_outcome_breakdown_basic(self, sample_dataframe):
        """Test outcome breakdown playbook"""
        result = playbooks.outcome_breakdown_playbook(
            sample_dataframe,
            outcome="outcome"
        )
        
        assert result["visualization"]["type"] == "pie"
        assert result["analysis_context"]["kind"] == "outcome_breakdown"
        assert "counts" in result["analysis_context"]
        assert "percentages" in result["analysis_context"]

    def test_outcome_breakdown_auto_detect(self, sample_dataframe):
        """Test outcome breakdown with auto-detection"""
        result = playbooks.outcome_breakdown_playbook(
            sample_dataframe,
            outcome=None
        )
        
        assert result["visualization"]["type"] == "pie"
        assert result["analysis_context"]["kind"] == "outcome_breakdown"


class TestSegmentComparisonPlaybook:
    """Tests for segment_comparison_playbook"""

    def test_segment_comparison_basic(self, sample_dataframe):
        """Test segment comparison playbook"""
        # Create a categorical column
        df = sample_dataframe.copy()
        df['group'] = np.where(df['outcome'] == 1, 'positive', 'negative')
        
        result = playbooks.segment_comparison_playbook(
            df,
            segment_column="group",
            outcome="outcome"
        )
        
        assert result["visualization"]["type"] == "bar"
        assert result["analysis_context"]["kind"] == "segment_comparison"
        assert "segments" in result["analysis_context"]


class TestRelationshipPlaybook:
    """Tests for relationship_playbook"""

    def test_relationship_playbook_basic(self, sample_dataframe):
        """Test relationship playbook"""
        result = playbooks.relationship_playbook(
            sample_dataframe,
            feature_x="age",
            feature_y="glucose"
        )
        
        assert result["visualization"]["type"] == "scatter"
        assert result["analysis_context"]["kind"] == "relationship"
        assert "x" in result["visualization"]["data"]
        assert "y" in result["visualization"]["data"]
        assert len(result["visualization"]["data"]["x"]) > 0

    def test_relationship_playbook_auto_features(self, sample_dataframe):
        """Test relationship playbook with auto-selected features"""
        result = playbooks.relationship_playbook(
            sample_dataframe,
            feature_x=None,
            feature_y=None
        )
        
        assert result["visualization"]["type"] == "scatter"
        assert "feature_x" in result["analysis_context"]
        assert "feature_y" in result["analysis_context"]


