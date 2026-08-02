import pandas as pd
import numpy as np
import re
from utils import load_housing_data

def normalize_address(addr):
    if not isinstance(addr, str):
        return ""
    # Convert to uppercase
    addr = addr.upper().strip()
    # Replace multiple whitespaces
    addr = re.sub(r'\s+', ' ', addr)
    # Remove trailing/leading periods
    addr = addr.replace(".", "")
    # Normalize abbreviations
    addr = re.sub(r'\bSTREET\b', 'ST', addr)
    addr = re.sub(r'\bROAD\b', 'RD', addr)
    addr = re.sub(r'\bDRIVE\b', 'DR', addr)
    addr = re.sub(r'\bAVENUE\b', 'AVE', addr)
    addr = re.sub(r'\bBOULEVARD\b', 'BLVD', addr)
    addr = re.sub(r'\bCOURT\b', 'CT', addr)
    addr = re.sub(r'\bPLACE\b', 'PL', addr)
    addr = re.sub(r'\bNORTH\b', 'N', addr)
    addr = re.sub(r'\bSOUTH\b', 'S', addr)
    addr = re.sub(r'\bEAST\b', 'E', addr)
    addr = re.sub(r'\bWEST\b', 'W', addr)
    return addr.strip()

def main():
    print("Loading permit data...")
    # Load Permit Data
    df_permits = load_housing_data('Permit/Permit.txt.gz')

    # Fill NA values
    df_permits['PermitTypeAliasName'] = df_permits['PermitTypeAliasName'].fillna('')
    df_permits['PermitNbr'] = df_permits['PermitNbr'].fillna('').astype(str).str.strip()
    df_permits['PermitStatusCode'] = df_permits['PermitStatusCode'].fillna('').astype(str).str.strip()
    df_permits['PermitDescriptionText'] = df_permits['PermitDescriptionText'].fillna('')
    df_permits['RealEstatePropertyCode'] = df_permits['RealEstatePropertyCode'].fillna('').astype(str).str.strip()
    df_permits['StreetAddressText'] = df_permits['StreetAddressText'].fillna('').astype(str).str.strip()

    # Filter EHO permits
    eho_mask = (df_permits['PermitTypeAliasName'] == 'Expanded Housing Option') | (df_permits['PermitNbr'].str.startswith('ZEHO'))
    df_eho = df_permits[eho_mask]

    print(f"Total EHO Permits: {len(df_eho)}")

    # Get all unique RPCs with EHO permits
    eho_rpcs = df_eho['RealEstatePropertyCode'].unique()
    eho_rpcs = [rpc for rpc in eho_rpcs if rpc and rpc != 'nan']
    print(f"Unique RPCs with EHO Permits: {len(eho_rpcs)}")

    # Filter all permits for those properties
    df_rpc_permits = df_permits[df_permits['RealEstatePropertyCode'].isin(eho_rpcs)]

    print("Loading development projects data...")
    df_projects = load_housing_data('HousingBuilding/DevelopmentProject.txt')
    df_projects['CommentText'] = df_projects['CommentText'].fillna('')
    df_projects['DevelopmentProjectName'] = df_projects['DevelopmentProjectName'].fillna('')
    df_projects['DevelopmentProjectAddressText'] = df_projects['DevelopmentProjectAddressText'].fillna('')
    df_projects['StatusDsc'] = df_projects['StatusDsc'].fillna('')

    # List to store processed rows for report
    records = []

    for rpc in eho_rpcs:
        # Get permits for this RPC
        prop_permits = df_rpc_permits[df_rpc_permits['RealEstatePropertyCode'] == rpc]

        # Get EHO permits for this RPC
        prop_eho = prop_permits[
            (prop_permits['PermitTypeAliasName'] == 'Expanded Housing Option') |
            (prop_permits['PermitNbr'].str.startswith('ZEHO'))
        ]

        if prop_eho.empty:
            continue

        # Address extraction
        address_raw = prop_eho['StreetAddressText'].iloc[0]
        address_norm = normalize_address(address_raw)

        # Determine EHO permit details
        # We can list all EHO permits for this property
        eho_list = []
        is_approved = False
        approved_eho_nbrs = []
        all_eho_nbrs = []

        for _, row in prop_eho.iterrows():
            nbr = row['PermitNbr']
            status = row['PermitStatusCode']
            eho_list.append(f"{nbr} ({status})")
            all_eho_nbrs.append(nbr)
            if status.upper() == 'APPROVED':
                is_approved = True
                approved_eho_nbrs.append(nbr)

        eho_status_summary = ", ".join(eho_list)

        # Look for multi-unit permits (Commercial New or Residential New with multi-unit keywords)
        multi_unit_permits = []
        sfd_permits = []
        demolition_permits = []
        other_notable_permits = []

        for _, row in prop_permits.iterrows():
            p_type = row['PermitTypeAliasName']
            p_nbr = row['PermitNbr']
            p_desc = row['PermitDescriptionText']
            p_status = row['PermitStatusCode']

            # Skip EHO permit itself
            if p_nbr in all_eho_nbrs:
                continue

            p_desc_upper = p_desc.upper()

            # Multi-unit classification:
            # - 'Commercial New'
            # - 'Residential New' that contains keywords indicating multi-unit (townhouse, duplex, triplex, EHO, 2-unit, 3-unit, 4-unit, 5-unit, 6-unit, multifamily, multiplex)
            # Single-family classification:
            # - 'Residential New' that does NOT contain multi-unit keywords but mentions single family, SFD, SFH, dwelling.
            is_multi = False
            is_sfd = False

            if p_type == 'Commercial New':
                is_multi = True
            elif p_type == 'Residential New':
                # Keywords indicating multi-unit
                multi_keywords = ['TOWNHOUSE', 'TOWNHOME', 'DUPLEX', 'TRIPLEX', 'MULTIFAMILY', 'MULTI-UNIT', 'EHO', '4-UNIT', '5-UNIT', '6-UNIT', '3-UNIT', '2-UNIT', 'APARTMENT', 'MULTIPLEX']
                if any(kw in p_desc_upper for kw in multi_keywords):
                    is_multi = True
                else:
                    is_sfd = True

            if is_multi:
                multi_unit_permits.append(f"{p_nbr}: {p_status} ({p_type} - {p_desc[:60]}...)")
            elif is_sfd:
                sfd_permits.append(f"{p_nbr}: {p_status} ({p_desc[:60]}...)")
            elif p_type == 'Demolition':
                demolition_permits.append(f"{p_nbr}: {p_status}")
            elif 'SEWER CAP' in p_desc_upper or 'CAP OFF' in p_desc_upper:
                other_notable_permits.append(f"{p_nbr}: {p_status} (Sewer Cap)")

        multi_unit_summary = "; ".join(multi_unit_permits) if multi_unit_permits else "None"
        sfd_summary = "; ".join(sfd_permits) if sfd_permits else "None"
        demo_summary = "; ".join(demolition_permits) if demolition_permits else "None"

        # Link to Development Projects
        # Try to match by EHO permit number in CommentText
        proj_matches = pd.DataFrame()
        for eho_nbr in all_eho_nbrs:
            m = df_projects[df_projects['CommentText'].str.contains(eho_nbr, case=False, na=False)]
            if not m.empty:
                proj_matches = pd.concat([proj_matches, m])

        # If no match by ZEHO number, try matching by normalized address
        if proj_matches.empty and address_norm:
            # Let's normalize address field in df_projects for lookup
            # We do it on the fly or pre-filter
            # A simple fast match:
            # Check if address_norm is in normalized development project address
            df_projects['NormalizedAddress'] = df_projects['DevelopmentProjectAddressText'].apply(normalize_address)
            m = df_projects[df_projects['NormalizedAddress'] == address_norm]
            if not m.empty:
                proj_matches = pd.concat([proj_matches, m])

        # Deduplicate matches
        if not proj_matches.empty:
            proj_matches = proj_matches.drop_duplicates(subset=['DevelopementProjectKey'])
            proj_name = proj_matches['DevelopmentProjectName'].iloc[0]
            proj_status = proj_matches['StatusDsc'].iloc[0]
            proj_units = proj_matches['ResidentialUnitCnt'].iloc[0]
            proj_comment = proj_matches['CommentText'].iloc[0]
            proj_id = proj_matches['DevelopementProjectId'].iloc[0]
            proj_summary = f"{proj_name} (ID: {proj_id}) - Status: {proj_status}"
        else:
            proj_summary = "None Found"
            proj_status = "None"
            proj_units = ""
            proj_comment = ""

        # Let's synthesize "Construction Status" from all sources
        # Underway, Complete, or Not Started?
        # Check active multi-unit or SFD permits, or Development Project status.
        construction_status = "Not Started"

        # If development project is Completed or Under Construction:
        if proj_status == 'Under Construction':
            construction_status = "Underway (via DevProject)"
        elif proj_status == 'Completed':
            construction_status = "Complete (via DevProject)"
        elif proj_status == 'Demolitions':
            construction_status = "Demolition Underway"

        # Check permit statuses
        # 'Issued Awaiting Insp', 'Issued Awaiting Inspection', 'Active', 'Approved'
        all_related_permits = prop_permits[~prop_permits['PermitNbr'].isin(all_eho_nbrs)]
        active_statuses = ['ACTIVE', 'ISSUED AWAITING INSP', 'ISSUED AWAITING INSPECTION', 'ISSUED AWAITING INSPECTIONS']
        completed_statuses = ['FINALED', 'CLOSED', 'COMPLETED']

        has_active_permit = False
        has_completed_permit = False

        for _, row in all_related_permits.iterrows():
            st = str(row['PermitStatusCode']).upper().strip()
            # If we have an active building permit (Residential New or Commercial New)
            if row['PermitTypeAliasName'] in ['Commercial New', 'Residential New']:
                if st in active_statuses:
                    has_active_permit = True
                elif st in completed_statuses:
                    has_completed_permit = True

        if has_completed_permit:
            construction_status = "Complete"
        elif has_active_permit:
            construction_status = "Underway"
        elif demolition_permits:
            # If demo permit exists, let's see if it is active or completed
            demo_active = False
            for dp in demolition_permits:
                if any(act in dp.upper() for act in active_statuses + ['APPROVED']):
                    demo_active = True
            if demo_active:
                construction_status = "Demolition/Site Prep"

        records.append({
            'RPC': rpc,
            'Address': address_raw,
            'EHO_Permit_Status': "Approved" if is_approved else "Not Approved (Pending/Void/Other)",
            'EHO_Permits': eho_status_summary,
            'Multi_Unit_Permit': multi_unit_summary,
            'SFD_Permit': sfd_summary,
            'Demolition_Permit': demo_summary,
            'Development_Project': proj_summary,
            'Construction_Status': construction_status,
            'Approved_EHO': is_approved
        })

    df_report = pd.DataFrame(records)

    # Sort by Approved_EHO (descending) so Approved EHOs are at the top, then by Address
    df_report = df_report.sort_values(by=['Approved_EHO', 'Address'], ascending=[False, True])
    df_report.drop(columns=['Approved_EHO'], inplace=True)

    # Export to CSV
    csv_path = "eho_permit_construction_report.csv"
    df_report.to_csv(csv_path, index=False)
    print(f"Report saved to CSV: {csv_path}")

    # Generate Markdown Report
    markdown_path = "EHO_Permit_Construction_Report.md"
    generate_markdown_report(df_report, markdown_path)
    print(f"Report saved to Markdown: {markdown_path}")

