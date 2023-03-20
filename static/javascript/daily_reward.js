


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
  modalInstance.show();
  // Show the modal

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
    let square = document.getElementById(`task_point-normal-${taskStatus.day}`);
    if (!square) {
      square = document.getElementById(`task_point-pos-${taskStatus.day}`);
      if (!square) {
        square = document.getElementById(`task_point-super-${taskStatus.day}`);
      }
    }

    if (taskStatus.completed) {
      square.innerHTML = "<i class='bi bi-emoji-smile'></i>get!!!";
    } else{

      square.innerHTML =  "<i class='bi bi-emoji-frown-fill'></i> miss";
    }
  });

}



function task_point_pos_click_handler(day) {
    var task_point_pos = document.getElementById("task_point-pos-" + day);
    const xhr = new XMLHttpRequest();

    xhr.open("POST", "/add_login_task_points/", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));

    xhr.onreadystatechange = function() {
      if ( this.status === 200) {
        task_point_pos.innerHTML = "<i class='bi bi-emoji-smile'></i>get!!!";
      }else {
        console.log('Request failed.  Returned status of ' + xhr.status);
      }
    };
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



