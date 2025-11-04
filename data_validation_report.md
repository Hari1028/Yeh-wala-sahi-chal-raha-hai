# 🗂️ Multi-Sheet Validation Report: 'ironclad.xlsx'
**Processed At:** 2025-11-03T16:59:21.623341+00:00


---

## 📈 Report for Sheet: `FileInfo`

### Sheet at a Glance
| Metric | Value |
| :--- | :--- |
| Validation Status | **Failed** |
| Data Quality Score | **45 (Grade: D)** |
| Target Table (Inferred) | `customer_orders` |
| High Severity Issues | 2 |
| Medium Severity Issues | 1 |
| Total Rows Checked | 4186 |
### 🎯 Overall Analysis

> **The current data is NOT ready for production use due to significant schema and quality issues, especially missing primary keys and inconsistent data types. The biggest business risk is the potential for order record duplication or loss, which could severely impact order processing and reporting accuracy.**

### 📊 Data Quality Score: 45 / 100 (Grade: D)
**Reasoning:** The presence of null 'OrderID's and the type mismatch in 'Quantity' (float instead of integer) pose significant risks of data integrity and key duplication, which could lead to order record corruption or loss. Additionally, the extraneous columns and inconsistent source schema indicate poor data extraction and mapping, further undermining data reliability for operational use.

###  triage_plan
| Priority | Action | Reasoning |
| :--- | :--- | :--- |
| **1** | Implement a robust extraction process to parse 'OrderID' from 'File Name' or 'File Path In Lakehouse'. | Null 'OrderID's directly threaten data integrity and key uniqueness, blocking reliable order tracking and reporting. |
| **2** | Remove irrelevant columns ('Folder Name', 'File Name', 'File Path In Lakehouse') from the data load pipeline. | Extraneous columns increase schema pollution and risk misinterpretation during ETL, leading to downstream errors. |
| **3** | Validate and enforce data types, especially converting 'Quantity' to INTEGER and ensuring all required fields are populated. | Type mismatches and missing values in critical fields can cause calculation errors and failed downstream processes. |
| **4** | Establish a source-to-target mapping document, especially for key identifiers like 'OrderID' and 'Quantity'. | Clear mapping reduces semantic errors and ensures data consistency across systems. |

--- 
## 1. Schema Mismatch Analysis
**Analysis:** The validation reveals that the source file contains columns unrelated to the target schema, with some columns like 'Folder Name', 'File Name', and 'File Path In Lakehouse' being extraneous, and several target columns missing. Notably, 'OrderID' appears to be represented by multiple file-related columns, indicating a semantic mapping issue.

#### Columns Missing from File (Required by Table):
- `OrderID`
- `CustomerID`
- `OrderDate`
- `Quantity`
- `Price`
- `DiscountCode`

#### Extra Columns Found in File (Not in Table):
- `file_size`
- `Folder Name`
- `File Path In Lakehouse`
- `File Name`
- `File Size in MB`

#### Suggested Naming Mappings:
- Map `Folder Name` (file) to `OrderID` (table)
- Map `File Name` (file) to `OrderID` (table)
- Map `File Path In Lakehouse` (file) to `OrderID` (table)
- Map `File Size in MB` (file) to `Quantity` (table)

#### Recommendations:
- `Implement a data extraction process to parse 'OrderID' from 'File Name' or 'File Path In Lakehouse' to ensure the primary key is correctly captured.`
- `Remove or ignore irrelevant columns such as 'Folder Name', 'File Name', and 'File Path In Lakehouse' during data ingestion to prevent schema pollution.`
- `Verify that the source data includes all required fields ('OrderID', 'CustomerID', 'OrderDate', 'Quantity', 'Price', 'DiscountCode') and that they are correctly populated and typed.`
- `Establish a mapping document that clearly links source columns (or derived fields) to target schema columns, especially for 'OrderID' and 'Quantity'.`
- `Validate the source data extraction logic to ensure semantic accuracy, particularly for key identifiers and numeric fields.`

--- 
## 2. Data Quality Violations
No data quality violations found.

--- 
## 3. Data Type Violations

