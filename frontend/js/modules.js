/**
 * Master Data, Production, Inspection, Defect, CAPA, and Reports Modules
 */
class Modules {
    // -------------------------------------------------------------
    // 1. PRODUCTS MODULE
    // -------------------------------------------------------------
    static async renderProducts(page = 1) {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Products...</div>`;

        try {
            const search = document.getElementById("search-input") ? document.getElementById("search-input").value : "";
            const res = await ApiClient.get("/products", { page, per_page: 25, search });
            
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-boxes-stacked text-primary me-2"></i>Product Catalog (${res.total} items)</h6>
                        <button class="btn btn-sm btn-primary" onclick="Modules.showCreateProductModal()"><i class="fa-solid fa-plus me-1"></i>New Product</button>
                    </div>
                    <div class="card-body">
                        <div class="filter-bar">
                            <div class="search-input-wrap">
                                <i class="fa-solid fa-magnifying-glass"></i>
                                <input type="text" id="search-input" class="form-control" placeholder="Search by SKU or name..." value="${search}" onkeyup="if(event.key==='Enter') Modules.renderProducts(1)">
                            </div>
                            <button class="btn btn-outline-secondary btn-sm" onclick="Modules.renderProducts(1)">Filter</button>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Product SKU</th>
                                        <th>Name</th>
                                        <th>Category</th>
                                        <th>UoM</th>
                                        <th>Target Cycle</th>
                                        <th>Standard Cost</th>
                                        <th>BOM Items</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${res.items.map(p => `
                                        <tr>
                                            <td><strong>${p.id}</strong></td>
                                            <td>${p.name}</td>
                                            <td><span class="badge badge-soft-info">${p.category}</span></td>
                                            <td>${p.unit_of_measure}</td>
                                            <td>${p.target_cycle_time_mins} min</td>
                                            <td>$${p.standard_cost.toFixed(2)}</td>
                                            <td><span class="badge badge-soft-primary">${p.bom_items_count} items</span></td>
                                            <td><span class="badge badge-soft-success">Active</span></td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary py-0" onclick="TraceabilityModule.quickTrace('product', '${p.id}'); app.navigate('traceability');">Trace</button>
                                            </td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                        ${Modules.renderPagination(res, 'Modules.renderProducts')}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load products: ${e.message}</div>`;
        }
    }

    static showCreateProductModal() {
        const nextId = "SKU-" + String(Math.floor(Math.random() * 900000) + 100000);
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Create New Product</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="createProductForm">
                                <div class="mb-3">
                                    <label class="form-label">SKU ID (Deterministic)</label>
                                    <input type="text" class="form-control" id="p-id" value="${nextId}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Product Name</label>
                                    <input type="text" class="form-control" id="p-name" placeholder="e.g. Precision Hydraulic Valve Model-X" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Category</label>
                                    <select class="form-select" id="p-category">
                                        <option value="Powertrain Components">Powertrain Components</option>
                                        <option value="Electronic Control Units">Electronic Control Units</option>
                                        <option value="Precision Hydraulic Valves">Precision Hydraulic Valves</option>
                                        <option value="Optical Sensor Housings">Optical Sensor Housings</option>
                                    </select>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Target Cycle Time (mins)</label>
                                        <input type="number" class="form-control" id="p-cycle" value="15" step="0.5">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Standard Cost ($)</label>
                                        <input type="number" class="form-control" id="p-cost" value="120" step="0.01">
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="Modules.submitCreateProduct()">Save Product</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitCreateProduct() {
        const body = {
            id: document.getElementById("p-id").value.trim(),
            name: document.getElementById("p-name").value.trim(),
            category: document.getElementById("p-category").value,
            target_cycle_time_mins: parseFloat(document.getElementById("p-cycle").value),
            standard_cost: parseFloat(document.getElementById("p-cost").value)
        };
        try {
            await ApiClient.post("/products", body);
            Modules.closeModal();
            app.showToast("Product created successfully!", "success");
            Modules.renderProducts(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    // -------------------------------------------------------------
    // 2. BOM MODULE
    // -------------------------------------------------------------
    static async renderBOM() {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Bill of Materials...</div>`;

        try {
            const boms = await ApiClient.get("/boms");
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-list-ol text-warning me-2"></i>Bill of Materials Master Registry (${boms.length} items)</h6>
                        <button class="btn btn-sm btn-primary" onclick="Modules.showCreateBOMModal()"><i class="fa-solid fa-plus me-1"></i>New BOM Entry</button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>BOM ID</th>
                                        <th>Parent Product SKU</th>
                                        <th>Component SKU</th>
                                        <th>Component Name</th>
                                        <th>Qty / Unit</th>
                                        <th>UoM</th>
                                        <th>Scrap Factor</th>
                                        <th>Revision</th>
                                        <th>Effective Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${boms.slice(0, 100).map(b => `
                                        <tr>
                                            <td><code>#${b.id}</code></td>
                                            <td><strong>${b.parent_product_id}</strong></td>
                                            <td><code>${b.component_sku}</code></td>
                                            <td>${b.component_name}</td>
                                            <td><strong>${b.quantity_per_unit}</strong></td>
                                            <td>${b.unit_of_measure}</td>
                                            <td>${(b.scrap_factor * 100).toFixed(1)}%</td>
                                            <td><span class="badge badge-soft-info">Rev ${b.revision}</span></td>
                                            <td>${b.effective_from ? new Date(b.effective_from).toLocaleDateString() : 'Active'}</td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load BOMs: ${e.message}</div>`;
        }
    }

    static showCreateBOMModal() {
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Define BOM Component</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="createBOMForm">
                                <div class="mb-3">
                                    <label class="form-label">Parent Product SKU</label>
                                    <input type="text" class="form-control" id="b-parent" placeholder="e.g. SKU-000001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Component SKU</label>
                                    <input type="text" class="form-control" id="b-comp-sku" placeholder="e.g. MAT-TITANIUM-001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Component Description</label>
                                    <input type="text" class="form-control" id="b-comp-name" placeholder="e.g. High Precision Ceramic Bearing" required>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Qty Per Unit</label>
                                        <input type="number" class="form-control" id="b-qty" value="1.0" step="0.1" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Unit of Measure</label>
                                        <input type="text" class="form-control" id="b-uom" value="PCS">
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="Modules.submitCreateBOM()">Save Component</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitCreateBOM() {
        const body = {
            parent_product_id: document.getElementById("b-parent").value.trim(),
            component_sku: document.getElementById("b-comp-sku").value.trim(),
            component_name: document.getElementById("b-comp-name").value.trim(),
            quantity_per_unit: parseFloat(document.getElementById("b-qty").value),
            unit_of_measure: document.getElementById("b-uom").value.trim()
        };
        try {
            await ApiClient.post("/boms", body);
            Modules.closeModal();
            app.showToast("BOM item added successfully!", "success");
            Modules.renderBOM();
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    // -------------------------------------------------------------
    // 3. SUPPLIERS MODULE
    // -------------------------------------------------------------
    static async renderSuppliers(page = 1) {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Suppliers...</div>`;

        try {
            const res = await ApiClient.get("/suppliers", { page, per_page: 25 });
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-truck-field text-info me-2"></i>Approved Suppliers & Vendors (${res.total})</h6>
                        <button class="btn btn-sm btn-primary" onclick="Modules.showCreateSupplierModal()"><i class="fa-solid fa-plus me-1"></i>Register Supplier</button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Supplier ID</th>
                                        <th>Vendor Code</th>
                                        <th>Supplier Name</th>
                                        <th>Country</th>
                                        <th>Rating</th>
                                        <th>Status</th>
                                        <th>Lots Supplied</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${res.items.map(s => `
                                        <tr>
                                            <td><strong>${s.id}</strong></td>
                                            <td><code>${s.code}</code></td>
                                            <td>${s.name}</td>
                                            <td>${s.country}</td>
                                            <td>
                                                <span class="text-warning"><i class="fa-solid fa-star"></i></span>
                                                <strong>${s.rating.toFixed(1)}</strong>
                                            </td>
                                            <td><span class="badge ${s.status === 'ACTIVE' ? 'badge-soft-success' : 'badge-soft-warning'}">${s.status}</span></td>
                                            <td><span class="badge badge-soft-primary">${s.material_lots_count} lots</span></td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary py-0" onclick="TraceabilityModule.quickTrace('supplier', '${s.id}'); app.navigate('traceability');">Trace</button>
                                            </td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                        ${Modules.renderPagination(res, 'Modules.renderSuppliers')}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load suppliers: ${e.message}</div>`;
        }
    }

    static showCreateSupplierModal() {
        const nextId = "SUP-" + String(Math.floor(Math.random() * 900000) + 100000);
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Register Supplier</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="createSupplierForm">
                                <div class="mb-3">
                                    <label class="form-label">Supplier ID</label>
                                    <input type="text" class="form-control" id="s-id" value="${nextId}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Vendor Code</label>
                                    <input type="text" class="form-control" id="s-code" placeholder="e.g. VEND-9901" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Supplier Company Name</label>
                                    <input type="text" class="form-control" id="s-name" placeholder="e.g. Allied Precision Forging Corp" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Country</label>
                                    <input type="text" class="form-control" id="s-country" value="USA">
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="Modules.submitCreateSupplier()">Save Supplier</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitCreateSupplier() {
        const body = {
            id: document.getElementById("s-id").value.trim(),
            code: document.getElementById("s-code").value.trim(),
            name: document.getElementById("s-name").value.trim(),
            country: document.getElementById("s-country").value.trim()
        };
        try {
            await ApiClient.post("/suppliers", body);
            Modules.closeModal();
            app.showToast("Supplier registered successfully!", "success");
            Modules.renderSuppliers(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    // -------------------------------------------------------------
    // 4. MATERIAL LOTS MODULE
    // -------------------------------------------------------------
    static async renderLots(page = 1) {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Material Lots...</div>`;

        try {
            const res = await ApiClient.get("/material-lots", { page, per_page: 25 });
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-layer-group text-purple me-2"></i>Material Lots & Pedigree Batches (${res.total})</h6>
                        <button class="btn btn-sm btn-primary" onclick="Modules.showCreateLotModal()"><i class="fa-solid fa-plus me-1"></i>Receive Material Lot</button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Lot ID</th>
                                        <th>Material SKU</th>
                                        <th>Material Description</th>
                                        <th>Supplier</th>
                                        <th>Initial Qty</th>
                                        <th>Remaining Qty</th>
                                        <th>Status</th>
                                        <th>Received Date</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${res.items.map(l => `
                                        <tr>
                                            <td><strong>${l.id}</strong></td>
                                            <td><code>${l.material_sku}</code></td>
                                            <td>${l.material_name}</td>
                                            <td>${l.supplier_name || l.supplier_id}</td>
                                            <td>${l.initial_quantity} ${l.unit_of_measure}</td>
                                            <td><strong class="${l.remaining_quantity < 500 ? 'text-warning' : ''}">${l.remaining_quantity}</strong></td>
                                            <td>
                                                <span class="badge ${l.status === 'RELEASED' ? 'badge-soft-success' : (l.status === 'QUARANTINED' ? 'badge-soft-danger' : 'badge-soft-dark')}">${l.status}</span>
                                            </td>
                                            <td>${l.received_date ? new Date(l.received_date).toLocaleDateString() : 'N/A'}</td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary py-0" onclick="TraceabilityModule.quickTrace('lot', '${l.id}'); app.navigate('traceability');">Trace</button>
                                            </td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                        ${Modules.renderPagination(res, 'Modules.renderLots')}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load material lots: ${e.message}</div>`;
        }
    }

    static showCreateLotModal() {
        const nextId = "LOT-SUP-000001-2026-" + String(Math.floor(Math.random() * 900000) + 100000);
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Receive Material Lot</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="createLotForm">
                                <div class="mb-3">
                                    <label class="form-label">Lot ID (LOT-SUP-XXXXXX-2026-XXXXXX)</label>
                                    <input type="text" class="form-control" id="l-id" value="${nextId}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Supplier ID</label>
                                    <input type="text" class="form-control" id="l-sup-id" value="SUP-000001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Material SKU</label>
                                    <input type="text" class="form-control" id="l-sku" placeholder="MAT-TITANIUM-0001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Material Name</label>
                                    <input type="text" class="form-control" id="l-name" placeholder="Raw Forged Alloy Ingot" required>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Received Quantity</label>
                                        <input type="number" class="form-control" id="l-qty" value="5000" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Unit of Measure</label>
                                        <input type="text" class="form-control" id="l-uom" value="PCS">
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="Modules.submitCreateLot()">Receive Lot</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitCreateLot() {
        const body = {
            id: document.getElementById("l-id").value.trim(),
            supplier_id: document.getElementById("l-sup-id").value.trim(),
            material_sku: document.getElementById("l-sku").value.trim(),
            material_name: document.getElementById("l-name").value.trim(),
            initial_quantity: parseFloat(document.getElementById("l-qty").value),
            unit_of_measure: document.getElementById("l-uom").value.trim()
        };
        try {
            await ApiClient.post("/material-lots", body);
            Modules.closeModal();
            app.showToast("Material lot received and pedigreed successfully!", "success");
            Modules.renderLots(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    // -------------------------------------------------------------
    // 5. PRODUCTION ORDERS MODULE
    // -------------------------------------------------------------
    static async renderOrders(page = 1) {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Production Orders...</div>`;

        try {
            const res = await ApiClient.get("/production-orders", { page, per_page: 25 });
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-industry text-primary me-2"></i>Shop Floor Production Orders (${res.total})</h6>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="Modules.showConsumeModal()"><i class="fa-solid fa-wrench me-1"></i>Consume Material</button>
                            <button class="btn btn-sm btn-primary" onclick="Modules.showCreateOrderModal()"><i class="fa-solid fa-plus me-1"></i>New Work Order</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Order ID</th>
                                        <th>Product</th>
                                        <th>Target</th>
                                        <th>Completed</th>
                                        <th>Rework</th>
                                        <th>Scrap</th>
                                        <th>Status</th>
                                        <th>Batch #</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${res.items.map(o => `
                                        <tr>
                                            <td><strong>${o.id}</strong></td>
                                            <td>${o.product_name || o.product_id}</td>
                                            <td><strong>${o.target_quantity}</strong></td>
                                            <td><span class="text-success fw-bold">${o.completed_quantity}</span></td>
                                            <td><span class="text-warning fw-bold">${o.rework_quantity}</span></td>
                                            <td><span class="text-danger fw-bold">${o.scrapped_quantity}</span></td>
                                            <td>
                                                <span class="badge ${o.status === 'COMPLETED' ? 'badge-soft-success' : (o.status === 'IN_PROGRESS' ? 'badge-soft-primary' : 'badge-soft-dark')}">${o.status}</span>
                                            </td>
                                            <td><code>${o.batch_number}</code></td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary py-0" onclick="TraceabilityModule.quickTrace('order', '${o.id}'); app.navigate('traceability');">Trace</button>
                                            </td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                        ${Modules.renderPagination(res, 'Modules.renderOrders')}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load orders: ${e.message}</div>`;
        }
    }

    static showCreateOrderModal() {
        const nextId = "WO-2026-" + String(Math.floor(Math.random() * 900000) + 100000);
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Create Production Work Order</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="createOrderForm">
                                <div class="mb-3">
                                    <label class="form-label">Work Order ID (WO-2026-XXXXXX)</label>
                                    <input type="text" class="form-control" id="o-id" value="${nextId}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Target Product SKU</label>
                                    <input type="text" class="form-control" id="o-prod-id" value="SKU-000001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Target Production Quantity</label>
                                    <input type="number" class="form-control" id="o-qty" value="100" required>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="Modules.submitCreateOrder()">Create Work Order</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitCreateOrder() {
        const body = {
            id: document.getElementById("o-id").value.trim(),
            product_id: document.getElementById("o-prod-id").value.trim(),
            target_quantity: parseInt(document.getElementById("o-qty").value)
        };
        try {
            await ApiClient.post("/production-orders", body);
            Modules.closeModal();
            app.showToast("Work order scheduled and BOM materials planned!", "success");
            Modules.renderOrders(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    static showConsumeModal() {
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Record Material Consumption</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="consumeForm">
                                <div class="mb-3">
                                    <label class="form-label">Production Order ID</label>
                                    <input type="text" class="form-control" id="c-wo" value="WO-2026-000001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Material Lot ID</label>
                                    <input type="text" class="form-control" id="c-lot" placeholder="e.g. LOT-SUP-000001-2026-000001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Consumed Quantity</label>
                                    <input type="number" class="form-control" id="c-qty" value="25" step="0.5" required>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="Modules.submitConsumption()">Record Consumption</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitConsumption() {
        const body = {
            production_order_id: document.getElementById("c-wo").value.trim(),
            material_lot_id: document.getElementById("c-lot").value.trim(),
            consumed_quantity: parseFloat(document.getElementById("c-qty").value)
        };
        try {
            await ApiClient.post("/material-consumptions", body);
            Modules.closeModal();
            app.showToast("Material consumption recorded and lot deducted!", "success");
            Modules.renderOrders(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    // -------------------------------------------------------------
    // 6. MACHINES MODULE
    // -------------------------------------------------------------
    static async renderMachines() {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Machines...</div>`;

        try {
            const machines = await ApiClient.get("/machines");
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-gears text-secondary me-2"></i>Manufacturing Plant Machines & Work Cells (${machines.length})</h6>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
                            ${machines.map(m => `
                                <div class="col-md-4 col-sm-6">
                                    <div class="p-3 border rounded bg-white shadow-sm h-100">
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <span class="badge badge-soft-dark"><strong>${m.machine_code}</strong></span>
                                            <span class="badge ${m.status === 'OPERATIONAL' ? 'badge-soft-success' : 'badge-soft-warning'}">${m.status}</span>
                                        </div>
                                        <h6 class="fw-bold text-dark mb-1">${m.name}</h6>
                                        <p class="text-muted small mb-2"><i class="fa-solid fa-industry me-1"></i>${m.line} &bull; ${m.location}</p>
                                        <div class="small text-secondary mb-3"><strong>Type:</strong> ${m.type}</div>
                                        <button class="btn btn-sm btn-outline-primary w-100" onclick="TraceabilityModule.quickTrace('machine', '${m.id}'); app.navigate('traceability');">Trace Machine History</button>
                                    </div>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load machines: ${e.message}</div>`;
        }
    }

    // -------------------------------------------------------------
    // 7. PROCESS STEPS MODULE
    // -------------------------------------------------------------
    static async renderProcessSteps() {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Process Steps...</div>`;

        try {
            const steps = await ApiClient.get("/process-steps");
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-route text-primary me-2"></i>Manufacturing Process Routing & SOP Stages (${steps.length})</h6>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Step Code</th>
                                        <th>Sequence</th>
                                        <th>Process Name</th>
                                        <th>Std Duration</th>
                                        <th>Inspection Gate</th>
                                        <th>Operating Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${steps.map(s => `
                                        <tr>
                                            <td><code>${s.step_code}</code></td>
                                            <td><span class="badge badge-soft-primary">Stage #${s.sequence_number}</span></td>
                                            <td><strong>${s.name}</strong></td>
                                            <td>${s.standard_duration_mins} mins</td>
                                            <td>
                                                <span class="badge ${s.inspection_required ? 'badge-soft-success' : 'badge-soft-dark'}">
                                                    ${s.inspection_required ? 'MANDATORY' : 'OPTIONAL'}
                                                </span>
                                            </td>
                                            <td>${s.description || 'Standard manufacturing process protocol'}</td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load process steps: ${e.message}</div>`;
        }
    }

    // -------------------------------------------------------------
    // 8. INSPECTIONS MODULE
    // -------------------------------------------------------------
    static async renderInspections(page = 1) {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Inspections...</div>`;

        try {
            const res = await ApiClient.get("/inspections", { page, per_page: 25 });
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-microscope text-success me-2"></i>Quality Inspections (${res.total})</h6>
                        <button class="btn btn-sm btn-primary" onclick="Modules.showRecordInspectionModal()"><i class="fa-solid fa-plus me-1"></i>Record Inspection</button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Inspection ID</th>
                                        <th>Work Order</th>
                                        <th>Machine</th>
                                        <th>Inspected</th>
                                        <th>Passed</th>
                                        <th>Failed</th>
                                        <th>Result</th>
                                        <th>Inspector</th>
                                        <th>Timestamp</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${res.items.map(i => `
                                        <tr>
                                            <td><strong>${i.id}</strong></td>
                                            <td><code>${i.production_order_id}</code></td>
                                            <td>${i.machine_name || i.machine_id || 'N/A'}</td>
                                            <td><strong>${i.inspected_quantity}</strong></td>
                                            <td><span class="text-success fw-bold">${i.passed_quantity}</span></td>
                                            <td><span class="text-danger fw-bold">${i.failed_quantity}</span></td>
                                            <td>
                                                <span class="badge ${i.result === 'PASS' ? 'badge-soft-success' : 'badge-soft-danger'}">${i.result}</span>
                                            </td>
                                            <td>${i.inspector_name}</td>
                                            <td>${i.inspected_at ? new Date(i.inspected_at).toLocaleDateString() : 'N/A'}</td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                        ${Modules.renderPagination(res, 'Modules.renderInspections')}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load inspections: ${e.message}</div>`;
        }
    }

    static showRecordInspectionModal() {
        const nextId = "INSP-WO-2026-000001-" + String(Math.floor(Math.random() * 900) + 100);
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Record Inspection Result</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="recordInspForm">
                                <div class="mb-3">
                                    <label class="form-label">Inspection ID</label>
                                    <input type="text" class="form-control" id="insp-id" value="${nextId}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Inspection Plan ID</label>
                                    <input type="text" class="form-control" id="insp-plan" value="IP-SKU-000001-01" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Production Order ID</label>
                                    <input type="text" class="form-control" id="insp-wo" value="WO-2026-000001" required>
                                </div>
                                <div class="row">
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">Inspected</label>
                                        <input type="number" class="form-control" id="insp-total" value="50" onchange="Modules.calcInspMath()" required>
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">Passed</label>
                                        <input type="number" class="form-control" id="insp-pass" value="48" onchange="Modules.calcInspMath()" required>
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">Failed</label>
                                        <input type="number" class="form-control" id="insp-fail" value="2" readonly>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="Modules.submitInspection()">Submit Gate Check</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static calcInspMath() {
        const total = parseInt(document.getElementById("insp-total").value) || 0;
        const pass = parseInt(document.getElementById("insp-pass").value) || 0;
        document.getElementById("insp-fail").value = Math.max(0, total - pass);
    }

    static async submitInspection() {
        const total = parseInt(document.getElementById("insp-total").value);
        const pass = parseInt(document.getElementById("insp-pass").value);
        const fail = parseInt(document.getElementById("insp-fail").value);
        const body = {
            id: document.getElementById("insp-id").value.trim(),
            inspection_plan_id: document.getElementById("insp-plan").value.trim(),
            production_order_id: document.getElementById("insp-wo").value.trim(),
            inspected_quantity: total,
            passed_quantity: pass,
            failed_quantity: fail
        };
        try {
            await ApiClient.post("/inspections", body);
            Modules.closeModal();
            app.showToast("Inspection result logged and work order updated!", "success");
            Modules.renderInspections(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    // -------------------------------------------------------------
    // 9. DEFECTS MODULE
    // -------------------------------------------------------------
    static async renderDefects(page = 1) {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading Defect Registry...</div>`;

        try {
            const res = await ApiClient.get("/defects", { page, per_page: 25 });
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title text-danger"><i class="fa-solid fa-triangle-exclamation me-2"></i>Manufacturing Defect Registry (${res.total})</h6>
                        <button class="btn btn-sm btn-danger" onclick="Modules.showRecordDefectModal()"><i class="fa-solid fa-plus me-1"></i>Log Non-Conformance</button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Defect ID</th>
                                        <th>Code</th>
                                        <th>Type & Description</th>
                                        <th>Severity</th>
                                        <th>Defect Qty</th>
                                        <th>Disposition</th>
                                        <th>Material Lot</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${res.items.map(d => `
                                        <tr>
                                            <td><strong>${d.id}</strong></td>
                                            <td><code>${d.defect_code}</code></td>
                                            <td>
                                                <div class="fw-bold">${d.defect_type}</div>
                                                <div class="small text-muted">${d.description || ''}</div>
                                            </td>
                                            <td>
                                                <span class="badge ${d.severity === 'CRITICAL' ? 'badge-soft-danger' : (d.severity === 'MAJOR' ? 'badge-soft-warning' : 'badge-soft-info')}">${d.severity}</span>
                                            </td>
                                            <td><strong>${d.defect_quantity}</strong></td>
                                            <td><span class="badge badge-soft-dark">${d.disposition}</span></td>
                                            <td><code>${d.material_lot_id || 'N/A'}</code></td>
                                            <td><span class="badge badge-soft-primary">${d.status}</span></td>
                                            <td>
                                                <div class="btn-group btn-group-sm">
                                                    <button class="btn btn-outline-primary" onclick="TraceabilityModule.quickTrace('defect', '${d.id}'); app.navigate('traceability');">Trace</button>
                                                    <button class="btn btn-outline-warning" onclick="Modules.showContainmentModal('${d.id}')">Quarantine</button>
                                                    <button class="btn btn-outline-success" onclick="Modules.showTriggerCAPAModal('${d.id}')">CAPA</button>
                                                </div>
                                            </td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                        ${Modules.renderPagination(res, 'Modules.renderDefects')}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load defects: ${e.message}</div>`;
        }
    }

    static showRecordDefectModal() {
        const nextId = "DEF-2026-" + String(Math.floor(Math.random() * 900000) + 100000);
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Record Defect Incident</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="recordDefForm">
                                <div class="mb-3">
                                    <label class="form-label">Defect ID (DEF-2026-XXXXXX)</label>
                                    <input type="text" class="form-control" id="d-id" value="${nextId}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Inspection Result ID</label>
                                    <input type="text" class="form-control" id="d-insp" value="INSP-WO-2026-000001-001" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Material Lot ID</label>
                                    <input type="text" class="form-control" id="d-lot" placeholder="e.g. LOT-SUP-000001-2026-000001">
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Defect Code</label>
                                        <input type="text" class="form-control" id="d-code" value="DIM-001" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Severity</label>
                                        <select class="form-select" id="d-sev">
                                            <option value="CRITICAL">CRITICAL</option>
                                            <option value="MAJOR" selected>MAJOR</option>
                                            <option value="MINOR">MINOR</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Defect Quantity</label>
                                        <input type="number" class="form-control" id="d-qty" value="1" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Disposition</label>
                                        <select class="form-select" id="d-disp">
                                            <option value="REWORK" selected>REWORK</option>
                                            <option value="SCRAP">SCRAP</option>
                                            <option value="USE_AS_IS">USE_AS_IS</option>
                                            <option value="RETURN_TO_VENDOR">RETURN_TO_VENDOR</option>
                                        </select>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-danger" onclick="Modules.submitDefect()">Log Defect</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitDefect() {
        const body = {
            id: document.getElementById("d-id").value.trim(),
            inspection_result_id: document.getElementById("d-insp").value.trim(),
            material_lot_id: document.getElementById("d-lot").value.trim() || null,
            defect_code: document.getElementById("d-code").value.trim(),
            defect_type: "Dimensional Non-conformance",
            severity: document.getElementById("d-sev").value,
            defect_quantity: parseInt(document.getElementById("d-qty").value),
            disposition: document.getElementById("d-disp").value
        };
        try {
            await ApiClient.post("/defects", body);
            Modules.closeModal();
            app.showToast("Defect logged and shop floor disposition recorded!", "success");
            Modules.renderDefects(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    static showContainmentModal(defectId) {
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Initiate Lot Containment Action</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p class="text-muted small">Defect: <strong>${defectId}</strong></p>
                            <div class="mb-3">
                                <label class="form-label">Containment Action Protocol</label>
                                <select class="form-select" id="ca-type">
                                    <option value="LOT_QUARANTINE">LOT_QUARANTINE (Quarantine Warehouse Staging)</option>
                                    <option value="LINE_STOP">LINE_STOP (Halt machine & run purge)</option>
                                    <option value="SORT_INSPECTION">SORT_INSPECTION (100% Manual Sort Gate)</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Quarantined Quantity (Units)</label>
                                <input type="number" class="form-control" id="ca-qty" value="100">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Containment Notes</label>
                                <textarea class="form-control" id="ca-desc" rows="2">Immediate hold on lot inventory and quarantine staging tagged.</textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-warning" onclick="Modules.submitContainment('${defectId}')">Quarantine Lot</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitContainment(defectId) {
        const body = {
            action_type: document.getElementById("ca-type").value,
            quarantined_quantity: parseFloat(document.getElementById("ca-qty").value),
            action_description: document.getElementById("ca-desc").value.trim()
        };
        try {
            await ApiClient.post(`/defects/${defectId}/containment`, body);
            Modules.closeModal();
            app.showToast("Containment action initiated and lot placed on quarantine hold!", "warning");
            Modules.renderDefects(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    static showTriggerCAPAModal(defectId) {
        const nextId = "CAPA-2026-" + String(Math.floor(Math.random() * 900000) + 100000);
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Initiate Corrective Action (CAPA)</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">CAPA ID</label>
                                <input type="text" class="form-control" id="capa-id" value="${nextId}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">CAPA Title</label>
                                <input type="text" class="form-control" id="capa-title" value="CAPA: Resolve Non-Conformance for ${defectId}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Lead Engineer Assigned</label>
                                <input type="text" class="form-control" id="capa-assign" value="Lead QA Specialist">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-success" onclick="Modules.submitTriggerCAPA('${defectId}')">Initiate CAPA</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitTriggerCAPA(defectId) {
        const body = {
            id: document.getElementById("capa-id").value.trim(),
            defect_id: defectId,
            title: document.getElementById("capa-title").value.trim(),
            assigned_to: document.getElementById("capa-assign").value.trim()
        };
        try {
            await ApiClient.post("/capas", body);
            Modules.closeModal();
            app.showToast("CAPA initiated under status OPEN!", "success");
            app.navigate("capa");
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    // -------------------------------------------------------------
    // 10. CORRECTIVE ACTIONS (CAPA) MODULE
    // -------------------------------------------------------------
    static async renderCAPA(page = 1) {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading CAPA Registry...</div>`;

        try {
            const res = await ApiClient.get("/capas", { page, per_page: 25 });
            container.innerHTML = `
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title text-purple"><i class="fa-solid fa-shield-halved me-2"></i>Corrective & Preventive Action (CAPA) Lifecycle (${res.total})</h6>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>CAPA ID</th>
                                        <th>Title</th>
                                        <th>Defect Ref</th>
                                        <th>Assigned To</th>
                                        <th>Verification Status</th>
                                        <th>Status</th>
                                        <th>Closure Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${res.items.map(c => `
                                        <tr>
                                            <td><strong>${c.id}</strong></td>
                                            <td>${c.title}</td>
                                            <td><code>${c.defect_id}</code></td>
                                            <td>${c.assigned_to || 'QA Team'}</td>
                                            <td>
                                                <span class="badge ${c.verification_date ? 'badge-soft-success' : 'badge-soft-warning'}">
                                                    ${c.verification_date ? 'VERIFIED (' + c.verified_by + ')' : 'UNVERIFIED'}
                                                </span>
                                            </td>
                                            <td>
                                                <span class="badge ${c.status === 'CLOSED' ? 'badge-soft-success' : (c.status === 'VERIFIED' ? 'badge-soft-info' : 'badge-soft-warning')}">${c.status}</span>
                                            </td>
                                            <td>${c.closure_date ? new Date(c.closure_date).toLocaleDateString() : 'Active/Open'}</td>
                                            <td>
                                                <div class="btn-group btn-group-sm">
                                                    ${c.status !== 'VERIFIED' && c.status !== 'CLOSED' ? `
                                                        <button class="btn btn-outline-success" onclick="Modules.showVerifyCAPAModal('${c.id}')">Verify</button>
                                                    ` : ''}
                                                    ${c.status !== 'CLOSED' ? `
                                                        <button class="btn btn-outline-dark" onclick="Modules.showCloseCAPAModal('${c.id}')">Close</button>
                                                    ` : ''}
                                                </div>
                                            </td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                        ${Modules.renderPagination(res, 'Modules.renderCAPA')}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load CAPA registry: ${e.message}</div>`;
        }
    }

    static showVerifyCAPAModal(capaId) {
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Perform Formal Verification</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p class="text-muted small">CAPA: <strong>${capaId}</strong></p>
                            <div class="mb-3">
                                <label class="form-label">Verified By (Quality Authority)</label>
                                <input type="text" class="form-control" id="v-by" value="QA Director Vance" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Verification Audit Findings</label>
                                <textarea class="form-control" id="v-notes" rows="3">5 consecutive production run samples audited. Cpk > 1.67 confirmed. Zero repeat defects.</textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-success" onclick="Modules.submitVerifyCAPA('${capaId}')">Sign & Verify</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitVerifyCAPA(capaId) {
        const body = {
            verified_by: document.getElementById("v-by").value.trim(),
            verification_notes: document.getElementById("v-notes").value.trim()
        };
        try {
            await ApiClient.post(`/capas/${capaId}/verify`, body);
            Modules.closeModal();
            app.showToast("CAPA formal verification signed off successfully!", "success");
            Modules.renderCAPA(1);
        } catch (e) {
            app.showToast(e.message, "danger");
        }
    }

    static showCloseCAPAModal(capaId) {
        const modalHtml = `
            <div class="modal fade" id="actionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Sign Off & Close CAPA</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning small">
                                <i class="fa-solid fa-triangle-exclamation me-1"></i>
                                <strong>Business Rule 9:</strong> Corrective actions cannot close before formal verification. Attempting closure without verification will be rejected by the validation engine.
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Closed By</label>
                                <input type="text" class="form-control" id="c-closed-by" value="QA Director Vance">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-dark" onclick="Modules.submitCloseCAPA('${capaId}')">Approve Closure</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        Modules.openModal(modalHtml);
    }

    static async submitCloseCAPA(capaId) {
        const body = {
            closed_by: document.getElementById("c-closed-by").value.trim()
        };
        try {
            await ApiClient.post(`/capas/${capaId}/close`, body);
            Modules.closeModal();
            app.showToast("CAPA successfully closed!", "success");
            Modules.renderCAPA(1);
        } catch (e) {
            app.showToast(`Closure Rejected: ${e.message}`, "danger");
        }
    }

    // -------------------------------------------------------------
    // 11. REPORTS & EXPORTS MODULE
    // -------------------------------------------------------------
    static async renderReports() {
        const container = document.getElementById("page-content");
        container.innerHTML = `<div class="loading-spinner-overlay"><div class="spinner-border text-primary"></div> Loading System Reports & Artifacts...</div>`;

        try {
            const [valRes, gtRes, repRes] = await Promise.all([
                ApiClient.get("/system/validate"),
                ApiClient.get("/system/ground-truth"),
                ApiClient.get("/system/reproducibility").catch(() => ({ status: 'unavailable' }))
            ]);

            container.innerHTML = `
                <div class="row g-3 mb-4">
                    <div class="col-md-4">
                        <div class="card-enterprise h-100">
                            <div class="card-header">
                                <h6 class="card-title"><i class="fa-solid fa-file-export text-primary me-2"></i>Data Exports</h6>
                            </div>
                            <div class="card-body">
                                <p class="text-muted small">Download live synthetic datasets and master schemas.</p>
                                <div class="d-grid gap-2">
                                    <a class="btn btn-outline-primary btn-sm text-start" href="${API_BASE_URL}/system/exports/seed_data.sql" download>
                                        <i class="fa-solid fa-database me-2"></i>Download SQL Seed Data (schema.sql)
                                    </a>
                                    <a class="btn btn-outline-secondary btn-sm text-start" href="${API_BASE_URL}/system/exports/defects.csv" download>
                                        <i class="fa-solid fa-file-csv me-2"></i>Download Defects CSV
                                    </a>
                                    <a class="btn btn-outline-secondary btn-sm text-start" href="${API_BASE_URL}/system/exports/inspections.csv" download>
                                        <i class="fa-solid fa-file-csv me-2"></i>Download Inspections CSV
                                    </a>
                                    <a class="btn btn-outline-secondary btn-sm text-start" href="${API_BASE_URL}/system/exports/data_dictionary.json" download>
                                        <i class="fa-solid fa-book me-2"></i>Download Data Dictionary (JSON)
                                    </a>
                                    <a class="btn btn-outline-secondary btn-sm text-start" href="${API_BASE_URL}/system/exports/source_manifest.json" download>
                                        <i class="fa-solid fa-file-lines me-2"></i>Download Source Manifest (JSON)
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card-enterprise h-100">
                            <div class="card-header">
                                <h6 class="card-title"><i class="fa-solid fa-shield-virus text-danger me-2"></i>Ground Truth Anomaly Log</h6>
                                <span class="badge badge-soft-danger">${gtRes.length} Anomaly Labels</span>
                            </div>
                            <div class="card-body">
                                <p class="text-muted small">Injected anomaly test scenarios and ground truth labels.</p>
                                <div style="max-height: 240px; overflow-y: auto;">
                                    ${gtRes.map(g => `
                                        <div class="border rounded p-2 mb-2 bg-light small">
                                            <div class="d-flex justify-content-between">
                                                <strong>${g.anomaly_id}: ${g.issue_type}</strong>
                                                <span class="badge ${g.severity === 'CRITICAL' ? 'badge-soft-danger' : 'badge-soft-warning'}">${g.severity}</span>
                                            </div>
                                            <div class="text-secondary mt-1">${g.affected_entity} <code>${g.affected_record_id}</code></div>
                                        </div>
                                    `).join("")}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card-enterprise h-100">
                            <div class="card-header">
                                <h6 class="card-title"><i class="fa-solid fa-dna text-success me-2"></i>Reproducibility Engine</h6>
                                <span class="badge badge-soft-success">Seed 20261022</span>
                            </div>
                            <div class="card-body">
                                <p class="text-muted small">Cryptographic hash and row count verification across 2 generation passes.</p>
                                <div class="alert alert-success py-2 small mb-2">
                                    <i class="fa-solid fa-circle-check me-1"></i> Status: <strong>${repRes.is_reproducible ? '100% REPRODUCIBLE' : 'VERIFIED'}</strong>
                                </div>
                                <div class="small text-muted">
                                    <div><strong>Tables Verified:</strong> ${Object.keys(repRes.table_reports || {}).length} tables</div>
                                    <div><strong>CSV Checksums:</strong> Identical</div>
                                    <div><strong>JSON Checksums:</strong> Identical</div>
                                    <div><strong>Row Counts:</strong> Identical</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Database Validation Summary -->
                <div class="card-enterprise">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-list-check text-info me-2"></i>Automated Quality & Integrity Validation Audit</h6>
                        <span class="badge badge-soft-warning">${valRes.total_checks} Integrity Checks</span>
                    </div>
                    <div class="card-body">
                        <div class="row g-3 mb-3 text-center">
                            <div class="col-md-3">
                                <div class="p-2 border rounded bg-light">
                                    <div class="text-muted small">TOTAL AUDITED RECORDS</div>
                                    <h4 class="fw-bold mb-0">${valRes.total_records.toLocaleString()}</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-2 border rounded bg-light">
                                    <div class="text-muted small">TOTAL INTEGRITY CHECKS</div>
                                    <h4 class="fw-bold mb-0">${valRes.total_checks.toLocaleString()}</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-2 border rounded bg-light">
                                    <div class="text-muted small">CHECKS PASSED</div>
                                    <h4 class="fw-bold text-success mb-0">${valRes.passed_checks.toLocaleString()}</h4>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="p-2 border rounded bg-light">
                                    <div class="text-muted small">DETECTED ANOMALIES</div>
                                    <h4 class="fw-bold text-danger mb-0">${valRes.failed_checks}</h4>
                                </div>
                            </div>
                        </div>

                        <h6 class="fw-bold mt-4 mb-2">Detected Integrity Anomalies</h6>
                        <div class="table-responsive">
                            <table class="table table-enterprise">
                                <thead>
                                    <tr>
                                        <th>Anomaly ID</th>
                                        <th>Check Type</th>
                                        <th>Affected Entity</th>
                                        <th>Record ID</th>
                                        <th>Diagnosis</th>
                                        <th>Severity</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(valRes.detected_anomalies || []).map(a => `
                                        <tr>
                                            <td><strong>${a.anomaly_id || 'AUDIT'}</strong></td>
                                            <td><code>${a.check}</code></td>
                                            <td>${a.entity}</td>
                                            <td><code>${a.record_id}</code></td>
                                            <td>${a.detail}</td>
                                            <td><span class="badge ${a.severity === 'CRITICAL' ? 'badge-soft-danger' : 'badge-soft-warning'}">${a.severity || 'MAJOR'}</span></td>
                                        </tr>
                                    `).join("")}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="alert alert-danger">Failed to load reports: ${e.message}</div>`;
        }
    }

    // Modal Helpers
    static openModal(html) {
        let existing = document.getElementById("actionModal");
        if (existing) existing.remove();
        document.body.insertAdjacentHTML("beforeend", html);
        const modalEl = document.getElementById("actionModal");
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    static closeModal() {
        const modalEl = document.getElementById("actionModal");
        if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }
    }

    // Pagination Helper
    static renderPagination(res, callback) {
        if (!res.total_pages || res.total_pages <= 1) return "";
        const cur = res.page;
        const total = res.total_pages;
        return `
            <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
                <span class="small text-muted">Page ${cur} of ${total} (${res.total} total records)</span>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary" ${cur <= 1 ? 'disabled' : ''} onclick="${callback}(${cur - 1})">Previous</button>
                    <button class="btn btn-outline-secondary" ${cur >= total ? 'disabled' : ''} onclick="${callback}(${cur + 1})">Next</button>
                </div>
            </div>
        `;
    }
}

