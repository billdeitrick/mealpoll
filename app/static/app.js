// Submit item deletes with JS from button click. 
// #region
document.querySelectorAll(".item-list").forEach((element) => {
        element.addEventListener('click', (event) => {
            if (event.target.hasAttribute('data-delete')) {

                let target = (event.target.tagName === 'BUTTON') ? event.target : event.target.parentElement;

                if (event.target.dataset.delete == 'item') {
                
                    let form = document.getElementById('item-delete-form');
                    let type_field = form.querySelector('[name="item_type"]');
                    let id_field = form.querySelector('[name="item_id"]');

                    type_field.setAttribute('value', target.dataset.deletetype);
                    id_field.setAttribute('value', target.dataset.id);

                    form.submit();
                    
                } else if (event.target.dataset.delete == 'meal') {

                    let form = document.getElementById('meal-delete-form');
                    let type_field = form.querySelector('[name="meal_id"]');

                    type_field.setAttribute('value', target.dataset.id);

                    form.submit();

                }
            }
        });
    }
)
// #endregion

// Respond form dynamic behavior
// #region

// Dynamic side choices
document.querySelectorAll("#respond-form #food").forEach((element) => {
    element.addEventListener('change', (event) => {
        if (parseInt(element.value)) {
            let sideField = document.getElementById('side');

            fetch(`/sides/${element.value}`)
                .then((response) => {
                    return response.json()
                })
                .then((response) => {

                    while(sideField.firstChild) {
                        sideField.firstChild.remove();
                    }

                    response.sides.forEach((side) => {
                        let option = document.createElement("option");
                        option.value = side.id;
                        option.text = side.label;
                        sideField.appendChild(option);
                    });
                });

                document.getElementById('food_other')
                    .setAttribute('disabled', '');

        } else {
            document.getElementById('food_other')
                .removeAttribute('disabled');
        }
    });
});

// Enable/disable "other side" option
document.querySelectorAll("#respond-form #side, #respond-form #drink").forEach((element) => {
    element.addEventListener('change', (event) => {
        if (parseInt(element.value)) {
            document.getElementById(`${element.id}_other`)
                .setAttribute('disabled', '');
        } else {
            document.getElementById(`${element.id}_other`)
                .removeAttribute('disabled');
        }
    });
});

// Enable/Disable "other drink" option

// #endregion