- **Column: `Quantity`**
  - **Expected Type (DB):** `INTEGER`
  - **Found Type (File):** `float64`
  - **Invalid Samples:** `[]`

--- 
## 4. Root Cause Analysis
**Hypothesis:** The pattern of null 'OrderID's, extraneous file-related columns, and inconsistent data types suggests that the source data is manually compiled or exported from a file system without proper schema enforcement. This likely stems from manual CSV or Excel uploads where 'OrderID' is embedded in file names, not explicitly stored in the data, leading to extraction errors and missing primary keys.

--- 
## 5. Suggested Load Strategy
- **Strategy:** `UPSERT`
- **Key Column:** `OrderID`
- **Reasoning:** Upserting based on 'OrderID' allows incremental updates and prevents duplicate records, but requires that 'OrderID' be reliably extracted and validated first.

--- 
## 6. Schema Drift
**Drift Detected:** `True`
**Analysis:** The historical schemas show that 'OrderID' was previously inferred as 'object' with consistent sample values, but current null counts and the embedding of 'OrderID' in file names suggest a drift in data source structure and extraction logic, indicating schema evolution or inconsistent data ingestion.

--- 
## 7. Inferred Validation Rules
| Column | Rule Type | Details | Inferred From |
| :--- | :--- | :--- | :--- |
| `Folder Name` | `format_check` | Samples contain a mix of alphanumeric codes, dates, and embedded identifiers. A potential regex could be used to validate the presence of date formats (e.g., \d{2}\.\d{2}\.\d{2}) and alphanumeric patterns, but no strict format is evident. Validation could include ensuring presence of date and identifier patterns. | `[' Balzer & Associates - WO - 2023.11 (IC-929).10', '000414572  017.0000033211 (IC-4791)', '01.23.25 030.32425_Orig_$5500  030.0000033839 (IC-4571)', '01.30.25_030.32425_PO P202500602_$5500  030.0000033839 (IC-4569)', '011.0000034644 Proposal and WA (IC-4535)']` |
| `File Name` | `format_check` | File names include alphanumeric codes, dates, and descriptors. A regex could validate date formats (e.g., \d{4}-\d{2}-\d{2}) and presence of specific keywords like '(signedCopy)'. Case sensitivity may vary; validation should accommodate both .pdf and .PDF extensions. | `['19362 Verdantas Work Order_2023-11-10 (signedCopy).pdf', '000414572  017.0000033211 (signedCopy).pdf', '01.23.25 030.32425_Orig_$5500  030.0000033839 (signedCopy).pdf', '01.30.25_030.32425_PO P202500602_$5500  030.0000033839 (signedCopy).PDF', '011.0000034644 Proposal and WA (signedCopy).pdf']` |
| `File Path In Lakehouse` | `format_check` | Paths contain nested directories with alphanumeric and date patterns, as well as embedded identifiers. Validation could include ensuring consistent directory structure and presence of date and identifier patterns within folder names and filenames. | `['/lakehouse/default/Files/IronClad_Contracts/ Balzer & Associates - WO - 2023.11 (IC-929).10/19362 Verdantas Work Order_2023-11-10 (signedCopy).pdf', '/lakehouse/default/Files/IronClad_Contracts/000414572  017.0000033211 (IC-4791)/000414572  017.0000033211 (signedCopy).pdf', '/lakehouse/default/Files/IronClad_Contracts/01.23.25 030.32425_Orig_$5500  030.0000033839 (IC-4571)/01.23.25 030.32425_Orig_$5500  030.0000033839 (signedCopy).pdf', '/lakehouse/default/Files/IronClad_Contracts/01.30.25_030.32425_PO P202500602_$5500  030.0000033839 (IC-4569)/01.30.25_030.32425_PO P202500602_$5500  030.0000033839 (signedCopy).pdf', '/lakehouse/default/Files/IronClad_Contracts/011.0000034644 Proposal and WA (IC-4535)/011.0000034644 Proposal and WA (signedCopy).pdf']` |
| `file_size` | `range_check` | Sample file sizes range from approximately 45 KB to 1.8 MB. A validation rule could enforce that file sizes are within a reasonable range, e.g., between 50 KB and 2 MB, to catch corrupted or incomplete files. | `[1799359, 45449, 822151, 100095, 857546]` |
| `File Size in MB` | `range_check` | Sample values range from approximately 0.04 MB to 1.72 MB. Validation could specify acceptable file size range, e.g., 0.05 MB to 2 MB, to identify anomalously small or large files. | `[1.7160024642944336, 0.043343544006347656, 0.7840642929077148, 0.0954580307006836, 0.8178195953369141]` |


