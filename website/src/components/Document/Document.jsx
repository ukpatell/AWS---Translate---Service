import { Controls } from '../components';
import React, { useState, useEffect } from 'react';
import axios from 'axios';

import './Document.css'
import '../../App.css'
import secrets from '../../secrets.json'


const Document = (props) => {
    const [file_state, set_file_state] = useState("No File Choosen");
    const [fileToUpload, setFileToUpload] = useState(undefined);
    const [translated_files, setTranslatedFiles] = useState([])
    const [are_files_there, setAreFilesThere] = useState(null)
    const [downloadLink, setDownloadLink] = useState('')

    useEffect(() => {
        axios
            .get(secrets['TranslateServiceStack']['APIURLLISTTRANSLATEDFILES'])
            .then(res => {
                if ((res.data).length != 0) {
                    setTranslatedFiles(res.data)
                    setAreFilesThere(translated_files)
                }
                else {
                    setTranslatedFiles([])
                }
            })
            .catch(err => {
                console.log('ERROR WHILE FETCHING DOCUMENTS' + err)
            })
    }, [])

    const handleDownload = (e) => {
        const fileName = e.target.value;
        const api = secrets['TranslateServiceStack']['APIURLDWNLDTRANSLATEDFILES']+"?fileName="+fileName;

        axios(
            api,
        ).then(response => {            // Getting the url from response
            const url = response.data.fileUploadURL;
            window.open(url)
        });

    }

    function uploadFile() {

        if (fileToUpload && document.getElementById('from-lang-picker').value !== 'auto') {
            // When the upload file button is clicked, 
            // first we need to get the presigned URL        // URL is the one you get from AWS API Gateway
            const src = document.getElementById('from-lang-picker').value;
            const tgt = document.getElementById('to-lang-picker').value;

            const api = secrets['TranslateServiceStack']['APIURLTRANSLATEDOC']
            const doc_api = api + "?fileName=" + fileToUpload.name + "&src=" + src + "&tgt=" + tgt + "&type=" + fileToUpload.type;

            set_file_state('Processing...please wait')

            axios(
                doc_api,
            ).then(response => {            // Getting the url from response
                const url = response.data.fileUploadURL;
                set_file_state('Uploading file...')
                // Initiating the PUT request to upload file    
                axios({
                    method: "PUT",
                    url: url,
                    data: fileToUpload,
                    headers: { "Content-Type": "multipart/form-data", 'x-amz-meta-source': src, 'x-amz-meta-target': tgt, 'x-amz-meta-type': fileToUpload.type }
                }).then(res => {
                    alert('File upload successful!')
                    setFileToUpload(undefined)
                    set_file_state("No File Choosen")
                })
                    .catch(err => {
                        console.log(err)
                        alert('Error while uploading file!')
                        setFileToUpload(undefined)
                        set_file_state("No File Choosen")
                    });
            });
        }
        else {
            if (document.getElementById('from-lang-picker').value === 'auto') {
                alert('Please specify source language!')
            }
            else { alert('Please upload a file first!') }
        }

    }

    const handleDrop = (e) => {
        const fileInput = document.getElementById('uploaded-file');

        fileInput.click();
        fileInput.onchange = () => {
            const selectedFile = fileInput.files[0];
            if (selectedFile.size > 2097152) {
                alert("File too big!")
                return
            }
            else {
                // file_name_element.innerHTML = selectedFile.name;
                set_file_state(selectedFile.name);
                setFileToUpload(selectedFile)
            }
        }
    }

    return (
        <>
            <Controls />
            <div className="Document">
                <div className='upload-section' onClick={handleDrop}>
                    <input type="file" accept=".txt" name="files" placeholder="Upload Files" id="uploaded-file" maxLength={524288000} />
                    {/* <input type="file" accept=".txt, .html, .docx, .pptx, .xlsx, .xlf" name="files" placeholder="Upload Files" id="uploaded-file" maxLength={524288000} /> */}
                    <div className='upload-section-info' id="upload-section-info">
                        <label htmlFor="file">CLICK HERE TO UPLOAD</label>
                        <span id="supported-files">(UTF-8) - TXT [ONLY] [MAX SIZE: 1.5MB]</span>
                        {/* <span id="supported-files">(UTF-8) - TXT, HTML, DOCX, PPTX, XLSX, XLF(XLIFF 1.2+) [ONLY] [MAX SIZE: 5GB]</span> */}
                    </div>
                </div>
                <div>
                    <h5 id="file-name">{file_state}</h5>
                </div>
                <div>
                    <button type="submit" className="btn-submit" onClick={uploadFile}>Upload</button>
                </div>

                <div className='status-section'>
                    <h2 id="list-file">Name</h2>
                    <h2 id='file-lng'>Target Language</h2>
                    <h2>Download</h2>
                </div>
                <div>
                    {!are_files_there ? (
                        <div className='file-section'><h3>Nothing to show</h3></div>
                    ) : (
                        <div className='file-section'>
                            {translated_files.map(file => (
                                <div key={file.Name} className="file-section-files">
                                    <h3 id="list-file">{file.Name}</h3>
                                    <h3 id="file-lng">{file.Code}</h3>
                                    <button id={file.Name} download={file.Name} onClick={handleDownload} value={file.Name}>Download</button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </>
    )

}
export default Document;




