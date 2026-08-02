import os
import pandas as pd

def test_report_exists():
    assert os.path.exists("eho_permit_construction_report.csv"), "CSV report should exist"
    assert os.path.exists("EHO_Permit_Construction_Report.md"), "Markdown report should exist"

def test_report_contents():
    df = pd.read_csv("eho_permit_construction_report.csv")
    assert not df.empty, "Report should not be empty"

    # Check expected columns
    expected_cols = [
        'RPC', 'Address', 'EHO_Permit_Status', 'EHO_Permits',
        'Multi_Unit_Permit', 'SFD_Permit', 'Demolition_Permit',
        'Development_Project', 'Construction_Status'
    ]
    for col in expected_cols:
        assert col in df.columns, f"Expected column {col} in report"

    # Check EHO permit statuses
    statuses = df['EHO_Permit_Status'].unique()
    assert 'Approved' in statuses, "Should contain Approved EHOs"
    assert 'Not Approved (Pending/Void/Other)' in statuses, "Should contain non-Approved EHOs"

    # Check some construction status presence
    const_statuses = df['Construction_Status'].unique()
    assert any(s in const_statuses for s in ['Not Started', 'Underway', 'Complete']), "Should have valid construction status values"

if __name__ == '__main__':
    print("Running tests...")
    test_report_exists()
    test_report_contents()
    print("All tests passed successfully!")
