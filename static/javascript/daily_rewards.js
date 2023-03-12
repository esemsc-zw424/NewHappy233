

$(document).ready (function() {

    var modal = document.getElementById('reward');
    var modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    });


    const rewardPos = document.getElementById("rewardPos");


function rewardPosClickHandler() {
const xhr = new XMLHttpRequest();
xhr.open('GET', 'get_reward_points/');
xhr.onload = function() {
    if (xhr.status === 200) {
    rewardPos.innerHTML = "<i class='bi bi-emoji-smile'></i>get!!!";
    } else {
    console.log('Request failed.  Returned status of ' + xhr.status);
    }
};
xhr.send();

}