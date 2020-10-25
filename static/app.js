const BASE_URL = "https://acnhapi.com/v1a";

async function getAllFish() {
    const response = await axios.get(`${BASE_URL}/fish`);
    const fishArr = response.data
    populateImages(fishArr)
}

async function getFish(fish_id) {
    const response = await axios.get(`${BASE_URL}/fish/${fish_id}`);
    console.log(response);
    const name = response.data.name
    const catchphrase = response.data['catch-phrase']
    const icon = response.data['icon_uri']
    const imgsrc = response.data['image_uri']
    console.log(name['name-USen'])
    console.log(catchphrase)
    console.log(icon)
    console.log(imgsrc)
}

function populateImages(fish){
    const $grid = $("#uncaught-fish-grid");
    $grid.empty();
    
    for (let f of fish) {
        let $item = $(
        `<div class="card col-2 custom-control custom-checkbox image-checkbox bg-light" style="max-width: 300px" data-id="fish-${f.id}">
                <input type="checkbox" class="custom-control-input" id="fish-${f.id}">
                <label class="custom-control-label" for="fish-${f.id}">
                    <div class="card-header">${f.name['name-USen']}</div>
                    <img src="${f['icon_uri']}" class="card-img-top img-fluid">
                    </label>
        </div>
        `);
    
        $grid.append($item);
    }
}

//save button on click, save the checked fish.id and user.id (saved to localstorage or session?)
//to Caught table using sqlalchemy. Checked fish images should be taken away from UnCaught tab and appear under Caught tab.

//If user is signing in for the first time, get all fish



//Otherwise, if user is logging in, show fish they haven't caught yet