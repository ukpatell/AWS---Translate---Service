import "./Image.css";
import "../../App.css";
import React, { useState, useEffect } from "react";
import axios from "axios";

export const Image = () => {
  const [image_state, set_image_state] = useState("No File Choosen");
  const [imageToUpload, setimageToUpload] = useState(undefined);

  function uploadImage() {
    if (imageToUpload) {
      const api =
        "https://e3hl1n8ybb.execute-api.us-east-1.amazonaws.com/prod/test";

      set_image_state("Processing...please wait");
      var fileReader = new FileReader();
      var data = ''

      fileReader.onload = function(fileLoadedEvent) {
        data = fileLoadedEvent.target.result;
        console.log(data)
      }
      fileReader.readAsDataURL(imageToUpload);
      console.log(imageToUpload.type)
      // Initiating the PUT request to upload file
      axios({
        method: "POST",
        url: api,
        headers: {'Content-Type': imageToUpload.type },
        data: imageToUpload,
      }).then((res) => {
          alert("File upload successful!");
          setimageToUpload(undefined);
          set_image_state("No File Choosen");
          console.log(res);
        })
        .catch((err) => {
          console.log(err);
          alert("Error while uploading file!");
          setimageToUpload(undefined);
          set_image_state("No File Choosen");
        });
    } else {
      alert("UNKNOWN ERROR: Please upload a file first!");
    }
  }

  const handleDrop = (e) => {
    const imageInput = document.getElementById("uploaded-image");

    imageInput.click();
    imageInput.onchange = () => {
      const selectedImage = imageInput.files[0];
      if (selectedImage.size > 5242880) {
        alert("Image too big!");
        return;
      } else {
        // file_name_element.innerHTML = selectedImage.name;
        set_image_state(selectedImage.name);
        setimageToUpload(selectedImage);
      }
    };
  };

  return (
    <div>
      <h1>Image Translation in Construction</h1>
      <div className="upload-section" onClick={handleDrop}>
        <input
          type="file"
          accept="image/*"
          name="images"
          placeholder="Upload Images"
          id="uploaded-image"
        />
        <div className="upload-section-info" id="upload-section-info">
          <label htmlFor="file">CLICK HERE TO UPLOAD</label>
          <span id="supported-files">JPEG, PNG, PDF, or TIFF</span>
        </div>
      </div>
      <div>
        <h5 id="image-name">{image_state}</h5>
      </div>
      <div>
        <button type="submit" className="btn-submit" onClick={uploadImage}>
          Upload
        </button>
      </div>
    </div>
  );
};
export default Image;