---

## 📈 Report for Sheet: `Metadata`

### Sheet at a Glance
| Metric | Value |
| :--- | :--- |
| Validation Status | **Failed** |
| Data Quality Score | **40 (Grade: F)** |
| Target Table (Inferred) | `customer_orders` |
| High Severity Issues | 2 |
| Medium Severity Issues | 2 |
| Total Rows Checked | 3944 |
### 🎯 Overall Analysis

> **The current data is NOT fit for production use due to critical missing and inconsistent fields that threaten operational integrity. The biggest business risk is the potential for order processing failures and missed customer notifications caused by null and malformed key data points.**

### 📊 Data Quality Score: 40 / 100 (Grade: F)
**Reasoning:** The presence of null 'OrderID' and 'CustomerEmail' fields, which are critical for order tracking and customer communication, poses high business risks such as data loss and failed notifications. Additionally, inconsistent data types (e.g., 'qty' as string 'one') and invalid email formats further compromise data integrity, leading to unreliable reporting and operational errors. These issues significantly undermine the trustworthiness of the data, resulting in a failing score.

###  triage_plan
| Priority | Action | Reasoning |
| :--- | :--- | :--- |
| **1** | Immediately implement validation checks to ensure 'OrderID' and 'CustomerID' are non-null and unique before data ingestion. | Null 'OrderID' prevents unique identification of orders, risking data corruption and operational failures. |
| **2** | Standardize data types for key fields such as 'Quantity' (convert to numeric) and validate email formats for 'CustomerEmail'. | Inconsistent data types and invalid emails can cause processing errors and failed customer communications. |
| **3** | Filter out irrelevant extraneous columns during import and review data collection processes for completeness. | Extraneous columns and missing core data indicate poor data collection practices, risking confusion and data pollution. |

--- 
## 1. Schema Mismatch Analysis
**Analysis:** The file schema is missing core order data columns and contains numerous extra, unrelated columns. Six key columns ('OrderID', 'CustomerID', 'DiscountCode', 'OrderDate', 'Price', 'Quantity') are missing from the source file, which are essential for business operations. The file has many extraneous columns that are not part of the target schema, indicating potential data collection or extraction issues.

#### Columns Missing from File (Required by Table):
- `OrderID`
- `CustomerID`
- `DiscountCode`
- `OrderDate`
- `Price`
- `Quantity`

