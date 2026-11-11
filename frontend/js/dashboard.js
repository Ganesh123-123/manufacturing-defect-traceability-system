/**
 * Dashboard & Analytics Module
 */
class DashboardModule {
    static chartInstances = {};

    static async init() {
        const container = document.getElementById("page-content");
        container.innerHTML = `
            <div class="row g-3 mb-4" id="kpi-row">
                <div class="col-12 text-center py-4"><div class="spinner-border text-primary" role="status"></div> Loading Live Manufacturing KPIs...</div>
            </div>

            <!-- Charts Row 1: Trends & Distribution -->
            <div class="row g-3 mb-4">
                <div class="col-lg-8">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title"><i class="fa-solid fa-chart-line text-primary me-2"></i>Monthly Defect, Scrap & Rework Trends</h6>
                            <span class="badge badge-soft-primary">Live Database Audit</span>
                        </div>
                        <div class="card-body">
                            <canvas id="monthlyTrendChart" height="120"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title"><i class="fa-solid fa-chart-pie text-warning me-2"></i>Rework vs Scrap Volume</h6>
                        </div>
                        <div class="card-body d-flex flex-column align-items-center justify-content-center">
                            <div style="width: 220px; height: 220px;">
                                <canvas id="reworkScrapChart"></canvas>
                            </div>
                            <div class="mt-3 text-center" id="rework-scrap-legend"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row 2: Supplier & Machine Analysis -->
            <div class="row g-3 mb-4">
                <div class="col-lg-6">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title"><i class="fa-solid fa-truck-field text-info me-2"></i>Top Defective Suppliers</h6>
                        </div>
                        <div class="card-body">
                            <canvas id="supplierDefectChart" height="140"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title"><i class="fa-solid fa-gears text-purple me-2"></i>Machine Defect & Scrap Analysis</h6>
                        </div>
                        <div class="card-body">
                            <canvas id="machineDefectChart" height="140"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row 3: Product Defect Rates & CAPA Status -->
            <div class="row g-3">
                <div class="col-lg-6">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title"><i class="fa-solid fa-microchip text-danger me-2"></i>Highest Defect Rate Products (%)</h6>
                        </div>
                        <div class="card-body">
                            <canvas id="productRateChart" height="140"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title"><i class="fa-solid fa-check-double text-success me-2"></i>Inspection Pass/Fail</h6>
                        </div>
                        <div class="card-body d-flex flex-column align-items-center justify-content-center">
                            <div style="width: 180px; height: 180px;">
                                <canvas id="passFailChart"></canvas>
                            </div>
                            <div class="mt-3 text-center" id="pass-fail-legend"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title"><i class="fa-solid fa-clipboard-check text-primary me-2"></i>CAPA Status Distribution</h6>
                        </div>
                        <div class="card-body d-flex flex-column align-items-center justify-content-center">
                            <div style="width: 180px; height: 180px;">
                                <canvas id="capaStatusChart"></canvas>
                            </div>
                            <div class="mt-3 text-center" id="capa-status-legend"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await this.loadKPIs();
        await this.loadCharts();
    }

    static async loadKPIs() {
        try {
            const kpis = await ApiClient.get("/analytics/dashboard");
            const kpiRow = document.getElementById("kpi-row");
            kpiRow.innerHTML = `
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Total Products</h6>
                            <p class="kpi-value">${Number(kpis.total_products).toLocaleString()}</p>
                            <span class="kpi-sub">Active SKUs</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-blue"><i class="fa-solid fa-boxes-stacked"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Suppliers</h6>
                            <p class="kpi-value">${Number(kpis.total_suppliers).toLocaleString()}</p>
                            <span class="kpi-sub">Approved Vendors</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-cyan"><i class="fa-solid fa-truck"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Material Lots</h6>
                            <p class="kpi-value">${Number(kpis.total_material_lots).toLocaleString()}</p>
                            <span class="kpi-sub">Pedigree Batches</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-purple"><i class="fa-solid fa-layer-group"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Work Orders</h6>
                            <p class="kpi-value">${Number(kpis.total_production_orders).toLocaleString()}</p>
                            <span class="kpi-sub">Shop Floor Batches</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-blue"><i class="fa-solid fa-industry"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Inspections</h6>
                            <p class="kpi-value">${Number(kpis.total_inspections).toLocaleString()}</p>
                            <span class="kpi-sub">${Number(kpis.total_inspected_units || 0).toLocaleString()} units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-green"><i class="fa-solid fa-clipboard-check"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Total Defects</h6>
                            <p class="kpi-value text-danger">${Number(kpis.total_defects).toLocaleString()}</p>
                            <span class="kpi-sub">${Number(kpis.total_defective_units || 0).toLocaleString()} units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-red"><i class="fa-solid fa-triangle-exclamation"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Defect Rate</h6>
                            <p class="kpi-value ${kpis.defect_rate > 5 ? 'text-danger' : 'text-primary'}">${kpis.defect_rate}%</p>
                            <span class="kpi-sub">Defective / Inspected Units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-amber"><i class="fa-solid fa-percent"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Rework Quantity</h6>
                            <p class="kpi-value text-warning">${Number(kpis.rework_quantity).toLocaleString()}</p>
                            <span class="kpi-sub">Salvageable units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-amber"><i class="fa-solid fa-wrench"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Scrap Quantity</h6>
                            <p class="kpi-value text-danger">${Number(kpis.scrap_quantity).toLocaleString()}</p>
                            <span class="kpi-sub">Disposed scrap units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-red"><i class="fa-solid fa-trash-can"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Open CAPAs</h6>
                            <p class="kpi-value text-purple">${Number(kpis.open_corrective_actions).toLocaleString()}</p>
                            <span class="kpi-sub">Under active mitigation</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-purple"><i class="fa-solid fa-shield-halved"></i></div>
                    </div>
                </div>
            `;
        } catch (e) {
            document.getElementById("kpi-row").innerHTML = `
                <div class="col-12"><div class="alert alert-danger"><i class="fa-solid fa-circle-exclamation me-2"></i>Failed to fetch live KPIs: ${e.message}</div></div>
            `;
        }
    }

    static async loadCharts() {
        // Clear previous chart instances
        Object.values(this.chartInstances).forEach(c => c.destroy());
        this.chartInstances = {};

        try {
            // 1. Monthly Trends
            const trends = await ApiClient.get("/analytics/monthly-trends");
            const ctxTrends = document.getElementById("monthlyTrendChart").getContext("2d");
            this.chartInstances.trends = new Chart(ctxTrends, {
                type: "line",
                data: {
                    labels: trends.map(t => t.month),
                    datasets: [
                        {
                            label: "Total Defects",
                            data: trends.map(t => t.defect_count),
                            borderColor: "#ef4444",
                            backgroundColor: "rgba(239, 68, 68, 0.1)",
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: "Rework Qty",
                            data: trends.map(t => t.rework_quantity),
                            borderColor: "#f59e0b",
                            backgroundColor: "rgba(245, 158, 11, 0.05)",
                            tension: 0.3
                        },
                        {
                            label: "Scrap Qty",
                            data: trends.map(t => t.scrap_quantity),
                            borderColor: "#dc2626",
                            borderDash: [5, 5],
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "top" } }
                }
            });

            // 2. Rework vs Scrap
            const rws = await ApiClient.get("/analytics/rework-vs-scrap");
            const ctxRws = document.getElementById("reworkScrapChart").getContext("2d");
            this.chartInstances.rws = new Chart(ctxRws, {
                type: "doughnut",
                data: {
                    labels: ["Rework", "Scrap"],
                    datasets: [{
                        data: [rws.rework, rws.scrap],
                        backgroundColor: ["#f59e0b", "#ef4444"]
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
            document.getElementById("rework-scrap-legend").innerHTML = `
                <span class="badge badge-soft-warning me-2">Rework: ${rws.rework.toLocaleString()} (${rws.rework_percentage}%)</span>
                <span class="badge badge-soft-danger">Scrap: ${rws.scrap.toLocaleString()} (${rws.scrap_percentage}%)</span>
            `;

            // 3. Supplier Defect Analysis
            const suppliers = await ApiClient.get("/analytics/suppliers");
            const ctxSup = document.getElementById("supplierDefectChart").getContext("2d");
            this.chartInstances.suppliers = new Chart(ctxSup, {
                type: "bar",
                data: {
                    labels: suppliers.map(s => s.supplier_name.substring(0, 15) + ".."),
                    datasets: [{
                        label: "Defects Count",
                        data: suppliers.map(s => s.defect_count),
                        backgroundColor: "#0ea5e9"
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

            // 4. Machine Defect Analysis
            const machines = await ApiClient.get("/analytics/machines");
            const ctxMac = document.getElementById("machineDefectChart").getContext("2d");
            this.chartInstances.machines = new Chart(ctxMac, {
                type: "bar",
                data: {
                    labels: machines.map(m => m.machine_name),
                    datasets: [
                        { label: "Rework", data: machines.map(m => m.rework_quantity), backgroundColor: "#f59e0b" },
                        { label: "Scrap", data: machines.map(m => m.scrap_quantity), backgroundColor: "#ef4444" }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true }, y: { stacked: true } } }
            });

            // 5. Product Defect Rates
            const products = await ApiClient.get("/analytics/products");
            const ctxProd = document.getElementById("productRateChart").getContext("2d");
            this.chartInstances.products = new Chart(ctxProd, {
                type: "bar",
                data: {
                    labels: products.map(p => p.product_sku),
                    datasets: [{
                        label: "Defect Rate (%)",
                        data: products.map(p => p.defect_rate),
                        backgroundColor: "#8b5cf6"
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

            // 6. Inspection Pass/Fail
            const passFail = await ApiClient.get("/analytics/pass-fail");
            const ctxPf = document.getElementById("passFailChart").getContext("2d");
            this.chartInstances.passFail = new Chart(ctxPf, {
                type: "pie",
                data: {
                    labels: ["Passed", "Failed"],
                    datasets: [{
                        data: [passFail.passed_quantity, passFail.failed_quantity],
                        backgroundColor: ["#10b981", "#ef4444"]
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
            document.getElementById("pass-fail-legend").innerHTML = `
                <span class="badge badge-soft-success me-2">Pass: ${passFail.pass_rate}%</span>
                <span class="badge badge-soft-danger">Fail: ${passFail.fail_rate}%</span>
            `;

            // 7. CAPA Status Distribution
            const capaDist = await ApiClient.get("/analytics/capa-distribution");
            const ctxCapa = document.getElementById("capaStatusChart").getContext("2d");
            this.chartInstances.capa = new Chart(ctxCapa, {
                type: "doughnut",
                data: {
                    labels: Object.keys(capaDist),
                    datasets: [{
                        data: Object.values(capaDist),
                        backgroundColor: ["#3b82f6", "#f59e0b", "#ec4899", "#8b5cf6", "#10b981", "#64748b"]
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
            document.getElementById("capa-status-legend").innerHTML = `
                <span class="badge badge-soft-primary me-1">Open: ${capaDist.OPEN || 0}</span>
                <span class="badge badge-soft-warning me-1">In Prog: ${capaDist.IN_PROGRESS || 0}</span>
                <span class="badge badge-soft-success">Verified: ${capaDist.VERIFIED || 0}</span>
            `;

        } catch (e) {
            console.error("Failed to render dashboard charts:", e);
        }
    }
}
