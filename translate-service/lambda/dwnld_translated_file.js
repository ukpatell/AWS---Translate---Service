"use strict";// Need to use AWS 

const AWS = require("aws-sdk");// Creating new S3 instance
const s3 = new AWS.S3({ signatureVersion: "v4" });// Bucket name we are going to connect
const bucketName = process.env.BATCH_BUCKET; // Epiration Time of the presignedUrl


const expirationInSeconds = 120;
exports.handler = async (event, context) => {
    // Reading the file name from the request. (For this you can do according to your requirment)
    console.log(event)
    
    const key = event.queryStringParameters.fileName;

    // Params object for creating the 
    const params = {
        Bucket: bucketName,
        Key: "output/"+key,
        Expires: expirationInSeconds
    };
    try {
        // Creating the presigned Url
        const preSignedURL = await s3.getSignedUrl("getObject", params);
        let returnObject = {
            statusCode: 200,
            headers: {
                "Access-Control-Allow-Origin" : "*", // Required for CORS support to work
                "Content-Type":"text/plain"
        
            },
            body: JSON.stringify({
                fileUploadURL: preSignedURL
            })
        };
        console.log(returnObject)
        return returnObject;
    } catch (e) {
        const response = {
            err: e.message,
            headers: {
                "access-control-allow-origin": "*"
            },
            body: "error occured"
        };
        return response;
    }
};