#### Extra Columns Found in File (Not in Table):
- `Lien Searches`
- `Workflow Completion Duration (ms)`
- `Operating Expenses`
- `Renewal Opt Out Date`
- `Document for Review`
- `Workflow Participant Ids`
- `Workflow Internal Signer Names`
- `Termination`
- `Term`
- `Counterparty Address Region`
- `Renewal Opt Out Period`
- `Sign Step Duration (ms)`
- `Arbitration`
- `Autorenewal Cancellation Date`
- `No Other Liens`
- `Executed Date`
- `Repository Link`
- `Workflow Paused Duration (ms)`
- `Notice Of Termination`
- `New Jersey LSRP`
- `Status Override`
- `Assignee Names`
- `MOA Risk`
- `Suspensions`
- `Paper Source`
- `Non Exclusivity (Playbook Clause)`
- `Verdantas Contract Number`
- `Last Activity Date`
- `Project Location (Address) Locality`
- `Counterparty Address Country`
- `Change of Control (Playbook Clause)`
- `Waiver Of Consequential Damages (Playbook Clause)`
- `Contract Status`
- `Terminating Record Id`
- `Turn Tracking Time With Internal (ms)`
- `Workflow Configuration Id`
- `Workflow Completed Date`
- `Survival Of Agreements`
- `Nuclear QA Program Review`
- `AI Assist Language Included`
- `Project Location (Address) Region`
- `Workflow Review Step Completed Date`
- `Renewal Term Length`
- `Waiver Of Subrogation`
- `Number of Approvals`
- `Contract Extending`
- `Snippets`
- `Agreement Term`
- `Governing Law (Clause)`
- `Average Approval Time (ms)`
- `Assignment`
- `Regulatory Permits`
- `Counterparty Address Locality`
- `Workflow Signature Coordinator Emails`
- `Workflow Link`
- `Government Regulations`
- `Taxes`
- `Auto Renewal`
- `Additional Documents`
- `Return of Confidential Information`
- `Counterparty Address Line 4`
- `Execution Method`
- `Superseded Date`
- `Liabilities Or Developments`
- `Confidentiality`
- `Counterparty Address Postcode`
- `Renewals`
- `Workflow Creator Name`
- `Project Location (Address) Line 4`
- `Survival Of Representations`
- `Record Type`
- `Standard of Care (Clause)`
- `Renewal Term`
- `Counterparty Address`
- `Counterparty Address Line 1`
- `Renewal Approval Date`
- `Usage (Clause)`
- `Review Step Duration (ms)`
- `Last Activity Action`
- `Execution Time (ms)`
- `Usage (Playbook Clause)`
- `Workflow Internal Signer Emails`
- `Non Exclusivity (Clause)`
- `Original Filename`
- `Request Urgency`
- `Payment Frequency`
- `Workflow Internal Signer Ids`
- `Workflow Creator Id`
- `Prediction Date`
- `Termination For Convenience (Clause)`
- `Project Location (Address)`
- `Workflow Configuration Version Number`
- `Average Turn Time with Counterparty (ms)`
- `Intellectual Property`
- `Counterparty Signer Email`
- `Govt Entity Client`
- `Risk Levels`
- `Project Name`
- `Terminated Date`
- `Workflow Sign Step Completed Date`
- `Anniversary Date`
- `Payment Of Obligations (Playbook Clause)`
- `Create Step Duration (ms)`
- `Assignee Emails`
- `Remedies`
- `Current Turn Party`
- `Counterparty Address Line 2`
- `Opt Out Length`
- `Counterparty Signer Name`
- `Entity`
- `Workflow Archiver Emails`
- `Counterparty Signer Yes/No`
- `Premises`
- `Standard of Care (Playbook Clause)`
- `Stage`
- `Record Type Id`
- `Right Of Setoff`
- `Force Majeure`
- `Termination For Convenience (Text)`
- `Other Documents`
- `Turn Tracking Time With Counterparty (ms)`
- `Prime Agreement (Yes/No)`
- `Supersession Effective Date`
- `Representation`
- `Breach`
- `Workflow ID`
- `Record Name`
- `Notice`
- `Payment Of Obligations (Clause)`
- `Requester Name`
- `Maintenance Of Insurance`
- `Link to Additional Documents`
- `Counterparty Address Line 3`
- `Fees`
- `Parent Id`
- `Notice Of Defaults`
- `Termination For Breach`
- `Verdantas Signor / Approval`
- `Total Internal Turns`
- `Venue`
- `Superseding Record Id`
- `Release Of Liens`
- `Renewal Approval Required`
- `License (Playbook Clause)`
- `Verdantas Sub ID Number`
- `Whether Additional Documents`
- `Number of Signers`
- `Additional Notes`
- `Exclusive Remedy`
- `Request Description`
- `Change of Control (Clause)`
- `Acceptance Type`
- `Use Of Names (Clause)`
- `Bankruptcy`
- `Signed PDF`
- `Agreement Date`
- `Governing Law (Text)`
- `Total Counterparty Turns`
- `Insurance`
- `Project Coordinator`
- `Request Resolution`
- `Termination Notice Period (Text)`
- `Workflow Participant Names`
- `Connect Workflow`
- `Ironclad Import ID`
- `Verdantas Signor / Approval`
- `Termination For Cause (Clause)`
- `Limitation of Liability (Playbook Clause)`
- `Project Location (Address) Country`
- `Stage Index`
- `Indemnification (Clause)`
- `Project Location (Address) Postcode`
- `Attorney Fees`
- `Workflow Approver Emails`
- `Average Turn Time with Internal (ms)`
- `Mediation`
- `Start over from Template`
- `Counterparty Signer Title`
- `Indemnification (Playbook Clause)`
- `Project Location (Address) Line 2`
- `Termination For Cause (Yes/No)`
- `Workflow Created Date`
- `Times Renewed`
- `Workflow Configuration Name`
- `Workflow Owner Id`
- `Workflow Owner Name`
- `Workflow Signature Coordinator Ids`
- `Workflow Creator Email`
- `Limitation of Liability (Clause)`
- `Termination Effective Date`
- `Prime Agreement (File)`
- `Record Id`
- `License (Clause)`

