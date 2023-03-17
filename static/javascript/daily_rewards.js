

//function show_login_task_modal()() {
//    var modal = document.getElementById('daily_login_task');
//    var modalInstance = new bootstrap.Modal(modal);
//    modalInstance.show();
//}


function show_login_task_modal() {
  var modal = document.getElementById("daily_login_task");
  var modalInstance = new bootstrap.Modal(modal);

  // Add the event listener for when the modal is about to be shown
  modal.addEventListener("show.bs.modal", function (event) {
    // Get the pos value from the data attribute
    var myDiv = document.getElementById("pos_val");
    var pos = parseInt(myDiv.getAttribute("data-my-variable"));

    // Fetch and update the task point statuses
    get_login_task_status(pos);
  });

  // Show the modal
  modalInstance.show();
}


function get_login_task_status(pos) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/get_login_task_status/?pos=" + pos, true);
  xhr.responseType = "json";

  xhr.onload = function () {
    if (xhr.status === 200) {
      update_modal(xhr.response);
    } else {
      console.error("An error occurred while fetching the task point status");
    }
  };

  xhr.send();
}

function update_modal(data) {
  data.task_statuses.forEach((taskStatus) => {
    const square = document.getElementById(`task_point-normal-${taskStatus.day}`);

    if (taskStatus.received) {
      square.innerHTML = `day${taskStatus.day} <br> <i class='bi bi-emoji-smile'></i>get!!!`;
    } else {
      square.style.backgroundColor = "grey";
    }
  });
}













function task_point_pos_click_handler(day) {
    var task_point_pos = document.getElementById('task_point-pos');
//    var td_id = td_element.getAttribute('id');
    const xhr = new XMLHttpRequest();

    xhr.open("POST", "/add_login_task_points/", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));

    // Handle the response from the server
    xhr.onreadystatechange = function() {
      if (this.readyState === 4 && this.status === 200) {
      console.log(day)
        task_point_pos.innerHTML = "<i class='bi bi-emoji-smile'></i>get!!!";
      }else {
        console.log('Request failed.  Returned status of ' + xhr.status);
      }
    };
  // Send the AJAX request with the content data
    xhr.send();
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
