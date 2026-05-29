/* =========================================================
   VetCash Pro - Main JavaScript
   Sidebar + POS + Cart + Barcode Scanner
   ========================================================= */

const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const toggleBtn = document.getElementById('toggleSidebar');
const overlay = document.getElementById('overlay');

function isMobile() {
  return window.innerWidth <= 991;
}

function toggleSidebar() {
  if (isMobile()) {
    sidebar?.classList.toggle('mobile-open');
    overlay?.classList.toggle('show');
  } else {
    sidebar?.classList.toggle('collapsed');
    mainContent?.classList.toggle('full');
  }
}

toggleBtn?.addEventListener('click', toggleSidebar);

overlay?.addEventListener('click', () => {
  sidebar?.classList.remove('mobile-open');
  overlay?.classList.remove('show');
});

window.addEventListener('resize', () => {
  if (!isMobile()) {
    sidebar?.classList.remove('mobile-open');
    overlay?.classList.remove('show');
  } else {
    sidebar?.classList.remove('collapsed');
    mainContent?.classList.remove('full');
  }
});

/* =========================
   Helpers
   ========================= */

function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(';') : [];

  for (const cookie of cookies) {
    const trimmed = cookie.trim();

    if (trimmed.startsWith(name + '=')) {
      return decodeURIComponent(trimmed.substring(name.length + 1));
    }
  }

  return null;
}

function money(value) {
  return `${Number(value || 0).toFixed(2)} JD`;
}

/* =========================
   POS State
   ========================= */

let products = [];
let cart = [];
let searchTimer = null;

/* =========================
   Products
   ========================= */

async function loadProducts() {
  const productGrid = document.getElementById('productGrid');

  if (!productGrid || !window.VETCASH_URLS) return;

  const search = document.getElementById('productSearch')?.value || '';
  const category = document.getElementById('categoryFilter')?.value || '';

  const url = new URL(window.VETCASH_URLS.productsApi, window.location.origin);
  url.searchParams.set('q', search);
  url.searchParams.set('category', category);

  productGrid.innerHTML = `
    <div class="empty-state">
      <i class="bi bi-hourglass-split"></i>
      <p>جاري تحميل المنتجات...</p>
    </div>
  `;

  try {
    const response = await fetch(url);
    const data = await response.json();

    products = data.products || [];
    renderProducts();

    return products;
  } catch (error) {
    productGrid.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-wifi-off"></i>
        <p>تعذر تحميل المنتجات</p>
      </div>
    `;

    return [];
  }
}

function renderProducts() {
  const box = document.getElementById('productGrid');
  if (!box) return;

  if (products.length === 0) {
    box.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-box"></i>
        <p>لا توجد منتجات متاحة</p>
      </div>
    `;
    return;
  }

  box.innerHTML = products.map(product => `
    <div class="col-md-6 col-xl-4">
      <div class="product-card" onclick="addToCart(${product.id})">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <span class="badge-soft soft-blue">${product.category}</span>
          <small class="text-muted">المخزون: ${product.stock}</small>
        </div>

        <h5>${product.name}</h5>

        <div class="price">${money(product.price)}</div>
      </div>
    </div>
  `).join('');
}

/* =========================
   Cart
   ========================= */

function addToCart(id) {
  const product = products.find(item => item.id === id);
  if (!product) return;

  const cartItem = cart.find(item => item.id === id);

  if (cartItem) {
    if (cartItem.qty < product.stock) {
      cartItem.qty += 1;
    } else {
      alert('لا يمكن إضافة كمية أكبر من المخزون المتاح');
    }
  } else {
    cart.push({ ...product, qty: 1 });
  }

  renderCart();
}

function changeQty(id, value) {
  const item = cart.find(item => item.id === id);
  if (!item) return;

  const product = products.find(product => product.id === id);
  const newQty = item.qty + value;

  if (newQty <= 0) {
    cart = cart.filter(item => item.id !== id);
  } else if (product && newQty <= product.stock) {
    item.qty = newQty;
  } else {
    alert('لا يمكن إضافة كمية أكبر من المخزون المتاح');
  }

  renderCart();
}