#### Suggested Naming Mappings:
- Map `OrderID` (file) to `OrderID` (table)
- Map `CustomerID` (file) to `CustomerID` (table)
- Map `DiscountCode` (file) to `DiscountCode` (table)
- Map `OrderDate` (file) to `OrderDate` (table)
- Map `Price` (file) to `Price` (table)
- Map `Quantity` (file) to `Quantity` (table)

#### Recommendations:
- `Map 'OrderID', 'CustomerID', 'OrderDate', 'Price', and 'Quantity' from the source file to the target schema, ensuring these columns are present and correctly populated.`
- `Add missing core order columns to the source file or set default values where appropriate, and verify data completeness.`
- `Filter out or ignore extraneous columns not relevant to the order data during import to prevent data pollution.`
- `Implement validation checks to ensure key order fields are non-null and correctly formatted before loading.`
- `Review data collection processes to ensure all critical order information is captured consistently in the source file.`

--- 
## 2. Data Quality Violations
No data quality violations found.

--- 
## 3. Data Type Violations
No data type mismatches found.

--- 
## 4. Root Cause Analysis
**Hypothesis:** The pattern of missing core order data ('OrderID', 'OrderDate') combined with extraneous, unrelated columns suggests a manual data entry or spreadsheet export process that is not aligned with the target schema. This indicates a likely root cause of manual CSV or Excel uploads from non-automated sources, rather than a systematic API or automated pipeline.

--- 
## 5. Suggested Load Strategy
- **Strategy:** `UPSERT`
- **Key Column:** `OrderID`
- **Reasoning:** Using 'OrderID' as the key allows for updating existing records and maintaining data consistency, which is critical given the nulls and inconsistencies observed.

--- 
## 6. Schema Drift
**Drift Detected:** `True`
**Analysis:** Compared to historical schemas, the current schema shows a significant increase in extraneous columns unrelated to order processing, such as 'Lien Searches' and 'Workflow Completion Duration'. The core order columns like 'OrderID' and 'OrderDate' are missing or inconsistent, indicating schema drift likely due to uncoordinated data collection or extraction processes.

