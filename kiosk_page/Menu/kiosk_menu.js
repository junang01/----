let selectedItems = {};

function selectItem(itemId, itemName, itemPrice) {
    if (!selectedItems[itemId]) {
        selectedItems[itemId] = { name: itemName, price: itemPrice, quantity: 0 ,ordernum:0};
    }
    selectedItems[itemId].quantity += 1;
    renderSelectedItems();
}

function updateQuantity(itemId, change) {
    selectedItems[itemId].quantity += change;
    if (selectedItems[itemId].quantity <= 0) {
        delete selectedItems[itemId];
    }
    renderSelectedItems();
}

function renderSelectedItems() {
    const selectedItemsContainer = document.getElementById('selected-items');
    selectedItemsContainer.innerHTML = '';
    for (const [itemId, item] of Object.entries(selectedItems)) {
        selectedItemsContainer.innerHTML += `
            <div class="selected-item">
                <img src="/img/${itemId}.jpg" alt="${item.name}">
                <div class="quantity-control">
                    <button onclick="updateQuantity('${itemId}', -1)">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="updateQuantity('${itemId}', 1)">+</button>
                </div>
                <span>${(item.price * item.quantity).toLocaleString()}원</span>
            </div>
        `;
    }
}

function saveSelection() {
    localStorage.setItem('selectedItems', JSON.stringify(selectedItems));
}