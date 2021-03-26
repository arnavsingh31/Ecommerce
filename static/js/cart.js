var addToCartBtns = document.getElementsByClassName('update-cart');

for(let i =0;i<addToCartBtns.length;i++){
    addToCartBtns[i].addEventListener('click', addToCart)
}

function addToCart(){
    var productId = this.dataset.product;
    var action = this.dataset.action
    console.log(`productId: ${productId} action: ${action}`)

    console.log('USER:', user )
    if(user === "AnonymousUser"){
        addCookieItem(productId, action);
    }else{
        updateUserOrder(productId, action);
    }
}

function updateUserOrder(productId, action){
    var url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'productId':productId, 'action':action})
    }).then((res)=>{
        return res.json()
    }).then((data)=>{
        
        location.reload()
    })
}

function addCookieItem(productId, action){
    console.log('Not logged in');
    if(action == 'add'){
        if (cart[productId] == undefined){
            cart[productId] = {"quantity":1};
        }else{
            cart[productId]['quantity'] += 1;
        }
    }

    if(action == 'remove'){
        cart[productId]['quantity'] -= 1;

        if(cart[productId]['quantity'] <= 0){
            delete cart[productId];
        }
    }

    document.cookie = 'cart='+ JSON.stringify(cart) + ';domain=;path=/';

}