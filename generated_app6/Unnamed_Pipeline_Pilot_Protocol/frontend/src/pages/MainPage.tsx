
import React, { useState, ChangeEvent, FormEvent,useMemo } from 'react';
import headerImg from '../assets/blank-header.png';
import footerImg from '../assets/page-footer-with-logo.png';
import Header from '../components/Header';
import Footer from '../components/Footer';
// Define types for parsed files and import results
interface ParsedFile {
    id: string;
    name: string;
    type: string;
    file_path: string;
    section_title?: string;
}

interface ImportResult {
    fileId: string;
    fileName: string;
    success: boolean;
    message: string;
}

const ELNFileImporter: React.FC = () => {
    // Fetch the Params
    const queryParams = useMemo(() => {
        const params = new URLSearchParams(window.location.search);

        return {
            experimentId: params.get('experimentId') || '',
            documentId: params.get('documentId') || '',
            userId: params.get('userId') || '',
            notebookId: params.get('notebookId') || '',
        };
    }, []);
    console.log("Query Params:", queryParams);
    // State for XML file upload
    const [xmlFile, setXmlFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState<boolean>(false);
    const [uploadError, setUploadError] = useState<string | null>(null);

    // State for parsed files list
    const [parsedFiles, setParsedFiles] = useState<ParsedFile[]>([]);
    const [selectedFileIds, setSelectedFileIds] = useState<Set<string>>(new Set());

    // State for experiment selection (assuming a simple input for now)
    // commenting to use the url param
    //const [experimentId, setExperimentId] = useState<string>('EXP-001'); // Default experiment ID
    const [experimentId, setExperimentId] = useState<string>(queryParams.experimentId);
    // State for import process
    const [isImporting, setIsImporting] = useState<boolean>(false);
    const [importResults, setImportResults] = useState<ImportResult[]>([]);
    const [importError, setImportError] = useState<string | null>(null);

    // --- Workflow Step 1 & 2: Upload XML & Parse XML ---
    const handleXmlFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setXmlFile(event.target.files[0]);
            // Reset previous states
            setParsedFiles([]);
            setSelectedFileIds(new Set());
            setUploadError(null);
            setImportResults([]);
            setImportError(null);
        }
    };

    const handleUploadXml = async (event: FormEvent) => {
        event.preventDefault();
        if (!xmlFile) {
            setUploadError('Please select an XML file to upload.');
            return;
        }

        setIsUploading(true);
        setUploadError(null);
        setParsedFiles([]);
        setSelectedFileIds(new Set());

        try {
            const formData = new FormData();
            formData.append('xml_file', xmlFile);

            // API call to upload and parse XML
            // This assumes /api/custom-filter-(pilotscript) can handle XML upload and return parsed file metadata
            const response = await fetch('http://localhost:8000/api/custom-filter-(pilotscript)', {
                method: 'POST',
                body: formData, // Sending FormData for file upload
                // headers: { 'Content-Type': 'application/xml' } if sending plain XML,
                // but FormData is common for file uploads
            });
            console.log("RESPONSE", response);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to parse XML file.');
            }

            const data: { files: ParsedFile[] } = await response.json();
            console.log(data);
            setParsedFiles(data.files || []);
            setSelectedFileIds(new Set(data.files.map(f => f.id))); // Select all by default

        } catch (error: any) {
            setUploadError(error.message || 'An unknown error occurred during XML upload and parsing.');
            console.error('XML Upload/Parse Error:', error);
        } finally {
            setIsUploading(false);
        }
    };

    // --- Workflow Step 3: Select Files ---
    const handleFileSelectionChange = (fileId: string) => {
        setSelectedFileIds(prevSelected => {
            const newSelection = new Set(prevSelected);
            if (newSelection.has(fileId)) {
                newSelection.delete(fileId);
            } else {
                newSelection.add(fileId);
            }
            return newSelection;
        });
    };

    const handleSelectAllChange = (event: ChangeEvent<HTMLInputElement>) => {
        if (event.target.checked) {
            setSelectedFileIds(new Set(parsedFiles.map(f => f.id)));
        } else {
            setSelectedFileIds(new Set());
        }
    };

    // --- Workflow Step 4: Attach To ELN ---
    const handleImportSelectedFiles = async () => {
        if (selectedFileIds.size === 0) {
            setImportError('Please select at least one file to import.');
            return;
        }
        if (!experimentId) {
            setImportError('Please provide an Experiment ID.');
            return;
        }

        setIsImporting(true);
        setImportError(null);
        setImportResults([]);
        const currentImportResults: ImportResult[] = [];

        for (const fileId of selectedFileIds) {
            const fileToImport = parsedFiles.find(f => f.id === fileId);
            if (!fileToImport) continue;
            console.log("data type:",fileToImport.type )
            let endpoint: string;
            switch (fileToImport.type) {
                case 'pdf':
                    endpoint = 'http://localhost:8000/api/import-files-to-eln';
                    break;
                case 'xlsx':
                    endpoint = 'http://localhost:8000/api/import-files-to-eln';
                    break;
                case 'docx':
                    endpoint = 'http://localhost:8000/api/import-files-to-eln';
                    break;
                case 'pptx':
                    endpoint = 'http://localhost:8000/api/import-files-to-eln';
                    break;
                default:
                    endpoint = 'http://localhost:8000/api/import-files-to-eln';
                    // currentImportResults.push({
                    //     fileId: fileToImport.id,
                    //     fileName: fileToImport.name,
                    //     success: false,
                    //     message: `Unsupported file type: ${fileToImport.type}`,
                    // });
                    //continue;
                    break;
            }

            try {
                // Assuming the add-section APIs take experimentId and fileId
                // console.log("FILE TO IMPORT", fileToImport);
                // console.log("PAYLOAD", {
                //     experimentId,
                //     fileId: fileToImport.id,
                // });
                // const payload = {
                //     experiment_id: experimentId,
                //     selected_files: [
                //         {
                //             id: fileToImport.id,
                //             file_path: fileToImport.file_path,
                //             file_type: fileToImport.type,
                //             section_title: fileToImport.section_title
                //         }
                //     ]
                // };
                const payload = {
                    experiment_id: experimentId,
                    document_id: queryParams.documentId,
                    user_id: queryParams.userId,
                    notebook_id: queryParams.notebookId,

                    selected_files: [
                        {
                            id: fileToImport.id,
                            file_path: fileToImport.file_path,
                            file_type: fileToImport.type,
                            section_title: fileToImport.section_title
                        }
                    ]
                };
                console.log(
                    "IMPORT PAYLOAD",
                    JSON.stringify(payload, null, 2)
                );

                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                if (!response.ok) {
                    const errorData = await response.json();

                    console.error(
                        "IMPORT ERROR RESPONSE",
                        JSON.stringify(errorData, null, 2)
                    );

                    throw new Error(
                        JSON.stringify(errorData, null, 2)
                    );
                }

                const result = await response.json();
                currentImportResults.push({
                    fileId: fileToImport.id,
                    fileName: fileToImport.name,
                    success: result.success || true, // Assume success if response is ok
                    message: result.message || `${fileToImport.name} imported successfully.`,
                });
            } catch (error: any) {
                currentImportResults.push({
                    fileId: fileToImport.id,
                    fileName: fileToImport.name,
                    success: false,
                    message: error.message || `An error occurred importing ${fileToImport.name}.`,
                });
                console.error(`Import Error for ${fileToImport.name}:`, error);
            }
        }
        setImportResults(currentImportResults);
        setIsImporting(false);
    };

    const allFilesSelected = parsedFiles.length > 0 && selectedFileIds.size === parsedFiles.length;

    return (
        
        <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '1100px', margin: '0 auto', padding: '0px 20px 120px 20px' }}>
            <Header />
            {/* <h1>ELN External File Importer</h1>*/}

            {/* Workflow Step 1 & 2: Upload XML & Parse XML */}
            <section style={{ marginBottom: '30px', paddingBottom: '0px', borderBottom: '1px dashed #eee' }}>
                {/*<h2>1. Upload XML File</h2>*/}
                <form onSubmit={handleUploadXml}>
                    <input
                        type="file"
                        accept=".xml"
                        onChange={handleXmlFileChange}
                        disabled={isUploading}
                        style={{ marginBottom: '10px' }}
                    />
                    <button type="submit" disabled={!xmlFile || isUploading}>
                        {isUploading ? 'Parsing...' : 'Process XML'}
                    </button>
                    {isUploading && <p style={{ color: 'blue' }}>Processing XML...</p>}
                    {uploadError && <p style={{ color: 'red' }}>Error: {uploadError}</p>}
                </form>
            </section>

            {/* Workflow Step 3: Select Files */}
            {parsedFiles.length > 0 && (
                <section style={{ marginBottom: '0px', paddingBottom: '0px', borderBottom: '1px dashed #eee' }}>
                    {/*<h2>2. Select Files to Import</h2>*/}
                    <div style={{ marginBottom: '15px' }}>
                        <label>
                            {/* <strong>Experiment ID:</strong> */}
                            {/* <input
                                type="text"
                                value={experimentId}
                                onChange={(e) => setExperimentId(e.target.value)}
                                style={{ marginLeft: '10px', padding: '5px', borderRadius: '4px', border: '1px solid #ccc' }}
                            /> */}
                            {queryParams.experimentId ? (
                                <div>
                                    <strong>Experiment ID:</strong> {experimentId}
                                </div>
                            ) : (
                                <label>
                                    <strong>Experiment ID:</strong>
                                    <input
                                        type="text"
                                        value={experimentId}
                                        onChange={(e) => setExperimentId(e.target.value)}
                                        style={{
                                            marginLeft: '10px',
                                            padding: '5px',
                                            borderRadius: '4px',
                                            border: '1px solid #ccc'
                                        }}
                                    />
                                </label>
                            )}
                        </label>
                    </div>

                    <div style={{ maxHeight: '150px',width: '300px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px', borderRadius: '4px', marginBottom: '15px' }}>
                        <div style={{ borderBottom: '1px solid #eee', paddingBottom: '5px', marginBottom: '5px' }}>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={allFilesSelected}
                                    onChange={handleSelectAllChange}
                                    disabled={parsedFiles.length === 0}
                                />
                                Select All
                            </label>
                        </div>
                        {parsedFiles.map((file) => (
                            <div key={file.id} style={{ padding: '1px 0' }}>
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={selectedFileIds.has(file.id)}
                                        onChange={() => handleFileSelectionChange(file.id)}
                                    />
                                    {file.name} {/*(Type: {file.type})*/}
                                </label>
                            </div>
                        ))}
                    </div>
                    {parsedFiles.length === 0 && <p>No files found in the parsed XML.</p>}
                </section>
            )}

            {/* Workflow Step 4: Attach To ELN */}
            {parsedFiles.length > 0 && (
                <section style={{ marginBottom: '0px', marginTop: '0px' }}>
                   {/*  <h2>3. Attach Selected Files to ELN</h2>*/}
                    <button
                        onClick={handleImportSelectedFiles}
                        disabled={selectedFileIds.size === 0 || isImporting || !experimentId}
                        style={{ padding: '10px 10px', fontSize: '16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
                    >
                        {isImporting ? 'Importing...' : `Import ${selectedFileIds.size} File(s) to ELN`}
                    </button>
                    {isImporting && <p style={{ color: 'blue', marginTop: '10px' }}>Importing files to ELN...</p>}
                    {importError && <p style={{ color: 'red', marginTop: '10px' }}>Error: {importError}</p>}
                    
                    {importResults.length > 0 && (
                        <div style={{ marginTop: '20px', border: '1px solid #ddd', padding: '10px', borderRadius: '4px' }}>
                            <h3>Import Results:</h3>
                            <ul style={{ listStyleType: 'none', padding: 0 }}>
                                {importResults.map((result, index) => (
                                    <li key={index} style={{ color: result.success ? 'green' : 'red', marginBottom: '5px' }}>
                                        {result.fileName}: {result.message}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </section>
            )}

            {/* Overall status indicators */}
            {(isUploading || isImporting) && (
                <div style={{ position: 'fixed', top: '20px', right: '20px', backgroundColor: '#ffc107', padding: '10px', borderRadius: '5px', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' }}>
                    {isUploading ? 'Uploading & Parsing XML...' : 'Importing Files...'}
                </div>
            )}
            <div
                style={{
                    position: 'fixed',
                    bottom: 0,
                    left: 0,
                    width: '100%',
                    zIndex: 1000,
                    display: 'flex',
                    justifyContent: 'center',
                    backgroundColor: '#fff',
                }}
                >
                <Footer />
            </div>
        </div>
        
    );
};

export default ELNFileImporter;