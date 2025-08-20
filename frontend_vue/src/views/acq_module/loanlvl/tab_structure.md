loanlvl_index is the master wrapper for the loan-level UI. It provides the Hyper UI Layout/Breadcrumb shell for full-page usage and hosts the loan-level tabs (Snapshot, Property Details, Loan Details, Acquisition Analysis). It also centralizes the modal-related global styles (dialog/content sizing), so other components (e.g., data grid) remain clean and grid-only.

* LoanTabs.vue is the component that hosts the loan-level tabs (Snapshot, Property Details, Loan    Details, Acquisition Analysis, documents).

    * LoanTabSnapshot.vue is the component that hosts the Snapshot tab content for the acquisitions 
     product details modal.

    * LoanTabPropertyDetails.vue is the component that hosts the Property Details tab content for the 
     acquisitions product details modal.

    * LoanTabLoanDetails.vue is the component that hosts the Loan Details tab content for the 
     acquisitions product details modal.

    * LoanTabAcquisitionAnalysis.vue is the component that hosts the Acquisition Analysis tab content 
     for the acquisitions product details modal.

    * LoanTabDocuments.vue is the component that hosts the documents tab content for the acquisitions 
     product details modal.