def generate_markdown_report(df, filepath):
    with open(filepath, 'w') as f:
        f.write("# Arlington County Expanded Housing Option (EHO) Permit & Construction Report\n\n")
        f.write("This report provides a comprehensive overview of all Expanded Housing Option (EHO) permit properties in Arlington County. ")
        f.write("It details whether the property has an approved EHO permit, the status of actual multi-unit or single-family construction permits, ")
        f.write("whether construction is underway or complete, and references to development project tracking.\n\n")

        f.write("## Executive Summary\n\n")

        total = len(df)
        approved = len(df[df['EHO_Permit_Status'] == 'Approved'])
        pending_void = total - approved

        underway = len(df[df['Construction_Status'].str.contains('Underway', case=False)])
        complete = len(df[df['Construction_Status'].str.contains('Complete', case=False)])
        not_started = len(df[df['Construction_Status'].str.contains('Not Started', case=False)])
        demo_prep = len(df[df['Construction_Status'].str.contains('Demolition', case=False)])

        f.write(f"- **Total Unique EHO Properties Tracked**: {total}\n")
        f.write(f"- **EHO Permit Approved**: {approved}\n")
        f.write(f"- **EHO Permit Not Approved yet (Pending/Void/Withdrawn/Other)**: {pending_void}\n")
        f.write(f"- **Construction Complete**: {complete}\n")
        f.write(f"- **Construction Underway**: {underway}\n")
        f.write(f"- **Demolition/Site Prep**: {demo_prep}\n")
        f.write(f"- **Not Started**: {not_started}\n\n")

        f.write("## 1. Approved EHO Permit Properties\n")
        f.write("Below are the properties that have at least one **Approved** EHO permit. ")
        f.write("We examine whether they are building a multi-unit structure or a single-family home instead, and current construction status.\n\n")

        approved_df = df[df['EHO_Permit_Status'] == 'Approved']
        write_table(f, approved_df)

        f.write("\n## 2. Pending / Void / Other EHO Permit Properties\n")
        f.write("Below are the properties where an EHO permit has been filed but is not yet approved (e.g. Awaiting Plans, Void, Withdrawn, Denied).\n\n")

        pending_df = df[df['EHO_Permit_Status'] != 'Approved']
        write_table(f, pending_df)

def write_table(f, df_sub):
    if df_sub.empty:
        f.write("*No properties in this category.*\n")
        return

    f.write("| Address | RPC / Parcel | EHO Permits & Status | Multi-Unit Permit | Single-Family Permit | Development Project | Construction Status |\n")
    f.write("| --- | --- | --- | --- | --- | --- | --- |\n")

    for _, row in df_sub.iterrows():
        # Escape markdown pipe chars
        addr = row['Address'].replace('|', '\\|')
        rpc = row['RPC'].replace('|', '\\|')
        eho_p = row['EHO_Permits'].replace('|', '\\|')
        multi_p = row['Multi_Unit_Permit'].replace('|', '\\|')
        sfd_p = row['SFD_Permit'].replace('|', '\\|')
        dev_proj = row['Development_Project'].replace('|', '\\|')
        const_status = row['Construction_Status'].replace('|', '\\|')

        # Clean up lists/separators for better visual appearance in table
        f.write(f"| {addr} | {rpc} | {eho_p} | {multi_p} | {sfd_p} | {dev_proj} | {const_status} |\n")

if __name__ == '__main__':
    main()
