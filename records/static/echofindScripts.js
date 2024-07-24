function searchFiles() {
    var keyword = document.getElementById("searchInput").value.trim();
    var url = "/search/?keyword=" + keyword;

    const idToken = localStorage.getItem("idToken");

    var requestOptions = {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${idToken}`,
        }
    };

    fetch(url, requestOptions)
        .then(response => response.json())
        .then(data => {
            var resultsList = document.getElementById("searchResults");
            resultsList.innerHTML = "";

            document.getElementById("searchResultsHeader").style.display = "block";
            if (data.results) {
                for (const mp4name in data.results) {
                    const result = data.results[mp4name];
                    var listItem = document.createElement("li");

                    listItem.innerHTML = `
                    <div class="results">
                        <img class="thumbnail" alt="Thumbnail" onclick="playVideo('${result.url}', this)">
                        <span>${mp4name}</span><span class="transcription">${result.text}</span>
                        <button class="small-btn" onclick="toggleTranscription(this)">Show Transcription</button>
                    </div>
                        `;
                    resultsList.appendChild(listItem);
                    document.getElementById("noResultsMessage").style.display = "none";

                     fetchThumbnail(result.thumbnail_url, idToken, listItem.querySelector('.thumbnail'));

                }
            }
            else {
                document.getElementById("noResultsMessage").style.display = "block";
            }
        });
}

function fetchThumbnail(thumbnailUrl, idToken, thumbnailElement) {
    fetch(thumbnailUrl, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${idToken}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.blob();
    })
    .then(blob => {
        var url = URL.createObjectURL(blob);
        thumbnailElement.src = url;
    })
    .catch(error => {
        console.error('Error fetching thumbnail:', error);
    });
}

function playVideo(videoUrl, thumbnail) {
    const idToken = localStorage.getItem("idToken");
    const thumbnailWidth = thumbnail.width;
    const thumbnailHeight = thumbnail.height;

    fetch(videoUrl, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${idToken}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);

        const videoPlayer = document.createElement('video');
        videoPlayer.src = url;
        videoPlayer.controls = true;
        videoPlayer.style.width = thumbnailWidth + 'px';
        videoPlayer.style.height = thumbnailHeight + 'px';

        thumbnail.parentNode.replaceChild(videoPlayer, thumbnail);
        videoPlayer.play();
    })
    .catch(error => {
        console.error('Error fetching video:', error);
    });
}

document.getElementById("searchInput").addEventListener("input", function() {
    clearTimeout(this.searchTimer); //using this.searchTimer so creating a global variable is not necessary
    this.searchTimer = setTimeout(function() {
        searchFiles();
    }, 2000);}
);

document.getElementById("searchForm").addEventListener("submit", function (event){
    event.preventDefault();
    clearTimeout(document.getElementById("searchInput").searchTimer);
});

function toggleTranscription(button) {
    var transcription = button.previousElementSibling;
    if (transcription.style.display === "none" || transcription.style.display === "") {
        transcription.style.display = "block";
        button.textContent = "Hide Transcription";
    } else {
    transcription.style.display = "none";
    button.textContent = "Show Transcription";
    }
}

function logoutUser() {
    const idToken = localStorage.getItem("idToken")

    fetch('/logout/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': `Bearer ${idToken}`,
        }
    }).then(response => {
        if (response.ok) {
            localStorage.removeItem("idToken");
            location.reload();
        }
    }).catch(error => {
        console.error('Error logging out:', error);
    });
}

function dragOverHandler(event) {
    event.preventDefault();
    if(event.dataTransfer.types.includes('Files')){
        document.getElementById('drag-and-drop-area').classList.add('drag-over');
    }
}

function dropHandler(event) {
    event.preventDefault();
    document.getElementById('drag-and-drop-area').classList.remove('drag-over');
    document.getElementById('drag-and-drop-area').style.display = 'none';

    var files = event.dataTransfer.files;
    handleFiles(files);

    document.querySelector('.loader').style.display = 'block';

    sendFIleAndTranscriptionToDatabasesAndCreateThumbnail();
}

function dragLeaveHandler(event) {
    event.preventDefault();
    setTimeout(function (){
        document.getElementById('drag-and-drop-area').classList.remove('drag-over');
    }, 1000);
}

function handleFiles(files) {
    var input = document.getElementById('file');
    input.files = files;
}

function sendFIleAndTranscriptionToDatabasesAndCreateThumbnail() {
    document.querySelector('.loader').style.display = 'block';
    document.getElementById('drag-and-drop-area').style.display = 'none';

    var form = document.getElementById('uploadForm');
    var formData = new FormData(form);
    console.log("form: ", form)
    console.log("formDataL ", formData)

    const idToken = localStorage.getItem("idToken");

    fetch(form.action, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${idToken}`,
            'X-CSRFToken': getCookie("csrftoken")
        },
        body: formData
    })
    .then(response => {
        if (response.ok) {
            console.log('File uploaded successfully');
        } else {
            console.error('File upload failed');
        }
        document.querySelector('.loader').style.display = 'none';
        document.getElementById('drag-and-drop-area').style.display = 'block';
    })
    .catch(error => {
        console.error('Error during file upload:', error);
        document.querySelector('.loader').style.display = 'none';
        document.getElementById('drag-and-drop-area').style.display = 'block';
    });
}

function openFileInput() {
    document.getElementById('file').click()
    document.getElementById('file').addEventListener('change', function() {
    sendFIleAndTranscriptionToDatabasesAndCreateThumbnail();
    });
}

document.getElementById('drag-and-drop-area').addEventListener('dragend', dragLeaveHandler);

function downloadFile(fileName){
    const idToken = localStorage.getItem("idToken")

    var url = `/file/?file_name=${fileName}`

    var requestOptions = {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${idToken}`,
        }
    };

    fetch(url, requestOptions)
        .then(response => {
            if (response.ok) {
                return response.blob();
            } else {
                throw new Error('File download failed');
            }
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            a.click();
            URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}