--- 
## 7. Inferred Validation Rules
| Column | Rule Type | Details | Inferred From |
| :--- | :--- | :--- | :--- |
| `Record Id` | `format_check` | Based on sample values, this column appears to follow the format 'workflow:' followed by a 24-character alphanumeric string. | `['workflow:67a62d68d5fd644eceb4b7f7', 'workflow:67a54a40a4b42a3fce199e96']` |
| `Workflow Id` | `null_check` | Samples show that this column is often null; nulls are common, indicating optional presence. | `['67a62d68d5fd644eceb4b7f7', '67a54a40a4b42a3fce199e96']` |
| `Ironclad Id` | `format_check` | Samples suggest the format 'IC-' followed by 4 digits. | `['IC-3564', 'IC-3563']` |
| `Record Name` | `format_check` | Samples contain a pattern with organization name, description, date in YYYY.MM.DD format, and an alphanumeric code at the end. | `['ATI Inc. - Agreement/PO - 2025.03.24 - 011.P000032443', 'Subsurface Surveys - Subcontractor Agreement - 2025.03.31']` |
| `Parent Id` | `format_check` | Values are either UUIDs in standard hyphenated format or strings starting with 'workflow:'. | `['f206b3cc-62dd-4a73-8068-97ac7a5546fc', 'workflow:6756fddf5c5c6effae0a23d0']` |
| `Related Record Ids` | `null_check` | Samples show high null count, indicating optional presence; no strict format inferred. | `['b780719c-cc04-48f9-b3e2-90b8302c10a3', 'workflow:67ff955ec302f3d82eb6c6be']` |
| `Record Type Id` | `enum_check` | Samples indicate this column contains categorical values from a specific set of record type identifiers. | `['consultantServiceAgreementClientMasterUse', 'subcontractorAgreementMasterUse']` |
| `Record Type` | `enum_check` | Samples show categorical values from a fixed list of agreement types. | `['Consultant / Service Agreement - Client Master Use', 'Subcontractor Agreement - Master Use']` |
| `Workflow Configuration Name` | `enum_check` | Samples are from a predefined list of workflow configuration names. | `['Document Review Request', 'RFP / RFQ / RFI Submission']` |
| `Workflow Configuration Id` | `format_check` | Values are alphanumeric strings of length 24, likely UUIDs. | `['65e0e3d4cfe4b4de0c906c5b', '6632cc823d41a053019840d7']` |
| `Attachment Filenames` | `format_check` | Samples are filenames with descriptive text, possibly including parentheses, hyphens, and file extensions like .pdf. | `['PO_8107557_-_Ts_and_Cs_-_Revised.pdf\nPO 8107557.pdf', 'Subsurface Surveys - Subcontractor Agreement - Master Use (67a54a4e96).pdf']` |
| `Snippets` | `null_check` | Samples are empty; nulls are frequent, indicating optional or missing data. | `[]` |
| `Workflow Link` | `format_check` | Sample value is a fixed string; likely a placeholder or static link. | `['Link to Workflow']` |
| `Repository Link` | `format_check` | Sample value is a fixed string; likely a placeholder or static link. | `['Link to Repository']` |
| `Workflow Owner Id` | `format_check` | Values are UUIDs in hyphenated format. | `['6706ba5cb002b0986445d015', '670ee9ab43798a5c0dd0cd98']` |
| `Workflow Owner Email` | `format_check` | Samples follow standard email format with username@domain. | `['dgiza@verdantas.com', 'mpriestaf@verdantas.com']` |
| `Workflow Owner Name` | `null_check` | Names are free text; no strict format but non-null for valid entries. | `['Dan Giza', 'Michael Priestaf']` |
| `Stage Index` | `range_check` | Single sample suggests numeric, likely integer, with expected range starting from 1 upwards. | `['4.0']` |
| `Stage` | `enum_check` | Sample indicates categorical status; likely limited set of statuses such as 'completed'. | `['completed']` |
| `Execution Time (ms)` | `range_check` | Values are large integers representing milliseconds; range check suggests values typically in the billions. | `['6301581341.0', '8192668815.0']` |
| `Last Activity Date` | `datetime_check` | Samples are in ISO datetime format with microsecond precision; date range likely within current/future years. | `['2025-05-13 12:38:35.870000', '2025-05-13 10:59:20.530000']` |
| `Last Activity Action` | `enum_check` | Values are from a fixed set of action descriptions, indicating categorical data. | `['Abbie commented', 'Contract archived']` |
| `Stage` | `enum_check` | Sample indicates a categorical status, likely limited to specific values such as 'completed'. | `['completed']` |
| `Workflow Creator Id` | `format_check` | Values are UUIDs in hyphenated format. | `['6706ba5cb002b0986445d015', '670ee9ab43798a5c0dd0cd98']` |
| `Workflow Creator Email` | `format_check` | Samples follow standard email format. | `['dgiza@verdantas.com', 'mpriestaf@verdantas.com']` |
| `Workflow Creator Name` | `null_check` | Names are free text; non-null for valid entries. | `['Dan Giza', 'Michael Priestaf']` |
| `Stage` | `enum_check` | Values are categorical, with 'completed' as a sample status. | `['completed']` |
| `Workflow Signature Coordinator Ids` | `format_check` | Values are UUIDs in hyphenated format. | `['65aeae93bd3b449cf1fcc324', '65aabcaba572f8d93f0cc2a9']` |
| `Workflow Signature Coordinator Emails` | `format_check` | Samples follow email format. | `['aknaub@verdantas.com', 'cprice@verdantas.com']` |
| `Workflow Signature Coordinator Names` | `null_check` | Names are free text; non-null for valid entries. | `['Abbie Ficsor', 'Coby Price']` |
| `Contract Status` | `enum_check` | Values are from a fixed list of contract statuses. | `['expiring', 'executed', 'auto-renewing']` |
| `Agreement Date` | `date_format_check` | Samples are in ISO date format YYYY-MM-DD. | `['2025-04-21', '2025-05-12']` |
| `Attachment` | `null_check` | High null count; likely optional or missing data. | `[]` |
| `Agreement Term` | `format_check` | Samples contain duration descriptions with number and unit, e.g., 'years' or '(3) years'. | `['three (3) years', '3 years']` |
| `Effective Date` | `date_format_check` | Samples are in ISO date format YYYY-MM-DD. | `['2025-03-31', '2025-01-01']` |
| `Superseding Record Id` | `format_check` | Values are either UUIDs or descriptive strings with date in YYYY.MM.DD format. | `['IC-2301', 'IRG Realty - MSA - 2024.07.15']` |
| `Supersession Effective Date` | `date_format_check` | Samples are in ISO date format YYYY-MM-DD. | `['2024-07-15', '2024-10-23']` |
| `Termination Notice Period (Duration)` | `format_check` | Values follow ISO 8601 duration format starting with 'P' followed by number and unit (D for days). | `['P10D', 'P30D']` |
| `Times Renewed` | `range_check` | Values are numeric, typically small integers, indicating count of renewals. | `['15.0', '4.0']` |
| `Number of Approvals` | `range_check` | Values are small integers, indicating approval count, expected within a reasonable range. | `['1.0', '3.0']` |
| `Workflow Configuration Version Number` | `range_check` | Values are numeric, likely integer or float, within a small range indicating version numbers. | `['148.0', '137.0']` |
| `Workflow Created Date` | `date_format_check` | Samples are in ISO date format YYYY-MM-DD. | `['2025-02-07', '2025-02-06']` |
| `Start over from Template` | `enum_check` | Sample indicates binary flag, likely 0 or 1. | `['0.0']` |
| `AI Assist Language Included` | `enum_check` | Sample indicates binary flag, likely 0 or 1. | `['0.0']` |
| `Connect Workflow` | `enum_check` | Sample indicates binary flag, likely 0 or 1. | `['0.0']` |
| `Final Draft on Template` | `enum_check` | Values are binary flags, 0 or 1. | `['0.0', '1.0']` |
| `Number of Signers` | `range_check` | Values are small integers, indicating signer count, expected within a small range. | `['1.0', '3.0']` |
| `Reverted to Review` | `enum_check` | Binary flag, 0 or 1. | `['0.0', '1.0']` |
| `Workflow Review Step Completed Date` | `date_format_check` | Samples are in ISO date format YYYY-MM-DD. | `['2025-04-17', '2025-02-25']` |
| `Signature Provider` | `enum_check` | Values are from a fixed set of signature providers. | `['DocuSign', 'Ironclad Signature']` |
| `Workflow Sign Step Completed Date` | `date_format_check` | Samples are in ISO date format YYYY-MM-DD. | `['2025-04-21', '2025-05-13']` |
| `Workflow Completed Date` | `date_format_check` | Samples are in ISO date format YYYY-MM-DD. | `['2025-05-13', '2025-05-06']` |
| `Number of Turns` | `range_check` | Values are small integers, indicating turn count, expected within a small range. | `['1.0', '3.0']` |
| `Total Counterparty Turns` | `range_check` | Values are small integers, indicating total counterparty turns, expected within a small range. | `['0.0', '4.0']` |
| `Total Internal Turns` | `range_check` | Values are small integers, indicating internal turns, expected within a small range. | `['1.0', '4.0']` |