/**
 * Traceability Module - Multi-Tier Visualizer
 */
class TraceabilityModule {
    static async init(defaultType = "defect", defaultId = "DEF-2026-000001") {
        const container = document.getElementById("page-content");
        container.innerHTML = `
            <div class="card-enterprise mb-4">
                <div class="card-body">
                    <div class="row align-items-center g-3">
                        <div class="col-md-3">
                            <label class="form-label fw-bold text-muted small">TRACE LEVEL</label>
                            <select id="trace-type-select" class="form-select">
                                <option value="defect" selected>Defect ID (DEF-XXXXXX)</option>
                                <option value="product">Product SKU (SKU-XXXXXX)</option>
                                <option value="order">Production Order (WO-XXXXXX)</option>
                                <option value="lot">Material Lot (LOT-XXXXXX)</option>
                                <option value="supplier">Supplier ID (SUP-XXXXXX)</option>
                                <option value="machine">Machine ID (MAC-XXX)</option>
                            </select>
                        </div>
                        <div class="col-md-5">
                            <label class="form-label fw-bold text-muted small">IDENTIFIER</label>
                            <div class="input-group">
                                <input type="text" id="trace-id-input" class="form-control" placeholder="Enter ID to trace..." value="${defaultId}">
                                <button class="btn btn-primary px-4" id="btn-trace-search"><i class="fa-solid fa-magnifying-glass me-2"></i>Trace Chain</button>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-bold text-muted small">QUICK SAMPLE QUERIES</label>
                            <div class="d-flex flex-wrap gap-1">
                                <button class="btn btn-sm btn-outline-secondary py-1" onclick="TraceabilityModule.quickTrace('defect', 'DEF-2026-000001')">Valid Defect</button>
                                <button class="btn btn-sm btn-outline-danger py-1" onclick="TraceabilityModule.quickTrace('defect', 'DEF-2026-001594')">Scenario 1 (Broken Lot)</button>
                                <button class="btn btn-sm btn-outline-danger py-1" onclick="TraceabilityModule.quickTrace('defect', 'DEF-2026-001593')">Scenario 5 (Broken WO)</button>
                                <button class="btn btn-sm btn-outline-info py-1" onclick="TraceabilityModule.quickTrace('order', 'WO-2026-000001')">WO-000001</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="trace-result-container">
                <div class="text-center py-5 text-muted">
                    <i class="fa-solid fa-diagram-project fa-3x mb-3 text-secondary"></i>
                    <p>Enter an identifier or click one of the quick samples above to visualize the complete manufacturing pedigree.</p>
                </div>
            </div>
        `;

        document.getElementById("btn-trace-search").addEventListener("click", () => {
            const type = document.getElementById("trace-type-select").value;
            const id = document.getElementById("trace-id-input").value.trim();
            if (id) {
                this.executeTrace(type, id);
            }
        });

        document.getElementById("trace-type-select").value = defaultType;
        if (defaultId) {
            this.executeTrace(defaultType, defaultId);
        }
    }

    static quickTrace(type, id) {
        document.getElementById("trace-type-select").value = type;
        document.getElementById("trace-id-input").value = id;
        this.executeTrace(type, id);
    }

