$(".card").on('click', ".btn", async function processForm(evt){
    evt.preventDefault();
    let userId = $(evt.target.parentElement).data('user-id');
    let dataFishId = $(evt.target.parentElement).data('fish-id');
    let fishId = getSecondPart(dataFishId);

    const resp = await axios.patch(`/api/users/${userId}/fish/${fishId}`);
    if(resp.data.fish.is_caught === true){
        $(evt.target).hide();
        $(evt.target.parentElement).append(`<a href="/fish/${fishId}" class="btn btn-danger fish-uncaught-btn">Uncaught</a>`);
        showCatchphraseAlert(fishId);
    }   else {
        $(evt.target).hide();
        $(evt.target.parentElement).append(`<a href="/fish/${fishId}" class="btn btn-success fish-caught-btn">Caught!</a>`);
        showWarningAlert();
    }
});

// copied this getSecondPart function from artlung in https://stackoverflow.com/questions/573145/get-everything-after-the-dash-in-a-string-in-javascript/35236900
function getSecondPart(str) {
    return str.split('-')[1];
}

async function showCatchphraseAlert(fishId){
    const fishResp = await axios.get(`/api/fish/${fishId}`);
    const catchphrase = fishResp.data.fish.catchphrase;
    $('#message-container').empty();
    $('#message-container').append(`<div class="alert alert-success alert-dismissible fade show" role="alert">${catchphrase}
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
    </button></div>`);
    $('.alert').alert()
}

function showWarningAlert(){
    $('#message-container').empty();
    $('#message-container').append(`<div class="alert alert-warning alert-dismissible fade show" role="alert">
    Oops! You\'ll catch \'em next time!<button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
    </button>
    </div>`);
    $('.alert').alert()
}