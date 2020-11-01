$("#fish-caught-form").on('submit', function processForm(evt){
    evt.preventDefault();
    let fishDiv = evt.target.parentElement.parentElement;
    fishDiv.classList.toggle('caught');
});