    static async executeTrace(type, id) {
        const container = document.getElementById("trace-result-container");
        container.innerHTML = `
            <div class="loading-spinner-overlay">
                <div class="spinner-border text-primary" role="status"></div>
                <span>Auditing traceability relationships in MySQL database...</span>
            </div>
        `;

        try {
            const data = await ApiClient.get("/traceability", { type, id });
            if (type === "defect") {
                this.renderDefectChain(container, data);
            } else {
                this.renderEntityOverview(container, type, data);
            }
        } catch (error) {
            container.innerHTML = `
                <div class="alert alert-danger shadow-sm">
                    <div class="d-flex align-items-center gap-3">
                        <i class="fa-solid fa-triangle-exclamation fa-2x"></i>
                        <div>
                            <h5 class="alert-heading mb-1">Traceability Lookup Failed</h5>
                            <p class="mb-0">${error.message}</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    static renderDefectChain(container, data) {
        const nodes = data.nodes || {};
        const isBroken = data.status === "BROKEN_LINK";
        const brokenLinks = data.broken_links || [];

        let brokenBanner = "";
        if (isBroken) {
            brokenBanner = `
                <div class="alert alert-danger mb-4 shadow-sm">
                    <h6 class="fw-bold mb-2"><i class="fa-solid fa-link-slash me-2"></i>Traceability Anomaly Detected: Broken Relationship</h6>
                    <ul class="mb-0 ps-3">
                        ${brokenLinks.map(bl => `<li><strong>${bl.from} &rarr; ${bl.to}:</strong> ${bl.reason} (Reference ID: <code>${bl.reference_id}</code>)</li>`).join("")}
                    </ul>
                </div>
            `;
        }

        const product = nodes.product || {};
        const order = nodes.production_order || {};
        const lot = nodes.material_lot || {};
        const supplier = nodes.supplier || {};
        const machine = nodes.machine || {};
        const step = nodes.process_step || {};
        const insp = nodes.inspection_result || {};
        const defect = nodes.defect || {};
        const caList = nodes.containment_actions || [];
        const capaList = nodes.corrective_actions || [];
        const vStatus = nodes.verification_status || {};

        container.innerHTML = `
            ${brokenBanner}

            <div class="d-flex justify-content-between align-items-center mb-4">
                <h5 class="fw-bold m-0"><i class="fa-solid fa-sitemap text-primary me-2"></i>End-to-End Defect Pedigree Tree</h5>
                <span class="badge ${isBroken ? 'badge-soft-danger' : 'badge-soft-success'} px-3 py-2 fs-6">
                    <i class="fa-solid ${isBroken ? 'fa-triangle-exclamation' : 'fa-circle-check'} me-1"></i>
                    Status: ${data.status}
                </span>
            </div>

            <div class="trace-tree">

                <!-- 1. PRODUCT -->
                <div class="trace-node">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-box text-primary"></i> 1. Product (End Item)</div>
                        <span class="badge badge-soft-primary">${product.id || 'N/A'}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>Name:</strong> ${product.name || 'Unknown'}</div>
                        <div><strong>Category:</strong> ${product.category || 'N/A'}</div>
                        <div><strong>Cycle Time:</strong> ${product.target_cycle_time_mins || 0} mins</div>
                        <div><strong>Unit:</strong> ${product.unit_of_measure || 'PCS'}</div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 2. PRODUCTION ORDER -->
                <div class="trace-node ${brokenLinks.some(b => b.to === 'ProductionOrder') ? 'broken-node' : ''}">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-clipboard-list text-info"></i> 2. Production Order</div>
                        <span class="badge badge-soft-info">${order.id || defect.production_order_id}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>Batch:</strong> ${order.batch_number || 'N/A'}</div>
                        <div><strong>Status:</strong> <span class="badge badge-soft-dark">${order.status || 'MISSING'}</span></div>
                        <div><strong>Target Qty:</strong> ${order.target_quantity || 'N/A'}</div>
                        <div><strong>Completed / Scrap:</strong> ${order.completed_quantity || 0} / ${order.scrapped_quantity || 0}</div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 3. BOM & CONSUMPTION -->
                <div class="trace-node">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-cubes-stacked text-warning"></i> 3. BOM & Material Consumption</div>
                        <span class="badge badge-soft-warning">${(nodes.material_consumptions || []).length} Consumed Items</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>BOM Components:</strong> ${(nodes.boms || []).length} active items</div>
                        <div><strong>Consumptions:</strong> ${(nodes.material_consumptions || []).map(c => `${c.material_name || c.material_lot_id} (${c.consumed_quantity} ${c.unit_of_measure})`).join(', ') || 'None recorded'}</div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 4. MATERIAL LOT & SUPPLIER -->
                <div class="trace-node ${brokenLinks.some(b => b.to === 'MaterialLot') ? 'broken-node' : ''}">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-truck-ramp-box text-purple"></i> 4. Material Lot & Origin Supplier</div>
                        <span class="badge ${lot.id ? 'badge-soft-purple' : 'badge-soft-danger'}">${lot.id || defect.material_lot_id || 'NOT LINKED'}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>Material:</strong> ${lot.material_name || 'N/A'} (<code>${lot.material_sku || 'N/A'}</code>)</div>
                        <div><strong>Supplier:</strong> ${supplier.name || 'N/A'} (<code>${supplier.code || 'N/A'}</code>)</div>
                        <div><strong>Lot Status:</strong> <span class="badge badge-soft-warning">${lot.status || 'UNVERIFIED'}</span></div>
                        <div><strong>Received Date:</strong> ${lot.received_date ? new Date(lot.received_date).toLocaleDateString() : 'N/A'}</div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 5. PROCESS STEP & MACHINE -->
                <div class="trace-node">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-gear text-secondary"></i> 5. Process Step & Assigned Machine</div>
                        <span class="badge badge-soft-dark">${step.step_code || 'STEP'} &bull; ${machine.machine_code || 'MAC'}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>Process Step:</strong> ${step.name || 'Standard Step'}</div>
                        <div><strong>Machine:</strong> ${machine.name || 'Standard Cell'} (${machine.line || 'Line'})</div>
                        <div><strong>Machine Type:</strong> ${machine.type || 'N/A'}</div>
                        <div><strong>Machine Status:</strong> <span class="badge badge-soft-success">${machine.status || 'OPERATIONAL'}</span></div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 6. INSPECTION RESULT -->
                <div class="trace-node ${brokenLinks.some(b => b.to === 'InspectionResult') ? 'broken-node' : ''}">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-microscope text-success"></i> 6. Inspection Checkpoint</div>
                        <span class="badge badge-soft-success">${insp.id || 'N/A'}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>Result:</strong> <span class="badge ${insp.result === 'PASS' ? 'badge-soft-success' : 'badge-soft-danger'}">${insp.result || 'N/A'}</span></div>
                        <div><strong>Inspected / Failed:</strong> ${insp.inspected_quantity || 0} / ${insp.failed_quantity || 0}</div>
                        <div><strong>Inspector:</strong> ${insp.inspector_name || 'QC Inspector'}</div>
                        <div><strong>Timestamp:</strong> ${insp.inspected_at ? new Date(insp.inspected_at).toLocaleString() : 'N/A'}</div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 7. DEFECT INCIDENT -->
                <div class="trace-node border-danger" style="border-left-width: 6px;">
                    <div class="trace-node-header">
                        <div class="trace-node-title text-danger"><i class="fa-solid fa-triangle-exclamation"></i> 7. Defect Incident</div>
                        <span class="badge badge-soft-danger fs-6">${defect.id}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>Code & Type:</strong> <code>${defect.defect_code}</code> - ${defect.defect_type}</div>
                        <div><strong>Severity:</strong> <span class="badge ${defect.severity === 'CRITICAL' ? 'badge-soft-danger' : 'badge-soft-warning'}">${defect.severity}</span></div>
                        <div><strong>Defect Qty:</strong> ${defect.defect_quantity} units</div>
                        <div><strong>Disposition:</strong> <span class="badge badge-soft-dark">${defect.disposition}</span> (Rework: ${defect.rework_quantity}, Scrap: ${defect.scrap_quantity})</div>
                        <div><strong>Root Cause Cat:</strong> ${defect.root_cause_category}</div>
                        <div><strong>Lifecycle Status:</strong> <span class="badge badge-soft-info">${defect.status}</span></div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 8. CONTAINMENT ACTION -->
                <div class="trace-node">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-lock text-warning"></i> 8. Containment Action</div>
                        <span class="badge badge-soft-warning">${caList.length > 0 ? caList[0].action_type : 'NONE'}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>Action:</strong> ${caList.length > 0 ? caList[0].action_description : 'No containment required'}</div>
                        <div><strong>Quarantined Qty:</strong> ${caList.length > 0 ? caList[0].quarantined_quantity + ' units' : '0'}</div>
                        <div><strong>Status:</strong> ${caList.length > 0 ? caList[0].status : 'N/A'}</div>
                        <div><strong>Initiated:</strong> ${caList.length > 0 && caList[0].initiated_at ? new Date(caList[0].initiated_at).toLocaleDateString() : 'N/A'}</div>
                    </div>
                </div>

                <div class="trace-connector"></div>

                <!-- 9. CORRECTIVE ACTION & VERIFICATION -->
                <div class="trace-node ${vStatus.is_verified ? 'border-success' : 'border-warning'}" style="border-left-width: 6px;">
                    <div class="trace-node-header">
                        <div class="trace-node-title"><i class="fa-solid fa-shield-halved text-purple"></i> 9. Corrective Action & Verification</div>
                        <span class="badge badge-soft-purple">${vStatus.capa_id || (capaList.length > 0 ? capaList[0].id : 'NO CAPA')}</span>
                    </div>
                    <div class="trace-node-meta">
                        <div><strong>CAPA Status:</strong> <span class="badge ${vStatus.status === 'CLOSED' ? 'badge-soft-success' : 'badge-soft-warning'}">${vStatus.status || 'PENDING'}</span></div>
                        <div><strong>Formal Verification:</strong> <span class="badge ${vStatus.is_verified ? 'badge-soft-success' : 'badge-soft-danger'}">${vStatus.is_verified ? 'VERIFIED' : 'UNVERIFIED'}</span></div>
                        <div><strong>Verified By:</strong> ${vStatus.verified_by || 'Awaiting Verification'}</div>
                        <div><strong>Closure Date:</strong> ${vStatus.closure_date ? new Date(vStatus.closure_date).toLocaleDateString() : 'Active/Open'}</div>
                    </div>
                </div>

            </div>
        `;
    }

    static renderEntityOverview(container, type, data) {
        if (type === "machine") {
            const machine = data.machine;
            const inspections = data.inspections || [];
            const defects = data.defects || [];
            container.innerHTML = `
                <div class="card-enterprise mb-4">
                    <div class="card-header">
                        <h6 class="card-title"><i class="fa-solid fa-gears me-2 text-primary"></i>Machine History: ${machine.name}</h6>
                        <span class="badge badge-soft-primary">${machine.id}</span>
                    </div>
                    <div class="card-body">
                        <div class="row g-3 mb-4">
                            <div class="col-md-3"><strong>Line:</strong> ${machine.line}</div>
                            <div class="col-md-3"><strong>Location:</strong> ${machine.location || "N/A"}</div>
                            <div class="col-md-3"><strong>Status:</strong> ${machine.status}</div>
                            <div class="col-md-3"><strong>Inspections:</strong> ${data.inspections_count}</div>
                        </div>
                        <h6 class="fw-bold">Recent Inspection History (${inspections.length} of ${data.inspections_count})</h6>
                        ${inspections.length ? `
                            <div class="table-responsive mb-4">
                                <table class="table table-enterprise table-sm">
                                    <thead><tr><th>Date</th><th>Inspection</th><th>Work Order</th><th>Process Step</th><th>Result</th><th>Inspected</th><th>Passed</th><th>Failed</th></tr></thead>
                                    <tbody>${inspections.map(item => `
                                        <tr>
                                            <td>${item.inspected_at ? new Date(item.inspected_at).toLocaleString() : "N/A"}</td>
                                            <td>${item.id}</td>
                                            <td>${item.production_order_id}</td>
                                            <td>${item.step_name || item.step_id || "N/A"}</td>
                                            <td>${item.result}</td>
                                            <td>${item.inspected_quantity}</td>
                                            <td>${item.passed_quantity}</td>
                                            <td>${item.failed_quantity}</td>
                                        </tr>
                                    `).join("")}</tbody>
                                </table>
                            </div>
                        ` : `<p class="text-muted">No inspections recorded for this machine.</p>`}
                        <h6 class="fw-bold">Recent Defect History (${defects.length} of ${data.defects_count})</h6>
                        ${defects.length ? `
                            <div class="table-responsive">
                                <table class="table table-enterprise table-sm">
                                    <thead><tr><th>Date</th><th>Defect</th><th>Type</th><th>Work Order</th><th>Severity</th><th>Quantity</th><th>Status</th></tr></thead>
                                    <tbody>${defects.map(item => `
                                        <tr>
                                            <td>${item.detected_at ? new Date(item.detected_at).toLocaleString() : "N/A"}</td>
                                            <td>${item.id}</td>
                                            <td>${item.defect_type}</td>
                                            <td>${item.production_order_id}</td>
                                            <td>${item.severity}</td>
                                            <td>${item.defect_quantity}</td>
                                            <td>${item.status}</td>
                                        </tr>
                                    `).join("")}</tbody>
                                </table>
                            </div>
                        ` : `<p class="text-muted">No defects recorded for this machine.</p>`}
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="card-enterprise">
                <div class="card-header">
                    <h6 class="card-title text-capitalize"><i class="fa-solid fa-circle-nodes me-2 text-primary"></i>${type} Forward / Backward Pedigree</h6>
                    <span class="badge badge-soft-primary">${data.query_id}</span>
                </div>
                <div class="card-body">
                    <pre class="code-preview p-3 rounded text-light" style="max-height: 500px; overflow-y: auto;">${JSON.stringify(data, null, 2)}</pre>
                </div>
            </div>
        `;
    }
}