function getSubtotal() {
  return cart.reduce((sum, item) => sum + item.price * item.qty, 0);
}

function getDiscount() {
  return Number(document.getElementById('discountInput')?.value || 0);
}

function renderCart() {
  const box = document.getElementById('cartItems');
  const subtotalEl = document.getElementById('cartSubtotal');
  const totalEl = document.getElementById('cartTotal');

  if (!box || !subtotalEl || !totalEl) return;

  if (cart.length === 0) {
    box.innerHTML = `
      <div class="empty-state">
        <i class="bi bi-cart"></i>
        <p>لم يتم اختيار أي منتج</p>
      </div>
    `;

    subtotalEl.textContent = money(0);
    totalEl.textContent = money(0);
    return;
  }

  box.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div>
        <strong>${item.name}</strong><br>
        <small>${money(item.price)} × ${item.qty}</small>
      </div>

      <div class="text-end">
        <strong>${money(item.price * item.qty)}</strong><br>

        <button class="btn btn-sm btn-outline-primary py-0 px-2"
                onclick="changeQty(${item.id}, -1)">
          -
        </button>

        <button class="btn btn-sm btn-outline-primary py-0 px-2"
                onclick="changeQty(${item.id}, 1)">
          +
        </button>
      </div>
    </div>
  `).join('');

  const subtotal = getSubtotal();
  const total = Math.max(0, subtotal - getDiscount());

  subtotalEl.textContent = money(subtotal);
  totalEl.textContent = money(total);
}

/* =========================
   Barcode Scanner
   ========================= */

async function handleBarcodeEnter(event) {
  if (event.key !== 'Enter') return;

  event.preventDefault();

  const input = document.getElementById('productSearch');
  const barcode = input?.value.trim();

  if (!barcode) return;

  const foundProducts = await loadProducts();

  if (foundProducts.length === 1) {
    addToCart(foundProducts[0].id);

    input.value = '';
    products = [];

    await loadProducts();
    return;
  }

  if (foundProducts.length > 1) {
    alert('تم العثور على أكثر من منتج، اختر المنتج يدويًا');
    return;
  }

  alert('لم يتم العثور على منتج بهذا الباركود');
}

/* =========================
   Complete Sale
   ========================= */

async function completeSale() {
  if (cart.length === 0) {
    alert('الرجاء إضافة منتجات إلى السلة أولًا');
    return;
  }

  try {
    const response = await fetch(window.VETCASH_URLS.completeSaleApi, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        discount: getDiscount(),
        items: cart.map(item => ({
          id: item.id,
          qty: item.qty
        }))
      })
    });

    const data = await response.json();

    if (!response.ok || !data.ok) {
      alert(data.message || 'حدث خطأ أثناء البيع');
      return;
    }

    alert(`تم إتمام البيع بنجاح - رقم الفاتورة: #${data.sale_id}`);

    cart = [];

    const discountInput = document.getElementById('discountInput');
    if (discountInput) discountInput.value = 0;

    await loadProducts();
    renderCart();

  } catch (error) {
    alert('تعذر الاتصال بالخادم');
  }
}

/* =========================
   Page Events
   ========================= */

const productSearchInput = document.getElementById('productSearch');
const categoryFilter = document.getElementById('categoryFilter');
const discountInput = document.getElementById('discountInput');

productSearchInput?.addEventListener('input', () => {
  clearTimeout(searchTimer);

  searchTimer = setTimeout(() => {
    loadProducts();
  }, 300);
});

productSearchInput?.addEventListener('keydown', handleBarcodeEnter);

categoryFilter?.addEventListener('change', loadProducts);

discountInput?.addEventListener('input', renderCart);

loadProducts();
renderCart();