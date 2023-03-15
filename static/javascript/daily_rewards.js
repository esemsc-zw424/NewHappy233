

function showRewardModal() {
    var modal = document.getElementById('reward');
    var modalInstance = new bootstrap.Modal(modal);
    modalInstance.show(); 
}

//function rewardPosClickHandler() {
//const xhr = new XMLHttpRequest();
//xhr.open('GET', 'get_reward_points/');
//xhr.onload = function() {
//    if (xhr.status === 200) {
//    rewardPos.innerHTML = "<i class='bi bi-emoji-smile'></i>get!!!";
//    } else {
//    console.log('Request failed.  Returned status of ' + xhr.status);
//    }
//};
//xhr.send();
//
//}


function rewardPosClickHandler() {
    const rewardPos = document.getElementById("rewardPos");
    const xhr = new XMLHttpRequest();

    xhr.open("POST", "/update_content/", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));

    // Handle the response from the server
    xhr.onreadystatechange = function() {
      if (this.readyState === 4 && this.status === 200) {
        rewardPos.innerHTML = "<i class='bi bi-emoji-smile'></i>get!!!";
      }else {
        console.log('Request failed.  Returned status of ' + xhr.status);
      }
    };
    xhr.send();
  // Send the AJAX request with the content data
 // xhr.send(`contentID=${contentID}&newContent=${encodeURIComponent(newContent)}`);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}