function submitFile() {
  var formData = new FormData();
  formData.append("file", document.getElementById("uploaded-file").files[0]);
  formData.append("summary-length", document.getElementById("slider").value);
  let loader =
    ' <img id="loading-image" width="300" height="300" src="../static/images/loading_data.gif" alt="Loading..." />';
  document.getElementById("summary-output").innerHTML = loader;
  $.ajax({
    url: "/upload",
    dataType: "json",
    contentType: false,
    processData: false,
    data: formData,
    type: "post",
    success: function (response) {
      console.log(response.data.summary);
      if (response.status === 200) {
        document.getElementById("summary-output").innerHTML =
          response.data.summary;
      }
    },
    error: function (err) {
      console.log(err);
    },
  });
}

function deleteFile() {
  var inputElement = document.getElementById("uploaded-file");
  inputElement.files.length = 0;
}

var uploadFileForm = document.getElementById("upload-file-form");
var recordOnlineForm = document.getElementById("record-online-form");

var recordOnlineBtn = document.getElementById("record-online");
var uploadFileBtn = document.getElementById("upload-file");

recordOnlineBtn.addEventListener("click", function () {
  uploadFileForm.classList.add("upload-file-form");
  recordOnlineForm.classList.remove("record-online-form");
  document.getElementById("summarizer-col-two").classList.add("hidden");

  // Wait until everything has loaded
  (function () {
    audioElement = document.querySelector(".js-audio");
    startButton = document.querySelector(".js-start");
    stopButton = document.querySelector(".js-stop");

    // We'll get the user's audio input here.
    navigator.mediaDevices
      .getUserMedia({
        audio: true, // We are only interested in the audio
      })
      .then((stream) => {
        // Create a new MediaRecorder instance, and provide the audio-stream.
        recorder = new MediaRecorder(stream);

        // Set the recorder's eventhandlers
        recorder.ondataavailable = saveChunkToRecording;
        recorder.onstop = saveRecording;
      });

    // Add event listeners to the start and stop button
    startButton.addEventListener("mouseup", startRecording);
    stopButton.addEventListener("mouseup", stopRecording);
  })();
});

uploadFileBtn.addEventListener("click", function () {
  uploadFileForm.classList.remove("upload-file-form");
  recordOnlineForm.classList.add("record-online-form");
  document.getElementById("summarizer-col-two").classList.remove("hidden");
});

// record-online-form

// We'll save all chunks of audio in this array.
const chunks = [];

// We will set this to our MediaRecorder instance later.
let recorder = null;

// We'll save some html elements here once the page has loaded.
let audioElement = null;
let startButton = null;
let stopButton = null;

/**
 * Save a new chunk of audio.
 * @param  {MediaRecorderEvent} event
 */
const saveChunkToRecording = (event) => {
  chunks.push(event.data);
};

/**
 * Save the recording as a data-url.
 * @return {[type]}       [description]
 */
const saveRecording = () => {
  const blob = new Blob(chunks, {
    type: "audio/mp4; codecs=opus",
  });
  const url = URL.createObjectURL(blob);

  audioElement.setAttribute("src", url);
};

/**
 * Start recording.
 */
let p = document.createElement("p");
p.innerHTML = "Recording...";
p.setAttribute("id", "recording-text");

const startRecording = () => {
  recorder.start();

  let toolbar = document.getElementById("toolbar");
  recordOnlineForm.insertBefore(p, toolbar);
};

/**
 * Stop recording.
 */
const stopRecording = () => {
  recorder.stop();
  document.getElementById("audio").classList.remove("hidden");
  let recordingText = document.getElementById("recording-text");
  recordingText.innerHTML = "";
};

// upload-file-form

$(document).ready(createDropZone());
function createDropZone() {
  document.querySelectorAll(".drop-zone__input").forEach((inputElement) => {
    const dropZoneElement = inputElement.closest(".drop-zone");

    dropZoneElement.addEventListener("click", (e) => {
      inputElement.click();
    });

    inputElement.addEventListener("change", (e) => {
      if (inputElement.files.length) {
        updateThumbnail(dropZoneElement, inputElement.files[0]);
      }
    });

    dropZoneElement.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZoneElement.classList.add("drop-zone--over");
    });

    ["dragleave", "dragend"].forEach((type) => {
      dropZoneElement.addEventListener(type, (e) => {
        dropZoneElement.classList.remove("drop-zone--over");
      });
    });

    dropZoneElement.addEventListener("drop", (e) => {
      e.preventDefault();

      if (e.dataTransfer.files.length) {
        inputElement.files = e.dataTransfer.files;
        updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
      }

      dropZoneElement.classList.remove("drop-zone--over");
    });
  });
}

/**
 * Updates the thumbnail on a drop zone element.
 *
 * @param {HTMLElement} dropZoneElement
 * @param {File} file
 */
function updateThumbnail(dropZoneElement, file) {
  var deleteBtn = document.getElementById("delete-file");
  deleteBtn.classList.remove("delete-file");

  let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");

  // First time - remove the prompt
  if (dropZoneElement.querySelector(".drop-zone__prompt")) {
    dropZoneElement.querySelector(".drop-zone__prompt").remove();
  }

  let fileContent = document.createElement("p");

  // First time - there is no thumbnail element, so lets create it
  if (!thumbnailElement) {
    thumbnailElement = document.createElement("div");
    thumbnailElement.classList.add("drop-zone__thumb");

    thumbnailElement.appendChild(fileContent);
    dropZoneElement.appendChild(thumbnailElement);
  }

  thumbnailElement.dataset.label = file.name;

  // Show thumbnail for image files
  //   if (file.type.startsWith("image/")) {
  //     const reader = new FileReader();

  //     reader.readAsDataURL(file);
  //     reader.onload = () => {
  //       thumbnailElement.style.backgroundImage = `url('${reader.result}')`;
  //     };
  //   } else {
  //     thumbnailElement.style.backgroundImage = null;
  //   }

  deleteBtn.addEventListener("click", () => {
    location.reload();
  });

  var fileType = file.name.substring(file.name.length - 3);
  console.log(file);
  const filename = thumbnailElement.getAttribute("data-label");
  const h4 = document.createElement("h4");
  h4.classList.add("filename-header");
  h4.innerHTML = filename;
  thumbnailElement.insertBefore(h4, fileContent);
  if (fileType === "txt") {
    const reader = new FileReader();

    reader.readAsText(file);

    reader.onload = () => {
      fileContent.textContent = reader.result;
    };
  } else if (
    fileType === "pdf" ||
    fileType === "mp3" ||
    fileType === "m4a" ||
    fileType === "wav"
  ) {
    thumbnailElement.style.backgroundColor = "#ffd60a";
  } else {
    fileContent.textContent = "File Type Not Supported";
  }
}

// copy to clipboard
function copyToClipboard(id) {
  var r = document.createRange();
  r.selectNode(document.getElementById(id));
  window.getSelection().removeAllRanges();
  window.getSelection().addRange(r);
  document.execCommand("copy");
  window.getSelection().removeAllRanges();
  alert("Summary copied to clipboard!");
}
